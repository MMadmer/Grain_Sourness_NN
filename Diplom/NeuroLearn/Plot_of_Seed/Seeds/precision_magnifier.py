import os


def main(main_file):
    start_file = 1
    files = 45
    directory = "proc_0"

    for i in range(start_file, files + 1):
        time = 0.0002
        t = []
        V = []
        head = []
        file_path = f'{directory}/{i}.txt'

        if not os.path.exists(file_path):
            print(f"The file {file_path} does not exist.")
        else:
            with open(file_path, 'r') as f:
                # Parse the data as a time sequence
                for line in f:
                    values = line.split()
                    if len(values) == 2:
                        try:
                            t_val = float(values[0])
                            time += 0.0002
                            t_val = time
                            v_val = float(values[1])
                            t.append(t_val)
                            V.append(v_val)
                        except ValueError:
                            # If the string cannot be converted to a float, skip it
                            head.append(line)
                            continue
                    else:
                        head.append(line)
            f.close()

            with open(file_path, 'w') as f:
                for line in head:
                    f.write(line)

                for line in range(len(t)):
                    f.write("        {:.4f}        {:.3f}\n".format(t[line], V[line]))
            f.close()

        # Progress
        print(file_path)


if __name__ == "__main__":
    main("1.txt")

