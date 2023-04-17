import numpy as np
import matplotlib.pyplot as plt
import subprocess
import psutil
import os


def launch_ADC():
    proc_name = "adc_reader.exe"

    for proc in psutil.process_iter(['name']):
        if proc.info["name"] == proc_name:
            print("Программа уже запущена")
            break
    else:
        subprocess.Popen(["start", "cmd", '/k', "adc_reader\\adc_reader.exe"], shell=True)


def show_signal():
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
    files = sorted(files, key=os.path.getmtime)

    data = []

    for filename in files:
        if filename.endswith('.txt'):
            data.append(np.loadtxt(filename))

    data = np.concatenate(data)

    step = 0
    t = []

    for i in range(len(data)):
        step += 1 / len(data)
        t.append(step)

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(t, data)
    ax.set_ylabel("V")
    ax.set_xlabel("t")
    fig.subplots_adjust(left=0.045, bottom=0.04, right=1.0, top=1.0)
    t.clear()
    plt.show()


def show_fourier():
    data = np.loadtxt("adc_reader/thread_1.txt")

    data = data[:5000]

    data = np.fft.fft(data)

    freq = 5000
    N = len(data)
    freq_step = [k * freq / N for k in range(N)]

    mags = [abs(x) for x in data]

    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=100)
    ax.plot(freq_step, mags)
    fig.subplots_adjust(left=0.025, bottom=0.02, right=1.0, top=1.0)
    plt.show()


def get_fft_data(noise_filter=True):
    data = np.loadtxt("adc_reader/thread_1.txt")
    data = data[:5000]
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
