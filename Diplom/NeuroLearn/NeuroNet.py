import random
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import ttk
import time
import datetime
import Logging as Log


def relu(t):
    return np.maximum(t, 0)


def softmax(t):
    out = np.exp(t)
    return out / np.sum(out)


def softmax_batch(t):
    out = np.exp(t)
    return out / np.sum(out, axis=1, keepdims=True)


def sparse_cross_entropy(z, y):
    return -np.log(z[0, y])


def sparse_cross_entropy_batch(z, y):
    return -np.log(np.array([z[j, y[j]] for j in range(len(y))]))


def predict(x):
    t1 = x @ W1 + b1
    h1 = relu(t1)
    t2 = h1 @ W2 + b2
    h2 = relu(t2)
    t3 = h2 @ W3 + b3
    h3 = relu(t3)
    t4 = h3 @ W4 + b4
    z = softmax(t4)
    return z


def to_full(y, num_classes):
    y_full = np.zeros((1, num_classes))
    y_full[0, y] = 1
    return y_full


def to_full_batch(y, num_classes):
    y_full = np.zeros((len(y), num_classes))
    for j, yj in enumerate(y):
        y_full[j, yj] = 1
    return y_full


def relu_dervi(t):
    return (t >= 0).astype(float)


def calc_accuracy():
    correct = 0
    for x, y in dataset:
        z = predict(x)
        y_pred = np.argmax(z)
        if y_pred == y:
            correct += 1
    acc = correct / len(dataset)
    return acc


def category_converter(val):
    if val == 0:
        pass
    elif val == 10:
        val = 1
    elif val == 2:
        val = 2
    elif val == 4:
        val = 3
    elif val == 6:
        val = 4
    elif val == 8:
        val = 5

    return val


def update_progressbar(progress_bar, value):
    progress_bar["value"] = value


log_categories = [
    "logResult",
    "logStatus"
]
log = Log.Logging(True)

# ----------------Main------------------
ALPHA = 0.001
NUM_EPOCHS = 15
BATCH_SIZE = 16

INPUT_DIM = 5000
OUT_DIM = 6
H_DIM_1 = 32
H_DIM_2 = 64
H_DIM_3 = 128

x = np.random.randn(1, INPUT_DIM)
y = random.randint(0, OUT_DIM - 1)

log.log(log_categories[1], 1, "Loading training sample...")
base_dir = os.path.abspath("./Plot_of_Seed/Seeds")
retrieved_files = 200 + 1
dataset = []

np.set_printoptions(threshold=np.inf)

total_files = 0
for directory in os.listdir(base_dir):
    loaded_files_from_directory = 0
    full_path = os.path.join(base_dir, directory)
    if not os.path.isdir(full_path) or not directory.startswith("Selection_proc_"):
        continue
    files_in_directory = len(os.listdir(full_path))
    print(directory)

    category = int(directory[len("Selection_proc_"):])
    category = int(category / 2)
    # category = category_converter(category)

    if files_in_directory + 1 >= retrieved_files:
        LOADING = ['.', "..", "..."]
        loading_index = 0
        for i in range(retrieved_files, files_in_directory + 1):
            if not os.path.exists(f"{full_path}/{i}.txt"):
                continue
            loaded_files_from_directory += 1
            if loaded_files_from_directory % 1000 == 0:
                print(f"Loading{LOADING[loading_index]}")
                loading_index = (loading_index + 1) % len(LOADING)

            with open(os.path.join(full_path, f"{i}.txt")) as f:
                data = [float(line.strip()) for line in f]

            # Add the data to the dataset, with the category label
            dataset.append((np.array([data]), category))

            # print(f"{full_path}/{i}.txt")
    total_files += loaded_files_from_directory
    log.log(log_categories[1], 1,
            f"{loaded_files_from_directory} of {files_in_directory} files from {directory} loaded.")

log.log(log_categories[1], 1, f"Done. Total files: {total_files}")
# print(dataset)

# ---------------------------------
# ------------Layers---------------
# ---------------------------------
W1 = np.random.randn(INPUT_DIM, H_DIM_1)
b1 = np.random.randn(1, H_DIM_1)

