import tensorflow as tf, numpy as np, csv

model = tf.keras.models.load_model("baseline_cnn.keras")
x_calib = np.load("x_calib.npy"); y_calib = np.load("y_calib.npy")
LAYERS = ["conv1","conv2","conv3","conv4"]

def norm(d):
    v = np.array(list(d.values())); lo,hi = v.min(),v.max()
    return {k:(float((x-lo)/(hi-lo)) if hi>lo else 0.5) for k,x in d.items()}

w_var = {n: float(np.var(model.get_layer(n).get_weights()[0])) for n in LAYERS}

x_t = tf.convert_to_tensor(x_calib, dtype=tf.float32)
y_t = tf.convert_to_tensor(y_calib, dtype=tf.int64)

with tf.GradientTape() as tape:
    h = x_t
    acts = {}
    for layer in model.layers:
        h = layer(h)
        if layer.name in LAYERS:
            acts[layer.name] = h
    preds = h
    loss = tf.reduce_mean(tf.keras.losses.sparse_categorical_crossentropy(y_t, preds))

grads = tape.gradient(loss, [model.get_layer(n).kernel for n in LAYERS])

g_mag = {n: float(np.mean(np.abs(g.numpy()))) for n,g in zip(LAYERS, grads)}
a_var = {n: float(np.var(acts[n].numpy())) for n in LAYERS}
a_mean_abs = {n: float(np.mean(np.abs(acts[n].numpy()))) for n in LAYERS}

S1 = norm(w_var)
S2 = norm(g_mag)
S3 = {n: 0.5*S1[n] + 0.5*S2[n] for n in LAYERS}
S4 = norm(a_var)
gxa = {n: g_mag[n]*a_mean_abs[n] for n in LAYERS}
S5 = norm(gxa)

with open("sensitivity_scores.csv","w",newline="") as f:
    w = csv.writer(f); w.writerow(["layer","metric","value"])
    for n in LAYERS:
        w.writerow([n,"S1_weight_var",S1[n]])
        w.writerow([n,"S2_gradient",S2[n]])
        w.writerow([n,"S3_combined",S3[n]])
        w.writerow([n,"S4_activation_var",S4[n]])
        w.writerow([n,"S5_grad_x_act",S5[n]])

print("Saved sensitivity_scores.csv")
for n in LAYERS:
    print(f"{n}: S1={S1[n]:.3f} S2={S2[n]:.3f} S3={S3[n]:.3f} S4={S4[n]:.3f} S5={S5[n]:.3f}")