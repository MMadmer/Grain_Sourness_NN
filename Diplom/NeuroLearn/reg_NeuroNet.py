from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import Logging as Log
import os
import numpy as np
import time
import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from joblib import dump


def samples_loading():
    log.log(log_categories[1], 1, "Loading training sample...")
    base_dir = os.path.abspath("./Plot_of_Seed/Seeds")
    retrieved_files = 20 + 1
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

    return dataset


def update_progressbar(progress_bar, value):
    progress_bar["value"] = value


log_categories = [
    "logResult",
    "logStatus"
]
log = Log.Logging(True, "reg_log")
if log.ENABLE_LOGGING:
    if not os.path.exists(f"reg_results/{log.log_time}"):
        os.makedirs(f"reg_results/{log.log_time}")


def main():
    dataset = samples_loading()

    # extract the input features and labels from the dataset
    X = [data[0] for data in dataset]
    y = np.array([data[1] for data in dataset])
    X = np.squeeze(X)

    dataset.clear()

    # Load your dataset and split it into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    log.log(log_categories[1], 1, "Creating neural network")
    reg = MLPRegressor(hidden_layer_sizes=(250, 125, 62,), activation='relu', solver='adam',
                       verbose=10, max_iter=30, random_state=42, batch_size=16)
    log.log(log_categories[1], 1, "Done")

    # train the MLP on the training data
    log.log(log_categories[1], 1, "Training neural network")
    progress = 0
    root = tk.Tk()
    root.title("Selection creating")
    progressbar = ttk.Progressbar(root, length=300, mode="determinate")
    progressbar.pack()

    for ep in range(reg.max_iter):
        start_time = time.time()

        reg.partial_fit(X_train, y_train)

        # Progress
        progress += 1 / reg.max_iter * 100
        print("{:.2f}".format(progress), "%")

        update_progressbar(progressbar, progress)
        root.update()

        # Time
        end_time = time.time()
        time_diff = end_time - start_time

        current_time = time_diff * ep
        max_time = time_diff * reg.max_iter
        diff_time = max_time - current_time

        remaining_time = datetime.timedelta(seconds=diff_time)
        remaining_time_str = str(remaining_time - datetime.timedelta(microseconds=remaining_time.microseconds)).split(
            ':')[
                             -3:]
        print("Time remaining: " + ':'.join(remaining_time_str))
    root.destroy()
    log.log(log_categories[1], 1, "Done")

    log.log(log_categories[1], 1, "Weights saving")
    dump(reg, f"reg_results/{log.log_time}/reg_model.joblib")
    log.log(log_categories[1], 1, "Done")

    # Evaluate the model on the testing set
    y_pred = reg.predict(X_test)

    mse = mean_squared_error(y_test, y_pred)

    log.log(log_categories[0], 1, "Mean Squared Error: " + str(mse))

    plt.plot(reg.loss_curve_)
    plt.title('Loss curve')
    plt.xlabel('Iteration')
    plt.ylabel('Loss')
    plt.savefig(f"reg_results/{log.log_time}/loss_plot.png")
    plt.show()


if __name__ == "__main__":
    main()
