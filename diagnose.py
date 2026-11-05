import numpy as np, tensorflow as tf

tables = np.load("axm_tables.npz")
model = tf.keras.models.load_model("baseline_cnn.keras")
x_test = np.load("x_test.npy"); y_test = np.load("y_test.npy")

print("x_test shape/dtype/range:", x_test.shape, x_test.dtype, x_test.min(), x_test.max())
print("y_test sample:", y_test[:10])

# 1. Sanity check: does the REAL Keras model (no AxM) predict correctly?
real_preds = model.predict(x_test[:200], verbose=0)
real_acc = (real_preds.argmax(1) == y_test[:200]).mean()*100
print(f"\n[Check 1] Real Keras model accuracy on 200 images: {real_acc:.2f}% (should be ~84%)")

# 2. Check the "exact" lookup table actually behaves like real multiplication
exact_table = tables["exact"]
test_a, test_b = 37, 91
print(f"\n[Check 2] exact_table[{test_a},{test_b}] = {exact_table[test_a,test_b]} (should be {test_a*test_b})")

# 3. Check conv1 weight stats to see if quantization scale looks sane
w = model.get_layer("conv1").get_weights()[0]
print(f"\n[Check 3] conv1 kernel shape={w.shape} min={w.min():.4f} max={w.max():.4f}")

# 4. Manually run axm_conv2d for conv1 with 'exact' table and compare to real Keras conv1 output
def quantize_unsigned(x):
    m = np.max(x)
    if m < 1e-12: return np.zeros_like(x, dtype=np.uint8), 1e-12
    s = m/255.0
    return np.clip(np.round(x/s),0,255).astype(np.uint8), s

def quantize_signed(w):
    sign = np.sign(w).astype(np.int8); mag = np.abs(w)
    m = np.max(mag)
    if m < 1e-12: return sign, np.zeros_like(mag,dtype=np.uint8), 1e-12
    s = m/255.0
    return sign, np.clip(np.round(mag/s),0,255).astype(np.uint8), s

def axm_conv2d_debug(x, kernel, bias, table_name, batch=5):
    table = tables[table_name]
    N,H,W,Cin = x.shape; kh,kw,_,Cout = kernel.shape
    xq,ascale = quantize_unsigned(x)
    wsign,wq,wscale = quantize_signed(kernel)
    pad = kh//2
    xq_p = np.pad(xq, ((0,0),(pad,pad),(pad,pad),(0,0)))
    out = np.zeros((N,H,W,Cout), dtype=np.float32)
    for start in range(0,N,batch):
        end = min(start+batch,N)
        acc = np.zeros((end-start,H,W,Cout), dtype=np.int64)
        for i in range(kh):
            for j in range(kw):
                xs = xq_p[start:end, i:i+H, j:j+W, :]
                wij = wq[i,j,:,:]; sij = wsign[i,j,:,:]
                c = table[xs[...,:,None], wij[None,None,None,:,:]]
                c = (c*sij[None,None,None,:,:]).astype(np.int64)
                acc += c.sum(axis=3)
        out[start:end] = (acc.astype(np.float64)*ascale*wscale + bias[None,None,None,:]).astype(np.float32)
    return out

x_small = x_test[:5]
w1, b1 = model.get_layer("conv1").get_weights()
my_conv1 = axm_conv2d_debug(x_small, w1, b1, "exact")
my_conv1_relu = np.maximum(my_conv1, 0)

real_conv1_model = tf.keras.Model(inputs=model.inputs, outputs=model.get_layer("conv1").output)
real_conv1 = real_conv1_model.predict(x_small, verbose=0)

print(f"\n[Check 4] my axm_conv2d('exact') vs real Keras conv1 output:")
print(f"  my_conv1 mean={my_conv1_relu.mean():.4f} std={my_conv1_relu.std():.4f}")
print(f"  real_conv1 mean={real_conv1.mean():.4f} std={real_conv1.std():.4f}")
print(f"  max abs diff={np.abs(my_conv1_relu - real_conv1).max():.4f}")
