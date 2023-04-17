import os
import random


def shuffle(dir_path="Selection_proc_0", file_format="txt"):
    # Get a list of file names in the directory
    file_names = [f for f in os.listdir(dir_path) if f.endswith(f'.{file_format}')]

    # Shuffle the file names
    random.shuffle(file_names)

    # Rename the files in the new order
    # progress = 0
    # progress_step = 0
    for i, file_name in enumerate(file_names, start=1):
        # Creating buffer paths
        new_file = f"{i}.{file_format}"

        if file_name == new_file:
            continue

        old_path = os.path.join(dir_path, file_name)
        new_path = os.path.join(dir_path, new_file)
        temp_name = f"temp.{file_format}"
        temp_path = os.path.join(dir_path, temp_name)

        # Rename files
        os.rename(new_path, temp_path)
        os.rename(old_path, new_path)
        os.rename(temp_path, old_path)

        # # Progress
        # progress += 1 / len(file_names) * 100
        # if progress - progress_step >= 0:
        #     progress_step += 5
        #     print("{:.2f}".format(progress), "%")
    print(f"{dir_path} done")


if __name__ == "__main__":
    shuffle()
