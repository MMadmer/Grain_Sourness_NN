import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import os
import math
import cmath
import time
import datetime
import numpy as np
import threading
import random
import shuffle_files


# def dft(x):
#     N = len(x)
#     X = []
#     for k in range(N):
#         Xk = 0
#         for n in range(N):
#             Xk += x[n] * cmath.exp(-2j * cmath.pi * n * k / N)
#         X.append(Xk)
#     return X


def process_task(j, V, selection_duration, step, selection_folder_name, total_files_in_folder,
                 selection_images_folder_name):
    print("Task complete")


def dft(x):
    return np.fft.fft(x)


def counting_files(folder):
    global total_files
    global start_file
    global num_files
    global selection_duration
    global step

    total_files_in_folder = 0
    folder_name = f"proc_{folder}"

    if not os.path.exists(folder_name):
        print(f"The folder {folder_name} does not exist.")
        return

    # Read pol sig from pol_sig.txt file
    pol_sig_start = []
    pol_sig_end = []

    pol_sig_file_path = os.path.join(folder_name, "pol_sig.txt")
    if not os.path.exists(pol_sig_file_path):
        print(f"The file {pol_sig_file_path} in {folder_name} does not exist.")
        return

    with open(pol_sig_file_path, "r") as pol_sig_file:
        for line in pol_sig_file:
            values = line.split()
            if len(values) == 2:
                try:
                    pol_sig_start.append(float(values[0]))
                    pol_sig_end.append(float(values[1]))
                except ValueError:
                    # If the string cannot be converted to a float, skip it
                    continue

    # Split raw selection into pol sig
    for i in range(start_file, num_files + 1):
        file_path = os.path.join(folder_name, f"{i}.txt")
        if not os.path.exists(file_path):
            print(f"The file {file_path} does not exist.")
            continue

        V = []
        with open(file_path, "r") as data_file:
            # Skip the first 11 lines
            for j in range(11):
                next(data_file)
            # Parse the data as a time sequence
            for line in data_file:
                values = line.split()
                if len(values) == 2:
                    try:
                        t_val = float(values[0])
                        v_val = float(values[1])
                        if pol_sig_start[i - 1] <= t_val <= pol_sig_end[i - 1]:
                            V.append(v_val)
                        else:
                            continue
                    except ValueError:
                        # If the string cannot be converted to a float, skip it
                        continue

        # Calculating total files
        for j in range(1, math.ceil((len(V) - selection_duration + step) / step)):
            total_files_in_folder += 1
    total_files += total_files_in_folder


def update_progressbar(progressbar, value):
    progressbar["value"] = value


start_file = 1
num_files = 45
total_files = 0
selection_duration = 5000
step = 100


