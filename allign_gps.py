import os
from multiprocessing import Pool

import pandas as pd
import glob
import shutil
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\\labeled_data"
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed"
TEST_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
TEST_OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed_test"

def allign_train_gps(file):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(OUT_FILE, os.path.basename(file)), sep=",")

def allign_test_gps(file):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(TEST_OUT_FILE, os.path.basename(file)), sep=",")
if __name__ == '__main__':
    if os.path.isdir(OUT_FILE):
        shutil.rmtree(OUT_FILE)
        os.makedirs(OUT_FILE)
    if os.path.isdir(TEST_OUT_FILE):
        shutil.rmtree(TEST_OUT_FILE)
        os.makedirs(TEST_OUT_FILE)

    GPS_TRAIN_FILES = glob.glob(os.path.join(FILE, "*gps*"))
    p = Pool(4)
    p.map(allign_train_gps, GPS_TRAIN_FILES)
    p.close()
    p.join()

    for file in glob.glob(os.path.join(FILE, "*2018*2018*")):
        shutil.copy2(file, OUT_FILE)

    GPS_TEST_FILES = glob.glob(os.path.join(TEST_FILE, "*gps*"))
    p = Pool(4)
    p.map(allign_test_gps, GPS_TEST_FILES)
    p.close()
    p.join()

    for file in glob.glob(os.path.join(TEST_FILE, "*2018*2018*")):
        shutil.copy2(file, TEST_OUT_FILE)


