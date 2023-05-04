import os

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

    time_dur = 0

    folders = range(0, 12, 2)
    for folder in folders:
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

        for i in range(len(pol_sig_start)):
            time_dur += pol_sig_end[i] - pol_sig_start[i]

    print(time_dur)


if __name__ == "__main__":
    main()
