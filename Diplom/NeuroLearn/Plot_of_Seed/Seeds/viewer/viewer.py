import matplotlib.pyplot as plt
import os
import numpy as np
import math


def dft(data):
    part_re = []
    part_im = []
    spectre = []

    for i in range(len(data)):
        part_re.append(0)
        part_im.append(0)

        for j in range(len(data)):
            part_re[i] = part_re[i] + data[j] * math.cos(2 * math.pi * i * j / len(data))
            part_im[i] = part_im[i] + data[j] * math.sin(2 * math.pi * i * j / len(data))

        spectre.append(round(math.sqrt(part_re[i] ** 2 + (part_im[i] * -1) ** 2)))
        if i % 200 == 0:
            print(i)

    return spectre


def original(file_path):
    t = []
    V = []

    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return
    else:
        with open(file_path, 'r') as f:
            # Skip the first 11 lines
            for j in range(11):
                next(f)
            # Parse the data as a time sequence
            for line in f:
                values = line.split()
                if len(values) == 2:
                    try:
                        t_val = float(values[0])
                        v_val = float(values[1])
                        t.append(t_val)
                        V.append(v_val)
                    except ValueError:
                        # If the string cannot be converted to a float, skip it
                        continue

        fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
        ax.plot(t, V)
        ax.set_ylabel("V")
        ax.set_xlabel("t")
        fig.subplots_adjust(left=0.02, bottom=0.02, right=1.0, top=1.0)
        plt.show()
        # plt.savefig(f"Seeds_Images/{file}/{i}.png", dpi=100)

        t.clear()
        V.clear()


def fourier(file_path):
    V = []

    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return

    with open(file_path, 'r') as f:
        # Skip the first 11 lines
        for j in range(11):
            next(f)
        # Parse the data as a time sequence
        for line in f:
            values = line.split()
            if len(values) == 2:
                try:
                    v_val = float(values[1])
                    V.append(v_val)
                except ValueError:
                    # If the string cannot be converted to a float, skip it
                    continue

    # Fourier
    coeffs = np.fft.fft(V)
    freq = 5000
    N = len(V)
    freq_step = [k * freq / N for k in range(N)]

    mags = [abs(x) for x in coeffs]

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(freq_step, mags)
    fig.subplots_adjust(left=0.025, bottom=0.02, right=1.0, top=1.0)
    V.clear()
    plt.show()
    # plt.savefig(f"Seeds_Images/{file}/{i}.png", dpi=100)


def local_fourier(file_path, pol_sig):
    if not os.path.exists(file_path):
        print(f"The file {file_path} does not exist.")
        return

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
                    if pol_sig[0] <= t_val <= pol_sig[1]:
                        V.append(v_val)
                    else:
                        continue
                except ValueError:
                    # If the string cannot be converted to a float, skip it
                    continue

    # Fourier
    # coeffs = np.fft.fft(V)
    coeffs = dft(V)
    freq = 5000
    N = len(coeffs)
    freq_step = [k * freq / N for k in range(N)]

    mags = [abs(x) for x in coeffs]

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(freq_step, coeffs)
    fig.subplots_adjust(left=0.02, bottom=0.02, right=1.0, top=1.0)
    V.clear()
    plt.show()
    # plt.savefig(f"Seeds_Images/{file}/{i}.png", dpi=100)
