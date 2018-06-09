import os
import threading
from datetime import datetime

import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
from sklearn import svm
from scipy.signal import butter, lfilter, freqz
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, cross_val_score
from scipy.fftpack import fft
from scipy.fftpack import fftfreq

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a
def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='highpass', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y
def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"
#FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\labeled_data"
#FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'

def features(filepath):
    i = 0
    tags = []
    events = []
    features = np.zeros((len(glob.glob(os.path.join(filepath, "*gps*"))), 40))
    for gps_file in glob.glob(os.path.join(filepath, "*gps*")):
        event, date = gps_file.split("_gps_")
        acc_file = glob.glob(os.path.join(filepath, "{event}_2018*{date}".format(**locals())))
        acc_data = pd.read_csv(acc_file[0], sep=",")
        gps_data = pd.read_csv(gps_file, sep=",")
        x = np.array(acc_data["x"])
        #x = butter_lowpass_filter(x, 5, 50)
        # x_new = butter_highpass_filter(x_new, 0.5, 50)

        # plt.figure(i)
        # plt.plot(x)
        # plt.plot(x_new, '-')
        # plt.show()
        # x = x_new

        z = np.array(acc_data["z"])
        #z = butter_lowpass_filter(z, 5, 50)
        # z_new = butter_highpass_filter(z_new, 7, 50)
        # z=z_new
        freq_x = np.abs(fft(x))
        freq_z = np.abs(fft(z))

        energy_x = x.sum()
        energy_z = z.sum()
        range_z = z.max() - z.min()
        range_x = x.max() - x.min()
        speed = np.array(gps_data["speed"])
        range_speed = speed.max() - speed.min()
        time = np.linspace(0, len(acc_data["time"]) * 0.02, len(acc_data["time"]))
        time_speed = np.linspace(0, len(gps_data["time"]) * 0.02, len(gps_data["time"]))
        coeff_x = np.polyfit(time, x, 4)
        coeff_z = np.polyfit(time, z, 3)
        coeff_speed = np.polyfit(time_speed, speed, 3)
        mean_x = np.mean(x)
        std_x = np.std(x)
        mean_z = np.mean(z)
        std_z = np.std(z)
        speed_mean = np.mean(speed)
        speed_std = np.std(speed)
        temp_features = np.array([mean_x, std_x, mean_z, std_z, speed_mean, speed_std, range_speed, energy_x, energy_z])
        temp_features = np.concatenate((temp_features, coeff_x, coeff_z, coeff_speed, freq_x[1:10], freq_z[1:10]))
        features[i] += temp_features
        tags.append(event.split("\\")[-1])
        events.append(acc_file)
        i += 1
    return {
        "features": features,
        "tags": tags,
        "events": events
    }
if __name__ == '__main__':
    retval = features(FILE)
    svr = svm.SVC()
    exponential_range = [pow(10, i) for i in range(-4, 1)]
    parameters = {'kernel': ['linear', 'rbf'], 'C': exponential_range, 'gamma': exponential_range}
    clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=False)
    clf.fit(retval["features"], retval["tags"])
    #   print 'Sprawnosc klasyfikatora:'
    #print scores
    test_retval = features(FILE_TEST)

    y = clf.predict(retval["features"])
    # print y, tags
    k = 0
    for i in range(len(y)):
        if y[i] != retval["tags"][i]:
            k += 1
            print "\nZLE SKLASYFIKOWANO: ", retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print k

    y1 = clf.predict(test_retval["features"])
    # print y, tags
    k = 0
    for i in range(len(y1)):
        if y1[i] != test_retval["tags"][i]:
            k += 1
            print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y1[i],
    print k
    scores = cross_val_score(clf, retval["features"], retval["tags"], cv=10, n_jobs=8, verbose=False)
    print scores