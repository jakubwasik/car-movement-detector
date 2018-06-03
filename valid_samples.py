import os
from datetime import datetime

import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import re

FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\labeled_data"
test_file = r'C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed_test'
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
i=0
time = []
right = np.zeros((10,len(glob.glob(os.path.join(test_file,"*")))))
time = np.zeros(len(glob.glob(os.path.join(test_file,"*lewy_2*"))))
for file in glob.glob(os.path.join(FILE,"*lewy_2018*")):
    print file
    #regex = re.sub("za.*ch", "zatrzymanie_na_swiatlach",string=file)
    #print regex
    #os.rename(file, regex)
    data = pd.read_csv(file, sep=",")
    #obj = glob.glob(os.path.join(test_file, os.path.basename(file)))[0]
    #alligned_data = pd.read_csv(obj, sep=",")
    x = np.array(data["x"])
    #z = np.array(data["z"])
    #time[i]=len(x) * 0.02
    time = np.linspace(0, len(data["time"]) * 0.02, len(data["time"]))
    plt.figure(i)
    plt.plot(time, data["x"])
    plt.title(file)
    # plt.title(file)
    #alligned_data["x"].plot()
    #data["x"].plot()
    #freq_x = fft(x)
    #freq = fftfreq(x.size, 0.02)
    #spectral_energy = np.sum(np.abs(freq_x)**2)
    #print spectral_energy
    #plt.figure(i)
    #plt.title(file)

    #coeff_x = np.polyfit(time, data["z"], 3)
    #coeff_z = np.polyfit(time, data["z"], 3)
    #i+=1
    #p = np.poly1d(np.polyfit(time, data["x"], 3))
    #plt.plot(time, p(time))

    plt.show()
    #magnitude = np.sqrt(np.square(x) + np.square(z))

#print time.mean()
