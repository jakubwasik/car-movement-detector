import glob
import os

import numpy
import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler

import config



def get_success_rate_from_raw_events():
    print "### START OF CALCULATING SUCCESS RATE FROM RAW EVENTS ###"
    k = 0
    all = 0
    total_results = {
        "zatrzymanie_na_swiatlach": 0,
        "przyspieszanie_na_swiatlach": 0,
        "indle": 0,
        "skret_w_lewo": 0,
        "skret_w_prawo": 0,
        "hamowanie": 0,
        "zmiana_pasa_na_prawy": 0,
        "zmiana_pasa_na_lewy": 0
    }
    results = {
        "zatrzymanie_na_swiatlach": 0,
        "przyspieszanie_na_swiatlach": 0,
        "indle": 0,
        "skret_w_lewo": 0,
        "skret_w_prawo": 0,
        "hamowanie": 0,
        "zmiana_pasa_na_prawy": 0,
        "zmiana_pasa_na_lewy": 0
    }
    for event_file in glob.glob(os.path.join(config.EVENTS_F_R_DATA_TEST, "*")):
        event_data = pd.read_csv(event_file)
        event_data["start"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in event_data["start"]]
        event_data["stop"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in event_data["stop"]]
        labeled_event_data = pd.read_csv(os.path.join(config.EVENTS_F_L_DATA_TEST, os.path.basename(event_file)))
        labeled_event_data["start"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS_EVENT) for TIME in
                                       labeled_event_data["start"]]
        labeled_event_data["stop"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS_EVENT) for TIME in
                                      labeled_event_data["stop"]]
        for i in range(len(event_data)):
            total_results[event_data["event"][i]] += 1
            arr = {}
            # print "test"
            # print event_data["event"][i]
            for j in range(len(labeled_event_data)):
                # if event_data["event"][i] == labeled_event_data["event"][j]:
                if abs(labeled_event_data["start"][j] - event_data["start"][i]) < timedelta(seconds=15):
                    # print abs(labeled_event_data["start"][j] - event_data["start"][i])
                    # print "CORR1: ", event_data["event"][i], event_data["start"][i], event_data["stop"][i]
                    # print "Z1: ", labeled_event_data["event"][j], labeled_event_data["start"][j], labeled_event_data["stop"][j]
                    # print
                    if labeled_event_data["start"][j] < event_data["start"][i] and labeled_event_data["stop"][j] > \
                            event_data["start"][i]:
                        arr[j] = min(labeled_event_data["stop"][j], event_data["stop"][i]) - max(
                            labeled_event_data["start"][j], event_data["start"][i])
                    elif event_data["start"][i] < labeled_event_data["start"][j] and event_data["stop"][i] > \
                            labeled_event_data["start"][j]:

                        arr[j] = min(labeled_event_data["stop"][j], event_data["stop"][i]) - max(
                            labeled_event_data["start"][j], event_data["start"][i])
            if arr:
                # print arr
                candidate = max(arr.values())
                i_candidate = [key for key, value in arr.iteritems() if value == candidate][0]
                if labeled_event_data["event"][i_candidate] == event_data["event"][i]:
                    k += 1
                    results[event_data["event"][i]] += 1
                    # print event_data["event"][i]
                    # event_data["event"][i] += "_OK"
                elif candidate < timedelta(seconds=3) and event_data["event"][i] == "indle":
                    k += 1
                    results[event_data["event"][i]] += 1
                    # event_data["event"][i] += "_OK"
                else:
                    for index in arr.keys():
                        if arr[index] > timedelta(seconds=numpy.floor(config.WINDOW_SIZE / 2.0)) and \
                                event_data["event"][i] == labeled_event_data["event"][index]:
                            k += 1
                            results[event_data["event"][i]] += 1
                            # event_data["event"][i] += "_OK"
                            break
            else:
                if event_data["event"][i] == "indle":
                    results[event_data["event"][i]] += 1
                    # event_data["event"][i] += "_OK"
                    k += 1
                    # print "No candidate"
            all += 1
        # event_data.to_csv(os.path.join(OUT_FILE, os.path.basename(event_file)), index=False)
    print "\nSUCCESS RATE ALL EVENTS: ", float(k) / float(all)

    print results
    print total_results
    for key in results:
        print key, float(results[key]) / float(total_results[key])
    print "### END OF CALCULATING SUCCESS RATE FROM RAW EVENTS ###"



