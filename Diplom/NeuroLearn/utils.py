import numpy as np
import matplotlib.pyplot as plt
import subprocess
import psutil
import os
from datetime import datetime


def launch_ADC():
    proc_name = "adc_reader.exe"

    for proc in psutil.process_iter(['name']):
        if proc.info["name"] == proc_name:
            print("Программа уже запущена")
            break
    else:
        subprocess.Popen(["start", "cmd", '/k', "adc_reader\\adc_reader.exe"], shell=True)


def show_signal(gain=1):
    try:
        gain = float(gain)
    except Exception as ex:
        return
    directory = "adc_reader/output"
    if not os.path.exists(directory):
        return

    # Get a list of all files in the directory, sorted by modification time
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                files.append(file_path)

    if len(files) == 0:
        return
    files = sorted(files, key=os.path.getmtime)

    data = []

    for filename in files:
        if filename.endswith('.txt'):
            data.append(np.loadtxt(filename))

    data = np.concatenate(data)
    for i, V in enumerate(data):
        data[i] = V * gain

    seconds = len(data) / 5024
    step = 0
    t = []

    for i in range(len(data)):
        step += seconds / len(data)
        t.append(step)

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(t, data)
    ax.set_ylabel("V")
    ax.set_xlabel("t")
    fig.subplots_adjust(left=0.045, bottom=0.04, right=1.0, top=1.0)
    t.clear()
    plt.show()


def show_fourier(gain=1):
    data = np.loadtxt("adc_reader/thread_1.txt")

    data = data[:5000]
    for i, V in enumerate(data):
        data[i] = V * gain

    data = np.fft.fft(data)

    freq = 5000
    N = len(data)
    freq_step = [k * freq / N for k in range(N)]

    mags = [abs(x) for x in data]

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(freq_step, mags)
    fig.subplots_adjust(left=0.025, bottom=0.02, right=1.0, top=1.0)
    plt.show()


def show_results():
    if not os.path.exists("result.txt"):
        return

    data = np.loadtxt("result.txt")
    seconds = [i for i in range(1, len(data) + 1)]

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(seconds, data)
    fig.subplots_adjust(left=0.035, bottom=0.02, right=1.0, top=1.0)
    plt.show()


def compile_signal(gain=1):
    directory = "adc_reader/output"
    if not os.path.exists(directory):
        return

    signals_dir = "signals"
    if not os.path.exists(signals_dir):
        os.makedirs(signals_dir)

    # Get a list of all files in the directory, sorted by modification time
    files = []
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                files.append(file_path)

    if len(files) == 0:
        return
    files = sorted(files, key=os.path.getmtime)

    data = []

    for filename in files:
        if filename.endswith('.txt'):
            data.append(np.loadtxt(filename))

    data = np.concatenate(data)
    for i, V in enumerate(data):
        data[i] = V * gain

    seconds = len(data) / 5024
    step = 0
    t = []
    save_time = datetime.now().strftime("%d.%m.%y_%H.%M.%S_")

    for i in range(len(data)):
        step += seconds / len(data)
        t.append(round(step, 4))

    if os.path.exists("full_signal.txt"):
        os.remove("full_signal.txt")
    with open("full_signal.txt", "a+") as file:
        for i, num in enumerate(data):
            file.write(str(t[i]) + '        ' + str(num) + '\n')

    with open(f"{signals_dir}/{save_time}_signal.txt", "a+") as file:
        for i, num in enumerate(data):
            file.write(str(t[i]) + '        ' + str(num) + '\n')
    print("Done")


def get_fft_data(noise_filter=True, sec=-1, gain=1):
    sec = float(sec)
    if sec == -1:
        data = np.loadtxt("adc_reader/thread_1.txt")
    else:
        data = []
        with open("full_signal.txt", "r") as data_file:
            # Parse the data as a time sequence
            for line in data_file:
                values = line.split()
                if len(values) == 2:
                    try:
                        t_val = float(values[0])
                        v_val = float(values[1])
                        if sec <= t_val:
                            data.append(v_val)
                        else:
                            continue
                    except ValueError:
                        # If the string cannot be converted to a float, skip it
                        continue
        data = np.array(data)

    data = data[:5000]
    for i, V in enumerate(data):
        data[i] = V * gain
    data = np.fft.fft(data)
    data = [abs(x) for x in data]

    data = data[:1000]

    if noise_filter:
        # Noise cutting
        s_fourier = 0
        for element in data:
            s_fourier += element
        if s_fourier < 5000:
            return None

    return data
