"""
pynq_inference.py
=================
Phase 6: PYNQ-Z2 On-Board CNN Inference Driver
================================================
Runs approximate CNN inference on the physical PYNQ-Z2 FPGA board.

Hardware setup:
  - Load cnn_axm.bit + cnn_axm.hwh as a PYNQ Overlay
  - Stream quantized activation + weight data to CNN Accelerator via AXI DMA
  - Read output feature map from DMA
  - Dequantize and apply ReLU / MaxPool in Python
  - Measure real on-board latency, throughput, and accuracy

Run on PYNQ-Z2 board (Jupyter or SSH):
  python pynq_inference.py

Requirements on PYNQ board:
  pip install pynq numpy
"""

import numpy as np
import time
import os

# ── PYNQ imports (only available on the physical board) ──────
try:
    from pynq import Overlay, allocate
    from pynq.lib import dma
    ON_BOARD = True
except ImportError:
    ON_BOARD = False
    print("[WARNING] PYNQ library not found.")
    print("          Running in SIMULATION MODE (no hardware).")
    print("          Transfer this script to the PYNQ-Z2 board to run on hardware.\n")

# ────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────
OVERLAY_PATH = "/home/xilinx/cnn_axm.bit"   # path on PYNQ board
WEIGHT_NPY   = "weights_int8.npy"            # extracted layer weights
ACT_SCALE    = 1.0 / 255.0                   # activation dequantization scale
N_CLASSES    = 10

# Layer configuration (matching sensitivity-guided assignment)
# mode: 0=exact, 1=trunc, 2=comp, 3=orbased
LAYER_CONFIG = {
    "conv1": {"filters": 16, "cin":  1, "mode": 0},  # EXACT
    "conv2": {"filters": 32, "cin": 16, "mode": 2},  # COMPENSATED
    "conv3": {"filters": 64, "cin": 32, "mode": 2},  # COMPENSATED
    "conv4": {"filters": 64, "cin": 64, "mode": 1},  # TRUNCATED
}

# Fashion-MNIST class names
CLASS_NAMES = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]

# ────────────────────────────────────────────────────────────
# WEIGHT EXTRACTION UTILITY
# (Run this once on PC to create weights_int8.npy)
# ────────────────────────────────────────────────────────────
def extract_weights_from_keras(keras_model_path="baseline_cnn.keras",
                                output_path="weights_int8.npy"):
    """
    Loads the trained Keras model, extracts INT8 quantized weights
    and saves them as a numpy dict for use on the PYNQ board.
    Run on PC: python pynq_inference.py --extract-weights
    """
    import tensorflow as tf
    model = tf.keras.models.load_model(keras_model_path)

    weights_dict = {}
    layer_names = ["conv1","conv2","conv3","conv4","fc1","fc2"]

    for name in layer_names:
        layer = model.get_layer(name)
        W, b  = layer.get_weights()
        # INT8 quantization
        w_scale = np.max(np.abs(W)) / 255.0
        w_mag   = np.clip(np.round(np.abs(W) / w_scale), 0, 255).astype(np.uint8)
        w_sign  = (W < 0).astype(np.int8)
        weights_dict[f"{name}_mag"]   = w_mag
        weights_dict[f"{name}_sign"]  = w_sign
        weights_dict[f"{name}_scale"] = np.array([w_scale], dtype=np.float32)
        weights_dict[f"{name}_bias"]  = b.astype(np.float32)

    np.save(output_path, weights_dict, allow_pickle=True)
    print(f"Saved INT8 weights to: {output_path}")
    return weights_dict