W2 = np.random.randn(H_DIM_1, H_DIM_2)
b2 = np.random.randn(1, H_DIM_2)

W3 = np.random.randn(H_DIM_2, H_DIM_3)
b3 = np.random.randn(1, H_DIM_3)

W4 = np.random.randn(H_DIM_3, OUT_DIM)
b4 = np.random.randn(1, OUT_DIM)

W1 = (W1 - 0.5) * 2 * np.sqrt(1 / INPUT_DIM)
b1 = (b1 - 0.5) * 2 * np.sqrt(1 / INPUT_DIM)

W2 = (W2 - 0.5) * 2 * np.sqrt(1 / H_DIM_1)
b2 = (b2 - 0.5) * 2 * np.sqrt(1 / H_DIM_1)

W3 = (W3 - 0.5) * 2 * np.sqrt(1 / H_DIM_2)
b3 = (b3 - 0.5) * 2 * np.sqrt(1 / H_DIM_2)

W4 = (W4 - 0.5) * 2 * np.sqrt(1 / H_DIM_3)
b4 = (b4 - 0.5) * 2 * np.sqrt(1 / H_DIM_3)
# ---------------------------------

loss_arr = []

progress = 0

root = tk.Tk()
root.title("Selection creating")

log.log(log_categories[1], 1, "Learning starting")
progressbar = ttk.Progressbar(root, length=300, mode="determinate")
progressbar.pack()

