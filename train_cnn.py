"""
train_cnn.py
Trains the baseline CNN (TensorFlow/Keras) used for the layer-sensitivity
approximate-multiplier project. Fashion-MNIST is used (28x28 grayscale,
10 classes) as it trains fast on CPU while still being a real,
non-trivial benchmark -- CIFAR-10 can be substituted later by swapping
the dataset loader and adjusting input_shape.
"""
import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
import gzip
import os

tf.random.set_seed(42)
np.random.seed(42)

# ---- Data (loaded from local gz files -- downloaded directly from the
# official Zalando Research GitHub repo, since Google Storage is not
# reachable from this sandboxed environment's network allowlist) ----
def load_mnist_gz(images_path, labels_path):
    with gzip.open(labels_path, "rb") as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8, offset=8)
    with gzip.open(images_path, "rb") as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8, offset=16)
        images = images.reshape(len(labels), 28, 28)
    return images, labels

x_train, y_train = load_mnist_gz("train-images-idx3-ubyte.gz", "train-labels-idx1-ubyte.gz")
x_test, y_test = load_mnist_gz("t10k-images-idx3-ubyte.gz", "t10k-labels-idx1-ubyte.gz")
x_train = x_train.astype("float32") / 255.0
x_test = x_test.astype("float32") / 255.0
x_train = x_train[..., None]
x_test = x_test[..., None]

# ---- Model: compact 4-conv-layer CNN (named layers for later sensitivity scoring) ----
model = models.Sequential([
    layers.Input(shape=(28, 28, 1)),
    layers.Conv2D(16, 3, activation="relu", padding="same", name="conv1"),
    layers.MaxPooling2D(2),
    layers.Conv2D(32, 3, activation="relu", padding="same", name="conv2"),
    layers.MaxPooling2D(2),
    layers.Conv2D(64, 3, activation="relu", padding="same", name="conv3"),
    layers.Conv2D(64, 3, activation="relu", padding="same", name="conv4"),
    layers.GlobalAveragePooling2D(),
    layers.Dense(64, activation="relu", name="fc1"),
    layers.Dense(10, activation="softmax", name="fc2"),
])

model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

model.summary()

history = model.fit(x_train, y_train,
                     validation_split=0.1,
                     epochs=8,
                     batch_size=128,
                     verbose=2)

test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
print(f"\nBASELINE (exact) TEST ACCURACY: {test_acc*100:.2f}%")

model.save("baseline_cnn.keras")
np.save("x_test.npy", x_test)
np.save("y_test.npy", y_test)
np.save("x_calib.npy", x_train[:256])   # small calibration batch, no labels needed
np.save("y_calib.npy", y_train[:256])

with open("baseline_accuracy.txt", "w") as f:
    f.write(f"{test_acc*100:.4f}\n")

print("Saved: baseline_cnn.keras, x_test.npy, y_test.npy, x_calib.npy, y_calib.npy, baseline_accuracy.txt")
