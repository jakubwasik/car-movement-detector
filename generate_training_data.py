import os
import threading
from datetime import datetime, timedelta
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
DATE_FORMAT_MS_LABELED = '%Y-%m-%d %H:%M:%S.%f'
DATE_FORMAT_FILE = '%Y-%m-%d-%H-%M-%S_'
DATE_FORMAT_FILE_second = '%Y-%m-%d_%H_%M_%S'
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\\normalized_data"
OUT_FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_raw_data_test"
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
LABELED_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_labeled_data"
WINDOW_SIZE = 5 * 50


def sliding_window(args):
    k = 0
    acc_data = pd.read_csv(args[0], sep=";", names=["time", "x", "y", "z"])
    gps_data = pd.read_csv(args[1], sep=";", names=["time", "latitude", "longitude", "speed"])
    acc_data["time"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in acc_data['time']]
    gps_data["time"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in gps_data['time']]
    labeled_event_data = pd.read_csv(os.path.join(LABELED_FILE, "events_" + os.path.basename(args[0])))
    labeled_event_data["start"] = [datetime.strptime(TIME, DATE_FORMAT_MS_LABELED) for TIME in
                                   labeled_event_data["start"]]
    labeled_event_data["stop"] = [datetime.strptime(TIME, DATE_FORMAT_MS_LABELED) for TIME in
                                  labeled_event_data["stop"]]
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for i in range(0, len(acc_data) - 600, 250):
        if i + WINDOW_SIZE >= len(acc_data):
            break
        elif i < 400:
            pass
        else:
            arr = {}
            start = gps_data["time"].searchsorted(acc_data["time"][i])[0]
            stop = gps_data["time"].searchsorted(acc_data["time"][i + WINDOW_SIZE])[0]
            for j in range(len(labeled_event_data)):
                # if event_data["event"][i] == labeled_event_data["event"][j]:
                if abs(labeled_event_data["start"][j] - acc_data["time"][i]) < timedelta(seconds=15):
                    # print abs(labeled_event_data["start"][j] - event_data["start"][i])
                    # print "CORR1: ", event_data["event"][i], event_data["start"][i], event_data["stop"][i]
                    # print "Z1: ", labeled_event_data["event"][j], labeled_event_data["start"][j], labeled_event_data["stop"][j]
                    # print
                    if labeled_event_data["start"][j] < acc_data["time"][i] and labeled_event_data["stop"][j] > \
                            acc_data["time"][i]:
                        arr[j] = min(labeled_event_data["stop"][j], acc_data["time"][i + WINDOW_SIZE]) - max(
                            labeled_event_data["start"][j], acc_data["time"][i])
                    elif acc_data["time"][i] < labeled_event_data["start"][j] and acc_data["time"][i + WINDOW_SIZE] > \
                            labeled_event_data["start"][j]:

                        arr[j] = min(labeled_event_data["stop"][j], acc_data["time"][i + WINDOW_SIZE]) - max(
                            labeled_event_data["start"][j], acc_data["time"][i + WINDOW_SIZE])
            if arr:
                # print arr
                # candidate = max(arr.values())
                # i_candidate = [key for key, value in arr.iteritems() if value == candidate][0]
                # to_save_acc = acc_data[i: i + WINDOW_SIZE]
                # to_save_acc.to_csv(
                #    os.path.join(OUT_FILE, labeled_event_data["event"][i_candidate] + "_"+acc_data["time"][i].strftime(DATE_FORMAT_FILE) + ".csv"),
                #    index=False)
                # to_save_gps = gps_data[start: stop]
                # to_save_gps.to_csv(os.path.join(OUT_FILE,
                pass
                #                                "gps_" + labeled_event_data["event"][i_candidate]  + "_"+ acc_data["time"][i].strftime(DATE_FORMAT_FILE) + ".csv"), index=False)
            else:
                k += 1
                if k % 4 == 0:
                    to_save_acc = acc_data[i: i + WINDOW_SIZE]
                    to_save_acc.to_csv(os.path.join(OUT_FILE,
                                                    "indle_" + acc_data["time"][i].strftime(DATE_FORMAT_FILE) +
                                                    acc_data["time"][i].strftime(DATE_FORMAT_FILE_second) + ".csv"),
                                       index=False)
                    to_save_gps = gps_data[start:stop]
                    to_save_gps.to_csv(os.path.join(OUT_FILE,
                                                    "indle_gps_" +
                                                    acc_data["time"][i].strftime(DATE_FORMAT_FILE_second) + ".csv"),
                                       index=False)


if __name__ == '__main__':
    start = datetime.now()
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(RAW_FILE, "raw*")):
        date = acc_file.split("_")[-1]
        gps_file = glob.glob(os.path.join(RAW_FILE, "gps_data_{0}*".format(date[:-6])))[0]
        args.append([acc_file, gps_file])
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