for ep in range(NUM_EPOCHS):
    start_time = time.time()
    random.shuffle(dataset)
    for i in range(len(dataset) // BATCH_SIZE):
        batch_x, batch_y = zip(*dataset[i * BATCH_SIZE: i * BATCH_SIZE + BATCH_SIZE])
        x = np.concatenate(batch_x, axis=0)
        y = np.array(batch_y)
        # x, y = dataset[i]

        # Forward
        t1 = x @ W1 + b1
        h1 = relu(t1)
        t2 = h1 @ W2 + b2
        h2 = relu(t2)
        t3 = h2 @ W3 + b3
        h3 = relu(t3)
        t4 = h3 @ W4 + b4
        z = softmax_batch(t4)
        E = np.sum(sparse_cross_entropy_batch(z, y))

        # Backward
        y_full = to_full_batch(y, OUT_DIM)
        dE_dt4 = z - y_full
        dE_dW4 = h3.T @ dE_dt4
        dE_db4 = np.sum(dE_dt4, axis=0, keepdims=True)
        dE_dh3 = dE_dt4 @ W4.T
        dE_dt3 = dE_dh3 * relu_dervi(t3)
        dE_dW3 = h2.T @ dE_dt3
        dE_db3 = np.sum(dE_dt3, axis=0, keepdims=True)
        dE_dh2 = dE_dt3 @ W3.T
        dE_dt2 = dE_dh2 * relu_dervi(t2)
        dE_dW2 = h1.T @ dE_dt2
        dE_db2 = np.sum(dE_dt2, axis=0, keepdims=True)
        dE_dh1 = dE_dt2 @ W2.T
        dE_dt1 = dE_dh1 * relu_dervi(t1)
        dE_dW1 = x.T @ dE_dt1
        dE_db1 = np.sum(dE_dt1, axis=0, keepdims=True)

        # Update
        W1 -= ALPHA * dE_dW1
        b1 -= ALPHA * dE_db1
        W2 -= ALPHA * dE_dW2
        b2 -= ALPHA * dE_db2
        W3 -= ALPHA * dE_dW3
        b3 -= ALPHA * dE_db3
        W4 -= ALPHA * dE_dW4
        b4 -= ALPHA * dE_db4

        loss_arr.append(E)

    # Progress
    progress = ep / NUM_EPOCHS * 100
    print("{:.2f}".format(progress), "%")

    update_progressbar(progressbar, progress)
    root.update()

    # Time
    end_time = time.time()
    time_diff = end_time - start_time

    current_time = time_diff * ep
    max_time = time_diff * NUM_EPOCHS
    diff_time = max_time - current_time

    remaining_time = datetime.timedelta(seconds=diff_time)
    remaining_time_str = str(remaining_time - datetime.timedelta(microseconds=remaining_time.microseconds)).split(':')[
                         -3:]
    print("Time remaining: " + ':'.join(remaining_time_str))

root.destroy()
log.log(log_categories[1], 1, "Done")

log.log(log_categories[1], 1, "Calculating training accuracy...")
accuracy = calc_accuracy()
log.log(log_categories[1], 1, "Done")

log.log(log_categories[1], 1, "Weights saving")
if not os.path.exists(f"results/{log.log_time}"):
    os.makedirs(f"results/{log.log_time}")

np.savetxt(f"results/{log.log_time}/W1.txt", W1)
np.savetxt(f"results/{log.log_time}/b1.txt", b1)
np.savetxt(f"results/{log.log_time}/W2.txt", W2)
np.savetxt(f"results/{log.log_time}/b2.txt", b2)
np.savetxt(f"results/{log.log_time}/W3.txt", W3)
np.savetxt(f"results/{log.log_time}/b3.txt", b3)
np.savetxt(f"results/{log.log_time}/W4.txt", W4)
np.savetxt(f"results/{log.log_time}/b4.txt", b4)
log.log(log_categories[1], 1, "Done")

real_accuracy = []

# Input
for directory in os.listdir(base_dir):
    acc = 0
    full_path = os.path.join(base_dir, directory)
    if not os.path.isdir(full_path) or not directory.startswith('Selection_proc_'):
        continue
    print(directory)

    category = int(directory[len('Selection_proc_'):])
    category = int(category / 2)

    for i in range(1, retrieved_files):
        if not os.path.exists(f"{full_path}/{i}.txt"):
            print(f"{full_path}/{i}.txt not exist")
            continue

        with open(os.path.join(full_path, f"{i}.txt")) as f:
            data = [float(line.strip()) for line in f]

        print(f"{full_path}/{i}.txt")

        # Add the data to the dataset, with the category label
        x = np.array([data])

        # Using calibrated NN
        class_names = ['0%', '2%', '4%', '6%', '8%', '10%']
        probs = predict(x)
        pred_class = np.argmax(probs)
        print('Predicted class: ', class_names[pred_class])
        if category == pred_class:
            acc += 1

    real_accuracy.append(acc / (retrieved_files - 1) * 100)

log.log(log_categories[0], 1, f"Epochs count: {NUM_EPOCHS}")
log.log(log_categories[0], 1, f"Batch size: {BATCH_SIZE}")
log.log(log_categories[0], 1, f"Alpha: {ALPHA}")
log.log(log_categories[0], 1, f"Neurons in 1st layer: {H_DIM_1}")
log.log(log_categories[0], 1, f"Neurons in 2nd layer: {H_DIM_2}")
log.log(log_categories[0], 1, f"Neurons in 3rd layer: {H_DIM_3}")
log.log(log_categories[0], 1, f"Test set files for each type: {retrieved_files - 1}")

log.log(log_categories[0], 1, "Training average accuracy: " + "{:.2f}".format(accuracy * 100) + '%')
log.log(log_categories[0], 1, "Real accuracy")
log.log(log_categories[0], 1, f"0%: " + "{:.2f}".format(real_accuracy[0]) + '%')
log.log(log_categories[0], 1, f"2%: " + "{:.2f}".format(real_accuracy[2]) + '%')
log.log(log_categories[0], 1, f"4%: " + "{:.2f}".format(real_accuracy[3]) + '%')
log.log(log_categories[0], 1, f"6%: " + "{:.2f}".format(real_accuracy[4]) + '%')
log.log(log_categories[0], 1, f"8%: " + "{:.2f}".format(real_accuracy[5]) + '%')
log.log(log_categories[0], 1, f"10%: " + "{:.2f}".format(real_accuracy[1]) + '%')
log.log(log_categories[0], 1, f"Average real accuracy: " + "{:.2f}".format(sum(real_accuracy) / len(real_accuracy)) +
        '%')

plt.plot(loss_arr)
plt.savefig(f"results/{log.log_time}/loss_plot.png")
plt.show()
