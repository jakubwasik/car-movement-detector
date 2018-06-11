import glob
import os
import re
import shutil
from multiprocessing import Pool

import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt


def get_rotation_matrix(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    # print a,b
    dot = np.matmul(a, b)
    cross = np.cross(a, b)
    norm = lambda x: np.linalg.norm(x)
    G = np.array([[dot, -norm(cross), 0],
                  [norm(cross), dot, 0],
                  [0, 0, 1]])
    FFi = np.array([a, (b - dot * a) / norm(b - dot * a), np.cross(b, a)])
    FFi = np.transpose(FFi)
    return np.matmul(np.matmul(FFi, G), np.linalg.inv(FFi))


DATA_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed"
DATA_TEST_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed_test"
REF_DATA_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\ref_value"
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
OUT_TEST_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"


def rotate_train_matrix(file):
    date = re.search("_2018.*?_", file).group()[1:-1]
    ref_file = glob.glob(os.path.join(REF_DATA_FILE, "wartosc_referencyjna_{date}*".format(**locals())))
    if ref_file:
        ref_file = ref_file[0]
        data = pd.read_csv(file, sep=",")
        ref_data = pd.read_csv(ref_file, sep=",")
        data["x"] = (data["x"] - 0.042336469409452) * 1.003596269268205
        data["y"] = (data["y"] + 2.871617087981444e-04) * 1.007048491766642
        data["z"] = (data["z"] - 0.074352817371508) * 0.991392369049382
        ref_data["x"] = (ref_data["x"] - 0.042336469409452) * 1.003596269268205
        ref_data["y"] = (ref_data["y"] + 2.871617087981444e-04) * 1.007048491766642
        ref_data["z"] = (ref_data["z"] - 0.074352817371508) * 0.991392369049382
        ref_val = np.sqrt(ref_data["x"].mean() ** 2 + ref_data["y"].mean() ** 2 + ref_data["z"].mean() ** 2)
        # print ref_val
        rotation_matrix = get_rotation_matrix(
            np.array([ref_data["x"].mean(), ref_data["y"].mean(), ref_data["z"].mean()]),
            np.array([0, ref_val, 0]))
        np_data = data.as_matrix(["x", 'y', 'z'])
        for i in range(len(np_data)):
            np_data[i, :] = np.matmul(rotation_matrix, np_data[i, :])
            # result =  np.matmul(rotation_matrix, temp_arr)
            # data["x"][i] = result[0]
            # data["y"][i] = result[1]
            # data["z"][i] = result[2]
        new_data = pd.DataFrame(np_data, columns=['x', 'y', 'z'])
        new_data["time"] = data["time"]
        new_data = new_data[['time', 'x', 'y', 'z']]
        new_data.to_csv(os.path.join(OUT_FILE, os.path.basename(file)), index=False, sep=',')
    else:
        print "couldnt find ref file for: {file}".format(**locals())


def rotate_test_matrix(file):
    date = re.search("_2018.*?_", file).group()[1:-1]
    ref_file = glob.glob(os.path.join(REF_DATA_FILE, "wartosc_referencyjna_{date}*".format(**locals())))
    if ref_file:
        ref_file = ref_file[0]
        data = pd.read_csv(file, sep=",")
        ref_data = pd.read_csv(ref_file, sep=",")
        data["x"] = (data["x"] - 0.042336469409452) * 1.003596269268205
        data["y"] = (data["y"] + 2.871617087981444e-04) * 1.007048491766642
        data["z"] = (data["z"] - 0.074352817371508) * 0.991392369049382
        ref_data["x"] = (ref_data["x"] - 0.042336469409452) * 1.003596269268205
        ref_data["y"] = (ref_data["y"] + 2.871617087981444e-04) * 1.007048491766642
        ref_data["z"] = (ref_data["z"] - 0.074352817371508) * 0.991392369049382
        ref_val = np.sqrt(ref_data["x"].mean() ** 2 + ref_data["y"].mean() ** 2 + ref_data["z"].mean() ** 2)
        # print ref_val
        rotation_matrix = get_rotation_matrix(
            np.array([ref_data["x"].mean(), ref_data["y"].mean(), ref_data["z"].mean()]),
            np.array([0, ref_val, 0]))
        np_data = data.as_matrix(["x", 'y', 'z'])
        for i in range(len(np_data)):
            np_data[i, :] = np.matmul(rotation_matrix, np_data[i, :])
            # result =  np.matmul(rotation_matrix, temp_arr)
            # data["x"][i] = result[0]
            # data["y"][i] = result[1]
            # data["z"][i] = result[2]
        new_data = pd.DataFrame(np_data, columns=['x', 'y', 'z'])
        new_data["time"] = data["time"]
        new_data = new_data[['time', 'x', 'y', 'z']]
        new_data.to_csv(os.path.join(OUT_TEST_FILE, os.path.basename(file)), index=False, sep=',')
    else:
        print "couldnt find ref file for: {file}".format(**locals())


if __name__ == '__main__':
    # a = pd.read_csv(FILE, sep=";", names= ["time", "x", "y", "z"])
    if os.path.isdir(OUT_FILE):
        shutil.rmtree(OUT_FILE)
        os.makedirs(OUT_FILE)
    if os.path.isdir(OUT_TEST_FILE):
        shutil.rmtree(OUT_TEST_FILE)
        os.makedirs(OUT_TEST_FILE)

    TRAIN_FILES = glob.glob(os.path.join(DATA_FILE, "*2018*2018*"))
    p = Pool(4)
    p.map(rotate_train_matrix, TRAIN_FILES)
    p.close()
    p.join()

    TEST_FILES = glob.glob(os.path.join(DATA_TEST_FILE, "*2018*2018*"))
    p = Pool(4)
    p.map(rotate_test_matrix, TEST_FILES)
    p.close()
    p.join()

    for file in glob.glob(os.path.join(DATA_FILE, "*gps*")):
        print file
        shutil.copy2(file, OUT_FILE)

    for file in glob.glob(os.path.join(DATA_TEST_FILE, "*gps*")):
        print file
        shutil.copy2(file, OUT_TEST_FILE)