def main():
    global total_files
    global start_file
    global num_files
    global selection_duration
    global step

    folders = range(0, 12, 2)
    selection_folder_prefix = "Selection_proc"
    selection_images_folder_prefix = "Selection_images"
    progress = 0

    root = tk.Tk()
    root.title("Selection creating")

    progressbar = ttk.Progressbar(root, length=300, mode="determinate")
    progressbar.pack()

    print("Counting all files to be generated")

    threads = []
    for folder in folders:
        threads.append(threading.Thread(target=counting_files, args=(folder, )))
    # Start the threads
    for thread in threads:
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    threads.clear()

    print("Done")
    print(f"Total files: {total_files}")

    print("Creating samples")
    current_file = -1
    for folder in folders:
        total_files_in_folder = 0
        folder_name = f"proc_{folder}"

        if not os.path.exists(folder_name):
            print(f"The folder {folder_name} does not exist.")
            continue

        # Read pol sig from pol_sig.txt file
        pol_sig_start = []
        pol_sig_end = []

        pol_sig_file_path = os.path.join(folder_name, "pol_sig.txt")
        if not os.path.exists(pol_sig_file_path):
            print(f"The file {pol_sig_file_path} in {folder_name} does not exist.")
            continue

        with open(pol_sig_file_path, "r") as pol_sig_file:
            for line in pol_sig_file:
                values = line.split()
                if len(values) == 2:
                    try:
                        pol_sig_start.append(float(values[0]))
                        pol_sig_end.append(float(values[1]))
                    except ValueError:
                        # If the string cannot be converted to a float, skip it
                        continue

        selection_folder_name = f"{selection_folder_prefix}_{folder}"
        if not os.path.exists(selection_folder_name):
            os.makedirs(selection_folder_name)

        selection_images_folder_name = f"{selection_images_folder_prefix}_{folder}"
        if not os.path.exists(selection_images_folder_name):
            os.makedirs(selection_images_folder_name)

        # if not os.path.exists(f"Selection_Seeds_Images/proc_{folder}"):
        #     os.makedirs(f"Selection_Seeds_Images/proc_{folder}")

        # Split raw selection into pol sig
        for i in range(start_file, num_files + 1):
            file_path = os.path.join(folder_name, f"{i}.txt")
            if not os.path.exists(file_path):
                print(f"The file {file_path} does not exist.")
                continue

            V = []
            with open(file_path, "r") as data_file:
                # Skip the first 11 lines
                for j in range(11):
                    next(data_file)
                # Parse the data as a time sequence
                for line in data_file:
                    values = line.split()
                    if len(values) == 2:
                        try:
                            t_val = float(values[0])
                            v_val = float(values[1])
                            if pol_sig_start[i - 1] <= t_val <= pol_sig_end[i - 1]:
                                V.append(v_val)
                            else:
                                continue
                        except ValueError:
                            # If the string cannot be converted to a float, skip it
                            continue

            progress_step = 0
            for j in range(1, math.ceil((len(V) - selection_duration + step) / step)):
                start_time = time.time()
                current_file += 1

                total_files_in_folder += 1
                selection_V = []
                current_min = j * step - step
                current_max = current_min + selection_duration
                for k in range(current_min, current_max):
                    selection_V.append(V[k])

                # # Creating selection files
                # selection_file_path = os.path.join(selection_folder_name, f"{total_files_in_folder}.txt")
                # with open(selection_file_path, "w") as selection_file:
                #     for num in selection_V:
                #         selection_file.write(str(num) + "\n")

                # Fourier
                coeffs = dft(selection_V)
                freq = 5000
                N = int(len(coeffs) / 5)
                freq_step = [k * freq / N for k in range(N)]
                mags = [abs(coeffs[x]) for x in range(N)]

                # Creating selection files
                selection_file_path = os.path.join(selection_folder_name, f"{total_files_in_folder}.txt")
                with open(selection_file_path, "w") as selection_file:
                    for num in mags:
                        selection_file.write(str(num) + "\n")

                # # Create a plot with only the line visible
                # fig, ax = plt.subplots(figsize=(12.8, 7.2), dpi=100)
                # ax.plot(freq_step, mags)
                # ax.axis("off")
                #
                # # Set the border styles
                # fig.subplots_adjust(left=0, bottom=0, right=1.0, top=1.0)
                #
                # plt.savefig(f"{selection_images_folder_name}/{total_files_in_folder}.png", bbox_inches='tight', dpi=100,
                #             format="png")
                # plt.close()

                # Progress
                progress += 1 / total_files * 100
                if progress - progress_step >= 0:
                    progress_step += 2
                    print("{:.2f}".format(progress), "%")

                    update_progressbar(progressbar, progress)
                    root.update()

                    # Time
                    end_time = time.time()
                    time_diff = end_time - start_time

                    current_time = time_diff * current_file
                    max_time = time_diff * total_files
                    diff_time = max_time - current_time

                    remaining_time = datetime.timedelta(seconds=diff_time)
                    remaining_time_str = str(
                        remaining_time - datetime.timedelta(microseconds=remaining_time.microseconds)).split(':')[
                                         -3:]
                    print("Time remaining: " + ':'.join(remaining_time_str))
    print("Done")

    root.destroy()

    print("Sample shuffle")

    for folder in folders:
        selection_folder_name = f"{selection_folder_prefix}_{folder}"
        # print(selection_folder_name)
        # shuffle_files.shuffle(selection_folder_name)
        threads.append(threading.Thread(target=shuffle_files.shuffle, args=(selection_folder_name,)))
    # Start the threads
    for thread in threads:
        thread.start()
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    threads.clear()

    print("Done")


if __name__ == "__main__":
    main()
