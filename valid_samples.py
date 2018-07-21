import os
from datetime import datetime

import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
import re

FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_labeled_train_data"
test_file = r'C:\Users\kuba\Desktop\praca magisterska\sensor data\alligned_speed_test'
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
i=0
time = []
right = np.zeros((10,len(glob.glob(os.path.join(test_file,"*")))))
time = np.zeros(len(glob.glob(os.path.join(test_file,"*lewy_2*"))))

for file in glob.glob(os.path.join(FILE,"zmia*prawy_20*")):
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
    #plt.figure(i)
    plt.grid()
    plt.plot(time, data["x"])
    plt.title(os.path.basename(file))
    plt.xlabel('czas [s]')
    #plt.ylim(-4.5,4.5)
    plt.ylabel('przyspieszenie [m/s^2]')
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
    p = np.poly1d(np.polyfit(time, data["x"], 3))
    plt.plot(time, p(time), color ='red')

    plt.show()
    #magnitude = np.sqrt(np.square(x) + np.square(z))

#print time.mean()
"""
lewy_total = len(glob.glob(os.path.join(FILE,"*lewy_2018*")))
prawy_total = len(glob.glob(os.path.join(FILE,"*prawy_2018*")))
prawo_total = len(glob.glob(os.path.join(FILE,"*prawo_2018*")))
lewo_total = len(glob.glob(os.path.join(FILE,"*lewo_2018*")))
hamowanie_total = len(glob.glob(os.path.join(FILE,"hamowanie_2018*")))
zatrzymanie_total = len(glob.glob(os.path.join(FILE,"za*ch_2018*")))
przyspieszanie_total= len(glob.glob(os.path.join(FILE,"p*ch_2018*")))
indle_total= len(glob.glob(os.path.join(FILE,"indle_2018*")))
objects = ('skret\nw\nlewo', 'skret\nw\nprawo', 'zmiana\npasa\nna\nlewy', 'zmiana\npasa\nna\nprawy', 'hamowanie', 'zatrzymanie', "przyspieszanie", "bez\nmanewru")
y_pos = np.arange(len(objects))
performance = [lewo_total, prawo_total, lewy_total, prawy_total, hamowanie_total, zatrzymanie_total, przyspieszanie_total, indle_total]
fig, ax = plt.subplots()
ax.bar(y_pos, performance, align='center', alpha=.7)
for i, v in enumerate(performance):
    ax.text(v + 3, i + .25, str(v), color='red', fontweight='bold')
plt.xticks(y_pos, objects)
plt.ylabel('ilosc manewrow')



plt.show()
"""