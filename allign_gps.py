import os
from multiprocessing import Pool

import pandas as pd
import glob
import shutil

import config


def allign_train_gps(file):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(config.ALLIGNED_SPEED, os.path.basename(file)), sep=",")

def allign_test_gps(file):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(config.ALLIGNED_SPEED_TEST, os.path.basename(file)), sep=",")
if __name__ == '__main__':
    if os.path.isdir(config.ALLIGNED_SPEED):
        shutil.rmtree(config.ALLIGNED_SPEED)
        os.makedirs(config.ALLIGNED_SPEED)
    if os.path.isdir(config.ALLIGNED_SPEED_TEST):
        shutil.rmtree(config.ALLIGNED_SPEED_TEST)
        os.makedirs(config.ALLIGNED_SPEED_TEST)

    GPS_TRAIN_FILES = glob.glob(os.path.join(config.DNT_LABELED_DATA, "*gps*"))
    p = Pool(4)
    p.map(allign_train_gps, GPS_TRAIN_FILES)
    p.close()
    p.join()

    for file in glob.glob(os.path.join(config.DNT_LABELED_DATA, "*2018*2018*")):
        shutil.copy2(file, config.ALLIGNED_SPEED)

    GPS_TEST_FILES = glob.glob(os.path.join(config.DNT_TEST_DATA, "*gps*"))
    p = Pool(4)
    p.map(allign_test_gps, GPS_TEST_FILES)
    p.close()
    p.join()

    for file in glob.glob(os.path.join(config.DNT_TEST_DATA, "*2018*2018*")):
        shutil.copy2(file, config.ALLIGNED_SPEED_TEST)


