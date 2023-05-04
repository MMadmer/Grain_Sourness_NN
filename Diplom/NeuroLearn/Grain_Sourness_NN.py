import numpy as np
import os
import joblib
import time
import Logging as Log
import utils
import test


def get_weights(mod):
    main_dir = "the_best"

    if not os.path.exists(os.path.join(main_dir, mod)):
        return None
    model = joblib.load(os.path.join(main_dir, mod))

    return model


def main(mode=1, noise_filter=True, sec=-1):
    if mode == 1:
        log = Log.Logging(True, "working_logs/reg")
    elif mode == 2:
        log = Log.Logging(True, "working_logs/mlp")
    else:
        return

    log_categories = [
        "LogResult",
        "logStatus"
    ]

    log.log(log_categories[1], 1, "Model loading")
    if mode == 1:
        model = get_weights("reg_model.joblib")
    elif mode == 2:
        model = get_weights("mlp_model.joblib")
    else:
        log.log(log_categories[1], 2, "Incorrect mode")
        return

    if model is None:
        log.log(log_categories[0], 3, "Model not loaded")
        return
    log.log(log_categories[1], 1, "Done")

    log.log(log_categories[1], 1, "Loading data")
    data = np.array(utils.get_fft_data(noise_filter, sec)).reshape(1, -1)
    # data = np.array(test.main()).reshape(1, -1) # Filter test
    log.log(log_categories[1], 1, "Done")
    if None in data:
        log.log(log_categories[0], 1, "Noise")
        with open("result.txt", "a+") as file:
            file.seek(0, 2)
            file.write("-1" + '\n')
    elif len(data[0]) < 1000:
        log.log(log_categories[0], 1, f"Little data: {len(data)} of 1000")
    else:
        log.log(log_categories[1], 1, "Done")

        # make predictions on the new data
        y_pred = model.predict(data)

        if mode == 1:
            log.log(log_categories[0], 1, str(round(float(y_pred), 2)) + '%')

            with open(f"result.txt", "a+") as file:
                file.seek(0, 2)
                file.write(str(round(float(y_pred), 2)) + '\n')
        if mode == 2:
            classes = [0, 2, 4, 6, 8, 10]
            log.log(log_categories[1], 1, str(classes[int(y_pred) - 1]) + '%')

            with open(f"result.txt", "a+") as file:
                file.seek(0, 2)
                file.write(str(classes[int(y_pred) - 1]) + '\n')


if __name__ == "__main__":
    main()
