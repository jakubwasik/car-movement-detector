import os
import pandas as pd
import glob
import shutil
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\\labeled_data"
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed"
TEST_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
TEST_OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed_test"
if os.path.isdir(OUT_FILE):
    shutil.rmtree(OUT_FILE)
    os.makedirs(OUT_FILE)
if os.path.isdir(TEST_OUT_FILE):
    shutil.rmtree(TEST_OUT_FILE)
    os.makedirs(TEST_OUT_FILE)
for file in glob.glob(os.path.join(FILE,"*gps*")):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            print prev_speed, file
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(OUT_FILE, os.path.basename(file)), sep=",")

for file in glob.glob(os.path.join(FILE,"*2018*2018*")):
    print file
    shutil.copy2(file, OUT_FILE)

for file in glob.glob(os.path.join(TEST_FILE,"*gps*")):
    data = pd.read_csv(file, sep=",", index_col=False)
    prev_speed = data["speed"][0]
    for i in range(len(data["speed"])):
        if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
            print prev_speed, file
            data["speed"][i] = prev_speed
        prev_speed = data["speed"][i]
    data.to_csv(os.path.join(TEST_OUT_FILE, os.path.basename(file)), sep=",")

for file in glob.glob(os.path.join(TEST_FILE,"*2018*2018*")):
    print file
    shutil.copy2(file, TEST_OUT_FILE)


