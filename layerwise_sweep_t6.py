"""
layerwise_sweep_t6.py
=====================
Re-runs the 4-layer × 3-multiplier accuracy sweep using the TRUNC=6
lookup tables (axm_tables_t6.npz). Everything else is identical to
layerwise_sweep.py so results are directly comparable.

Writes: layerwise_results_t6.csv
"""
import numpy as np, tensorflow as tf, csv, time

tables = np.load("axm_tables_t6.npz")
model = tf.keras.models.load_model("baseline_cnn.keras")
x_test = np.load("x_test.npy")
y_test = np.load("y_test.npy")
LAYERS = ["conv1", "conv2", "conv3", "conv4"]
DESIGNS = ["trunc", "orbased", "compensated"]

def quantize_unsigned(x):
    m = np.max(x)
    if m < 1e-12: return np.zeros_like(x, dtype=np.uint8), 1e-12
    s = m / 255.0
    return np.clip(np.round(x / s), 0, 255).astype(np.uint8), s

def quantize_signed(w):
    sign = np.sign(w).astype(np.int8)
    mag = np.abs(w)
    m = np.max(mag)
    if m < 1e-12: return sign, np.zeros_like(mag, dtype=np.uint8), 1e-12
    s = m / 255.0
    return sign, np.clip(np.round(mag / s), 0, 255).astype(np.uint8), s

def axm_conv2d(x, kernel, bias, table_name, batch=25):
    table = tables[table_name]
    N, H, W, Cin = x.shape
    kh, kw, _, Cout = kernel.shape
    xq, ascale = quantize_unsigned(x)
    wsign, wq, wscale = quantize_signed(kernel)
    pad = kh // 2
    xq_p = np.pad(xq, ((0, 0), (pad, pad), (pad, pad), (0, 0)))
    out = np.zeros((N, H, W, Cout), dtype=np.float32)
    for start in range(0, N, batch):
        end = min(start + batch, N)
        acc = np.zeros((end - start, H, W, Cout), dtype=np.int64)
        for i in range(kh):
            for j in range(kw):
                xs = xq_p[start:end, i:i + H, j:j + W, :]
                wij = wq[i, j, :, :]
                sij = wsign[i, j, :, :]
                c = table[xs[..., :, None], wij[None, None, None, :, :]]
                c = (c * sij[None, None, None, :, :]).astype(np.int64)
                acc += c.sum(axis=3)
        out[start:end] = (acc.astype(np.float64) * ascale * wscale
                          + bias[None, None, None, :]).astype(np.float32)
    return out

def maxpool(x, p=2):
    N, H, W, C = x.shape
    return x.reshape(N, H // p, p, W // p, p, C).max(axis=(2, 4))

def relu(x): return np.maximum(x, 0)

def forward(x, assignment):
    w = {n: model.get_layer(n).get_weights()
         for n in ["conv1", "conv2", "conv3", "conv4", "fc1", "fc2"]}
    h = axm_conv2d(x, w["conv1"][0], w["conv1"][1], assignment["conv1"])
    h = relu(h); h = maxpool(h)
    h = axm_conv2d(h, w["conv2"][0], w["conv2"][1], assignment["conv2"])
    h = relu(h); h = maxpool(h)
    h = axm_conv2d(h, w["conv3"][0], w["conv3"][1], assignment["conv3"])
    h = relu(h)
    h = axm_conv2d(h, w["conv4"][0], w["conv4"][1], assignment["conv4"])
    h = relu(h)
    h = h.mean(axis=(1, 2))
    h = h @ w["fc1"][0] + w["fc1"][1]; h = relu(h)
    logits = h @ w["fc2"][0] + w["fc2"][1]
    e = np.exp(logits - logits.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)

# Baseline (all exact) on full test set
base_assign = {n: "exact" for n in LAYERS}
t0 = time.time()
probs = forward(x_test, base_assign)
baseline_acc = (probs.argmax(1) == y_test).mean() * 100
print(f"[T6] Baseline (all exact) accuracy: {baseline_acc:.2f}% [{time.time()-t0:.0f}s]")

rows = []
for layer in LAYERS:
    for design in DESIGNS:
        assign = {n: "exact" for n in LAYERS}
        assign[layer] = design
        t0 = time.time()
        probs = forward(x_test, assign)
        acc = (probs.argmax(1) == y_test).mean() * 100
        drop = baseline_acc - acc
        rows.append([layer, design, acc, drop])
        print(f"  {layer} + {design}: acc={acc:.2f}%  drop={drop:+.3f}%  [{time.time()-t0:.0f}s]")

with open("layerwise_results_t6.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["layer", "multiplier", "accuracy", "accuracy_drop"])
    w.writerows(rows)

print("\nSaved layerwise_results_t6.csv")
print("\nSummary — mean drop per layer:")
import pandas as pd
df = pd.DataFrame(rows, columns=["layer","multiplier","accuracy","accuracy_drop"])
print(df.groupby("layer")["accuracy_drop"].mean().round(4).to_string())
