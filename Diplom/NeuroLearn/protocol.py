import numpy as np
import os
import joblib
import Logging as Log
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import time
import datetime


def save_results(path):
    data = np.loadtxt(f"{path}/result.txt")
    try:
        seconds = [i for i in range(1, len(data) + 1)]

        fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
        ax.plot(seconds, data)
        fig.subplots_adjust(left=0.035, bottom=0.02, right=1.0, top=1.0)
        plt.savefig(f"{path}/results.png")
        plt.close()
    except Exception as ex:
        return


def get_data():
    data = {}
    for i in range(0, 6):
        data[i] = []

    for dir_id in range(0, 12, 2):
        files = []
        directory = f"test/{dir_id}"

        for filename in os.listdir(directory):
            if filename.endswith('.txt'):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    files.append(file_path)

        if len(files) == 0:
            print("Loading data error")
            return
        print(f"Loaded {len(files)} files from {dir_id} directory")

        for i, file in enumerate(files):
            data[int(dir_id / 2)].append(abs(np.fft.fft(np.loadtxt(file))))
            data[int(dir_id / 2)][i] = data[int(dir_id / 2)][i][:1000]

    return data


def get_weights(mod):
    main_dir = "the_best"

    if not os.path.exists(os.path.join(main_dir, mod)):
        return None
    model = joblib.load(os.path.join(main_dir, mod))

    return model


def update_progressbar(progressbar, value):
    progressbar["value"] = value


def main():
    log = Log.Logging(True, "protocol")

    log_categories = [
        "LogResult",
        "logStatus"
    ]

    log.log(log_categories[1], 1, "Model loading")
    model = get_weights("mlp_model.joblib")

    if model is None:
        log.log(log_categories[0], 3, "Model not loaded")
        return
    log.log(log_categories[1], 1, "Done")

    log.log(log_categories[1], 1, "Loading data")
    data = get_data()
    log.log(log_categories[1], 1, "Done")

    log.log(log_categories[1], 1, "Files counting")

    total_files = 0
    for i in range(len(data)):
        total_files += len(data[i])
    log.log(log_categories[1], 1, f"Done. Total files {total_files}")

    progress = 0
    progress_step = 0

    root = tk.Tk()
    root.title("Protocol creating")

    progressbar = ttk.Progressbar(root, length=300, mode="determinate")
    progressbar.pack()

    for i in range(6):
        dir_log = Log.Logging(True, f"protocol/proc_{int(i * 2)}")
        file_dir = f"protocol/proc_{int(i * 2)}/0"

        for file_num, fft in enumerate(data[i]):
            start_time = time.time()

            if (file_num + 1) % 2 == 0:
                file_dir = f"protocol/proc_{int(i * 2)}/{file_num}"
            file_log = Log.Logging(False, file_dir)

            if None in fft:
                file_log.log(log_categories[0], 1, "Noise")
                with open(f"{file_dir}/result.txt", "a+") as file:
                    file.seek(0, 2)
                    file.write("-1" + '\n')
            elif len(fft) < 1000:
                file_log.log(log_categories[0], 1, f"Little data: {len(fft)} of 1000")
            else:
                file_log.log(log_categories[1], 1, "Done")

                # make predictions on the new data
                y_pred = model.predict(np.array(fft).reshape(1, -1))

                y_pred = int(y_pred / 2)
                classes = [0, 2, 4, 6, 8, 10]
                file_log.log(log_categories[1], 1, str(classes[int(y_pred)]) + '%')

                with open(f"{file_dir}/result.txt", "a+") as file:
                    file.seek(0, 2)
                    file.write(str(classes[int(y_pred)]) + '\n')
                file.close()

                save_results(file_dir)

                with open(f"{file_dir}/{file_num}.txt", "a+") as current_file:
                    current_file.seek(0, 2)
                    for num in fft:
                        current_file.write(str(num) + "\n")
                current_file.close()

                # Progress
                progress += 1 / total_files * 100
                if progress - progress_step >= 0:
                    progress_step += 5
                    print("{:.2f}".format(progress), "%")

                    update_progressbar(progressbar, progress)
                    root.update()

                    # Time
                    end_time = time.time()
                    time_diff = end_time - start_time

                    current_time = time_diff * file_num
                    max_time = time_diff * total_files
                    diff_time = max_time - current_time

                    remaining_time = datetime.timedelta(seconds=diff_time)
                    remaining_time_str = str(
                        remaining_time - datetime.timedelta(microseconds=remaining_time.microseconds)).split(
                        ':')[-3:]
                    print("Time remaining: " + ':'.join(remaining_time_str))


if __name__ == "__main__":
    main()
