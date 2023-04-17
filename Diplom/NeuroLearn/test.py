import numpy as np


def main():
    data = np.loadtxt("test.txt", usecols=1)
    data = np.fft.fft(data)
    data = [abs(x) for x in data]

    data = data[:1000]

    # Noise cutting
    s_fourier = 0
    for element in data:
        s_fourier += element
    print(s_fourier)
    if s_fourier < 5000:
        return None

    return data


if __name__ == "__main__":
    main()
