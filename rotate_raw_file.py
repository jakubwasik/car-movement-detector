import glob
import os
import re

import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt


def get_rotation_matrix(a, b):
    a = a/ np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    #print a,b
    dot = np.matmul(a,b)
    cross = np.cross(a,b)
    norm = lambda x: np.linalg.norm(x)
    G = np.array([[dot, -norm(cross), 0],
                  [norm(cross), dot, 0],
                  [0, 0, 1]])
    FFi = np.array([a, (b-dot*a)/norm(b-dot*a), np.cross(b,a)])
    FFi = np.transpose(FFi)
    return np.matmul(np.matmul(FFi, G),np.linalg.inv(FFi))


DATA_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
REF_DATA_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\ref_value"
# a = pd.read_csv(FILE, sep=";", names= ["time", "x", "y", "z"])

file = os.path.join(DATA_FILE, "raw_data_2018-06-02-20-24-11.csv")
ref_file = os.path.join(REF_DATA_FILE, "wartosc_referencyjna_2018-06-02-20-23-56_2018-06-02_20_24_12.csv")
data = pd.read_csv(file, sep=";", names= ["time", "x", "y", "z"])
ref_data = pd.read_csv(ref_file, sep=",")
data["x"] = (data["x"] - 0.042336469409452) * 1.003596269268205
data["y"] = (data["y"] + 2.871617087981444e-04) * 1.007048491766642
data["z"] = (data["z"] - 0.074352817371508) * 0.991392369049382
ref_data["x"] = (ref_data["x"] - 0.042336469409452) * 1.003596269268205
ref_data["y"] = (ref_data["y"] + 2.871617087981444e-04) * 1.007048491766642
ref_data["z"] = (ref_data["z"] - 0.074352817371508) * 0.991392369049382
ref_val = np.sqrt(ref_data["x"].mean() ** 2 + ref_data["y"].mean() ** 2 + ref_data["z"].mean() ** 2)
print ref_val
rotation_matrix = get_rotation_matrix(np.array([ref_data["x"].mean(), ref_data["y"].mean(), ref_data["z"].mean()]),
                                      np.array([0, ref_val, 0]))
np_data = data.as_matrix(["x", 'y', 'z'])
for i in range(len(np_data)):
    np_data[i, :] = np.matmul(rotation_matrix, np_data[i, :])
new_data = pd.DataFrame(np_data, columns=['x', 'y', 'z'])
new_data["time"] = data["time"]
new_data = new_data[['time', 'x', 'y', 'z']]
new_data.to_csv(file, index=False, header=False, sep=';')

