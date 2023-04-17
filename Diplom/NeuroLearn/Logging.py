from datetime import datetime
import os


class Logging:
    def __init__(self, ENABLE_LOGGING, path="logs"):
        self.ENABLE_LOGGING = ENABLE_LOGGING
        self.log_time = datetime.now().strftime("%d.%m.%y_%H.%M.%S_")
        self.path = path
        if not os.path.exists(self.path):
            os.makedirs(self.path)

    def log(self, log_category, log_type, data):
        if not self.ENABLE_LOGGING:
            return

        log_types = {
            1: "\nDefault\n",
            2: "\nWarning!\n",
            3: "\nERROR!\n"
        }

        current_time = datetime.now()
        current_time = current_time.strftime("%d:%m:%y %H:%M:%S ")

        with open(f"{self.path}/{self.log_time}_log.txt", "a+") as file:
            file.seek(0, 2)
            try:
                file.write(log_types[log_type])
                file.write(current_time + ": " + log_category + ": " + str(data))
                print(log_types[log_type] + log_category + ": " + str(data))
            except Exception as ex:
                file.write(log_types[log_type])
                file.write(current_time + log_category + ": " + "Logging error: " + str(ex))
                print(log_types[log_type] + log_category + ": " + "Logging error: " + str(ex))