# ────────────────────────────────────────────────────────────
# PYNQ HARDWARE OVERLAY CLASS
# ────────────────────────────────────────────────────────────
class CnnAxmOverlay:
    """
    Manages the PYNQ overlay for the CNN approximate multiplier accelerator.
    """

    def __init__(self, bitfile=OVERLAY_PATH):
        if not ON_BOARD:
            raise RuntimeError("PYNQ not available. Cannot load overlay.")

        print(f"Loading overlay: {bitfile}")
        self.ol  = Overlay(bitfile)
        self.dma = self.ol.axi_dma_0

        # AXI-Lite registers (layer_id and bias written by PS)
        self.axm_ip = self.ol.cnn_axm_0

        print("Overlay loaded. DMA ready.")
        print(f"  DMA send channel: {self.dma.sendchannel}")
        print(f"  DMA recv channel: {self.dma.recvchannel}")

    def run_conv_layer(self, act_map, weights_dict, layer_name, layer_id):
        """
        Runs one convolutional layer on the FPGA accelerator.
        act_map : numpy array (H, W, Cin) uint8 — quantized activations
        Returns : numpy array (H, W, Cout) float32 — dequantized outputs
        """
        cfg      = LAYER_CONFIG[layer_name]
        Cout     = cfg["filters"]
        Cin      = cfg["cin"]
        H, W, _  = act_map.shape
        KH = KW  = 3

        w_mag    = weights_dict[f"{layer_name}_mag"]    # (3,3,Cin,Cout)
        w_sign   = weights_dict[f"{layer_name}_sign"]   # (3,3,Cin,Cout)
        w_scale  = float(weights_dict[f"{layer_name}_scale"][0])
        bias     = weights_dict[f"{layer_name}_bias"]   # (Cout,)

        # Act scale (assume max activation = 255 for simplicity)
        act_scale = ACT_SCALE

        # Pad activations (same padding)
        pad   = KH // 2
        act_p = np.pad(act_map, ((pad,pad),(pad,pad),(0,0)))

        # Output buffer
        out = np.zeros((H, W, Cout), dtype=np.float32)

        # ── Stream data to FPGA per output pixel ───────────
        # Packet format per beat: [w_sign(1), w_mag(8), act(8)] = 17 bits
        # Packed into 32-bit word: [0..7]=act, [8..15]=w_mag, [16]=w_sign

        n_beats = KH * KW * Cin   # beats per output pixel

        for oc in range(Cout):
            # Write bias to AXI-Lite register (simplified)
            bias_int = int(bias[oc] / (act_scale * w_scale))

            for oh in range(H):
                for ow in range(W):
                    # Build input packet (n_beats × 32-bit words)
                    in_buf  = allocate(shape=(n_beats,), dtype=np.uint32)
                    out_buf = allocate(shape=(1,),       dtype=np.int32)

                    idx = 0
                    for kh in range(KH):
                        for kw in range(KW):
                            for ic in range(Cin):
                                ih = oh + kh
                                iw = ow + kw
                                act_val = int(act_p[ih, iw, ic])
                                wm      = int(w_mag[kh, kw, ic, oc])
                                ws      = int(w_sign[kh, kw, ic, oc])
                                in_buf[idx] = (act_val & 0xFF) | \
                                              ((wm & 0xFF) << 8) | \
                                              ((ws & 0x1) << 16)
                                idx += 1

                    # Mark last beat
                    in_buf[n_beats-1] |= (1 << 24)   # tlast bit

                    # DMA transfer
                    self.dma.sendchannel.transfer(in_buf)
                    self.dma.recvchannel.transfer(out_buf)
                    self.dma.sendchannel.wait()
                    self.dma.recvchannel.wait()

                    # Dequantize
                    raw = int(out_buf[0]) + bias_int
                    out[oh, ow, oc] = raw * act_scale * w_scale

                    in_buf.freebuffer()
                    out_buf.freebuffer()

        return out


