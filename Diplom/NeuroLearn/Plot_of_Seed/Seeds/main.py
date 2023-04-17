import matplotlib.pyplot as plt
import os


def main():
    file = f"proc_2"
    start_file = 21
    files = 45
    t = []
    V = []
    progress = 0
    # folder = -2

    # while (folder < 10):
    # folder += 2
    # file = f"proc_{folder}"

    if not os.path.exists(file):
        print(f"The folder {file} does not exist.")
    else:
        for i in range(start_file, files + 1):
            file_path = f'{file}/{i}.txt'
            if not os.path.exists(file_path):
                print(f"The file {file_path} does not exist.")
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

            # Progress
            progress += 1 / (files - start_file + 1) * 100
            print("{:.2f}".format(progress), '%')


if __name__ == "__main__":
    main()
