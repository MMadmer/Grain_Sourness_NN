import matplotlib.pyplot as plt
import os


def main():
    filt = 3
    file = f"proc_0"
    start_file = 1
    files = 50
    t = []
    V = []
    progress = 0
    folder = -2

    while folder < 10:
        folder += 2
        file = f"proc_{folder}"

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
                        # for j in range(11):
                        #     next(f)
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
                        f.close()

                    with open(file_path, 'w') as f:
                        for num, el in enumerate(V):
                            if el >= filt or el <= -filt:
                                V[num] = 0
                            f.write(str(t[num]) + "        " + str(V[num]) + '\n')
                        f.close()

                t.clear()
                V.clear()

            # Progress
            progress += 1 / 6 * 100  # 1 / (files - start_file + 1) * 100
            print("{:.2f}".format(progress), '%')


if __name__ == "__main__":
    main()
