import os
import threading
from datetime import datetime
from multiprocessing import Pool

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

FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"
# FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\labeled_data"
# FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_raw_data"
OUT_FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_raw_data_test"
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
WINDOW_SIZE = 5 * 50


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


def features(filepath):
    i = 0
    tags = []
    events = []
    features = np.zeros((len(glob.glob(os.path.join(filepath, "*gps*"))), 38))
    for gps_file in glob.glob(os.path.join(filepath, "*gps*")):
        event, date = gps_file.split("_gps_")
        acc_file = glob.glob(os.path.join(filepath, "{event}_2018*{date}".format(**locals())))
        acc_data = pd.read_csv(acc_file[0], sep=",")
        gps_data = pd.read_csv(gps_file, sep=",")
        x = np.array(acc_data["x"])
        # x = butter_lowpass_filter(x, 5, 50)
        # x_new = butter_highpass_filter(x_new, 0.5, 50)

        # plt.figure(i)
        # plt.plot(x)
        # plt.plot(x_new, '-')
        # plt.show()
        # x = x_new

        z = np.array(acc_data["z"])
        # z = butter_lowpass_filter(z, 5, 50)
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
        coeff_x = np.polyfit(time, x, 2)
        coeff_x_1 = np.polyfit(time, x, 1)
        coeff_z = np.polyfit(time, z, 2)
        coeff_speed = np.polyfit(time_speed, speed, 2)
        mean_x = np.mean(x)
        std_x = np.std(x)
        mean_z = np.mean(z)
        std_z = np.std(z)
        var_x = np.var(x)
        var_z = np.var(z)
        speed_mean = np.mean(speed)
        speed_std = np.std(speed)
        temp_features = np.array(
            [mean_x, std_x, mean_z, std_z, speed_mean, speed_std, range_speed, energy_x, energy_z])
        temp_features = np.concatenate((temp_features, coeff_x, coeff_z,coeff_x_1, coeff_speed, freq_x[1:10], freq_z[1:10]))
        features[i] += temp_features
        tags.append(event.split("\\")[-1])
        events.append(acc_file)
        i += 1
    return {
        "features": features,
        "tags": tags,
        "events": events
    }


def features_from_window(acc_data, gps_data):
    i = 0
    tags = []
    events = []
    x = np.array(acc_data["x"])
    # x = butter_lowpass_filter(x, 5, 50)
    # x_new = butter_highpass_filter(x_new, 0.5, 50)

    # plt.figure(i)
    # plt.plot(x)
    # plt.plot(x_new, '-')
    # plt.show()
    # x = x_new
    z = np.array(acc_data["z"])
    # z = butter_lowpass_filter(z, 5, 50)
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
    coeff_x = np.polyfit(time, x, 2)
    coeff_x_1 = np.polyfit(time, x, 1)
    coeff_z = np.polyfit(time, z, 2)
    coeff_speed = np.polyfit(time_speed, speed, 2)
    mean_x = np.mean(x)
    std_x = np.std(x)
    mean_z = np.mean(z)
    std_z = np.std(z)
    speed_mean = np.mean(speed)
    speed_std = np.std(speed)
    features = np.array(
        [mean_x, std_x, mean_z, std_z, speed_mean, speed_std, range_speed, energy_x, energy_z])
    features = np.concatenate((features, coeff_x, coeff_z,coeff_x_1,  coeff_speed, freq_x[1:10], freq_z[1:10]))
    return features.reshape(1, -1)


def sliding_window(args):
    acc_data = pd.read_csv(args[1], sep=";", names=["time", "x", "y", "z"])
    gps_data = pd.read_csv(args[2], sep=";", names=["time", "latitude", "longitude", "speed"])
    acc_data["time"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in acc_data['time']]
    gps_data["time"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in gps_data['time']]
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for i in range(0, len(acc_data) - 600, 100):
        if i + WINDOW_SIZE >= len(acc_data):
            break
        elif i < 400:
            pass
        else:
            start = gps_data["time"].searchsorted(acc_data["time"][i])[0]
            stop = gps_data["time"].searchsorted(acc_data["time"][i + WINDOW_SIZE])[0]
            # print "test: "
            # print acc_data["time"][i], gps_data["time"][start]
            # print acc_data["time"][i + WINDOW_SIZE], gps_data["time"][stop]
            features = features_from_window(acc_data[i:i + WINDOW_SIZE], gps_data[start:stop])
            event = args[0].predict(features)[0]
            print event
            # print [acc_data["time"][i].strftime(DATE_FORMAT_MS), acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS), event]
            results = results.append(pd.DataFrame(data=[[acc_data["time"][i].strftime(DATE_FORMAT_MS),
                                                         acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS),
                                                         event]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(OUT_FILE_TEST, "events_" + os.path.basename(args[3])), index=False)


if __name__ == '__main__':
    start= datetime.now()
    retval = features(FILE)
    svr = svm.SVC()
    exponential_range = [pow(10, i) for i in range(-4, 1)]
    parameters = {'kernel': ['linear', 'rbf'], 'C': exponential_range, 'gamma': exponential_range}
    clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=True)
    clf.fit(retval["features"], retval["tags"])
    # scores = cross_val_score(clf, retval["features"], retval["tags"], cv=10, n_jobs=8, verbose=False)
    # print scores
    #   print 'Sprawnosc klasyfikatora:'
    # print scores
    # test_retval = features(FILE_TEST)
    y = clf.predict(retval["features"])
    # print y, tags
    k = 0
    for i in range(len(y)):
        if y[i] != retval["tags"][i]:
            k += 1
            print "\nZLE SKLASYFIKOWANO: ", retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print k
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(RAW_FILE, "raw_data_2018-05-30*")):
        print acc_file
        date = acc_file.split("_")[-1]
        gps_file = glob.glob(os.path.join(RAW_FILE, "gps_data_{0}*".format(date[:-6])))[0]
        args.append([clf, acc_file, gps_file, acc_file])
    print args
    pool.map(sliding_window, args)
    print datetime.now() - start
    # sliding_window(acc_file=acc_file, gps_file=gps_file)

"""
    

    y = clf.predict(retval["features"])     
    # print y, tags
    k = 0
    for i in range(len(y)):
        if y[i] != retval["tags"][i]:
            k += 1
            print "\nZLE SKLASYFIKOWANO: ", retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
"""