# ────────────────────────────────────────────────────────────
# SOFTWARE REFERENCE (for comparison on PC or board)
# ────────────────────────────────────────────────────────────
class SoftwareCnnReference:
    """
    Pure NumPy INT8 CNN inference (identical to layerwise_sweep_t6.py).
    Used to verify FPGA output and measure accuracy without the board.
    """
    def __init__(self, weights_dict, tables_path="axm_tables_t6.npz"):
        self.weights = weights_dict
        self.tables  = np.load(tables_path)

    def _quantize_unsigned(self, x):
        m = np.max(x)
        if m < 1e-12: return np.zeros_like(x, dtype=np.uint8), 1e-12
        s = m / 255.0
        return np.clip(np.round(x / s), 0, 255).astype(np.uint8), s

    def _axm_conv2d(self, x, layer_name, batch=25):
        import tensorflow as tf
        model = tf.keras.models.load_model("baseline_cnn.keras")
        kernel, bias = model.get_layer(layer_name).get_weights()
        tables = self.tables
        cfg    = LAYER_CONFIG[layer_name]
        design = ["exact","trunc","compensated","orbased"][cfg["mode"]]
        table  = tables[design]
        N, H, W, Cin = x.shape
        kh, kw, _, Cout = kernel.shape
        xq, ascale = self._quantize_unsigned(x)
        wsign = np.sign(kernel).astype(np.int8)
        wabs  = np.abs(kernel)
        m     = np.max(wabs)
        ws    = m / 255.0 if m > 1e-12 else 1e-12
        wq    = np.clip(np.round(wabs / ws), 0, 255).astype(np.uint8)
        pad   = kh // 2
        xq_p  = np.pad(xq, ((0,0),(pad,pad),(pad,pad),(0,0)))
        out   = np.zeros((N,H,W,Cout), dtype=np.float32)
        for start in range(0, N, batch):
            end = min(start+batch, N)
            acc = np.zeros((end-start,H,W,Cout), dtype=np.int64)
            for i in range(kh):
                for j in range(kw):
                    xs  = xq_p[start:end, i:i+H, j:j+W, :]
                    wij = wq[i,j,:,:]
                    sij = wsign[i,j,:,:]
                    c   = table[xs[...,:,None], wij[None,None,None,:,:]]
                    acc += (c * sij[None,None,None,:,:]).astype(np.int64).sum(axis=3)
            out[start:end] = (acc.astype(np.float64)*ascale*ws
                              + bias[None,None,None,:]).astype(np.float32)
        return out


# ────────────────────────────────────────────────────────────
# MAIN: ON-BOARD INFERENCE LOOP
# ────────────────────────────────────────────────────────────
def run_onboard_inference(n_images=100):
    """
    Runs n_images through the FPGA accelerator and measures:
    - Per-image latency (ms)
    - Total throughput (FPS)
    - Classification accuracy
    - FPGA resource utilization (printed from Vivado report)
    """
    print("=" * 58)
    print("  PYNQ-Z2 CNN Accelerator — On-Board Inference")
    print("=" * 58)

    # Load weights and test data
    weights = np.load(WEIGHT_NPY, allow_pickle=True).item()
    x_test  = np.load("x_test.npy")[:n_images]
    y_test  = np.load("y_test.npy")[:n_images]

    # Load PYNQ overlay
    overlay = CnnAxmOverlay()

    correct    = 0
    latencies  = []

    print(f"\nRunning {n_images} images through FPGA...\n")

    import tensorflow as tf
    model = tf.keras.models.load_model("baseline_cnn.keras")

    for idx in range(n_images):
        img = x_test[idx]           # (28,28,1) float32 [0,1]
        t_start = time.perf_counter()

        # ── Quantize input ─────────────────────
        act_scale = np.max(img) / 255.0 if np.max(img) > 1e-12 else 1e-12
        act_q     = np.clip(np.round(img / act_scale), 0, 255).astype(np.uint8)

        # ── Layer 1: conv1 (EXACT) ─────────────
        out1 = overlay.run_conv_layer(act_q, weights, "conv1", layer_id=0)
        out1 = np.maximum(out1, 0)                      # ReLU
        # MaxPool 2x2
        out1 = out1.reshape(14,2,14,2,16).max(axis=(1,3))  # (14,14,16)

        # ── Layer 2: conv2 (COMPENSATED) ───────
        act_scale2 = np.max(out1)/255.0 if np.max(out1)>1e-12 else 1e-12
        act_q2 = np.clip(np.round(out1/act_scale2),0,255).astype(np.uint8)
        out2   = overlay.run_conv_layer(act_q2, weights, "conv2", layer_id=1)
        out2   = np.maximum(out2, 0)
        out2   = out2.reshape(7,2,7,2,32).max(axis=(1,3))  # (7,7,32)

        # ── Layer 3: conv3 (COMPENSATED) ───────
        act_scale3 = np.max(out2)/255.0 if np.max(out2)>1e-12 else 1e-12
        act_q3 = np.clip(np.round(out2/act_scale3),0,255).astype(np.uint8)
        out3   = overlay.run_conv_layer(act_q3, weights, "conv3", layer_id=2)
        out3   = np.maximum(out3, 0)                    # (7,7,64)

        # ── Layer 4: conv4 (TRUNCATED) ─────────
        act_scale4 = np.max(out3)/255.0 if np.max(out3)>1e-12 else 1e-12
        act_q4 = np.clip(np.round(out3/act_scale4),0,255).astype(np.uint8)
        out4   = overlay.run_conv_layer(act_q4, weights, "conv4", layer_id=3)
        out4   = np.maximum(out4, 0)                    # (7,7,64)

        # ── GlobalAveragePooling + FC (in software) ─
        gap    = out4.mean(axis=(0,1))                  # (64,)
        w_fc1, b_fc1 = model.get_layer("fc1").get_weights()
        w_fc2, b_fc2 = model.get_layer("fc2").get_weights()
        fc1    = np.maximum(gap @ w_fc1 + b_fc1, 0)    # (64,)
        logits = fc1 @ w_fc2 + b_fc2                   # (10,)
        pred   = np.argmax(logits)

        t_end = time.perf_counter()
        latency_ms = (t_end - t_start) * 1000
        latencies.append(latency_ms)

        if pred == y_test[idx]:
            correct += 1

        if (idx + 1) % 10 == 0:
            print(f"  [{idx+1:3d}/{n_images}] "
                  f"Pred: {CLASS_NAMES[pred]:15s} | "
                  f"True: {CLASS_NAMES[y_test[idx]]:15s} | "
                  f"Latency: {latency_ms:.1f}ms")

    # ── Results ──────────────────────────────────────────────
    accuracy    = correct / n_images * 100
    mean_lat    = np.mean(latencies)
    std_lat     = np.std(latencies)
    throughput  = 1000.0 / mean_lat   # FPS

    print("\n" + "=" * 58)
    print("  ON-BOARD INFERENCE RESULTS")
    print("=" * 58)
    print(f"  Images tested    : {n_images}")
    print(f"  Correct          : {correct}")
    print(f"  Accuracy         : {accuracy:.2f}%")
    print(f"  Mean Latency     : {mean_lat:.2f} ms/image")
    print(f"  Std Latency      : {std_lat:.2f} ms")
    print(f"  Throughput       : {throughput:.1f} FPS")
    print(f"\n  Multiplier Assignment:")
    print(f"    conv1 → EXACT        (sensitivity 1.000)")
    print(f"    conv2 → COMPENSATED  (sensitivity 0.180)")
    print(f"    conv3 → COMPENSATED  (sensitivity 0.008)")
    print(f"    conv4 → TRUNCATED    (sensitivity 0.014)")
    print("=" * 58)

    # Save results
    with open("pynq_results.txt", "w") as f:
        f.write(f"accuracy={accuracy:.4f}\n")
        f.write(f"mean_latency_ms={mean_lat:.4f}\n")
        f.write(f"throughput_fps={throughput:.4f}\n")
        f.write(f"n_images={n_images}\n")
        f.write(f"correct={correct}\n")

    print("\nSaved: pynq_results.txt")
    return accuracy, mean_lat, throughput


# ────────────────────────────────────────────────────────────
# ENTRY POINT
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    if "--extract-weights" in sys.argv:
        # Run on PC to generate weights file for PYNQ board
        extract_weights_from_keras()
    elif ON_BOARD:
        # Run on physical PYNQ-Z2 board
        run_onboard_inference(n_images=100)
    else:
        print("Usage:")
        print("  On PC     : python pynq_inference.py --extract-weights")
        print("  On PYNQ   : python pynq_inference.py")
        print("")
        print("Files needed on PYNQ board:")
        print("  cnn_axm.bit      (from Vivado)")
        print("  cnn_axm.hwh      (from Vivado)")
        print("  weights_int8.npy (from --extract-weights)")
        print("  x_test.npy")
        print("  y_test.npy")
