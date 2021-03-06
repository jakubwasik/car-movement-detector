import glob
import os

import numpy
import pandas as pd
from datetime import datetime, timedelta
import getpass
if getpass.getuser() == "PHVD86":
    import config_mot as config
else:
    import config

def get_success_rate_from_labeled_events((event_file, queue)):
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
    total_results_binary = {
        "zatrzymanie_na_swiatlach": 0,
        "przyspieszanie_na_swiatlach": 0,
        "indle": 0,
        "skret_w_lewo": 0,
        "skret_w_prawo": 0,
        "hamowanie": 0,
        "zmiana_pasa_na_prawy": 0,
        "zmiana_pasa_na_lewy": 0
    }
    results_binary = {
        "zatrzymanie_na_swiatlach": 0,
        "przyspieszanie_na_swiatlach": 0,
        "indle": 0,
        "skret_w_lewo": 0,
        "skret_w_prawo": 0,
        "hamowanie": 0,
        "zmiana_pasa_na_prawy": 0,
        "zmiana_pasa_na_lewy": 0
    }
    k = 0
    all = 0
    k_binary = 0
    all_binary = 0
    actual = []
    predicted = []
    event_data = pd.read_csv(event_file)
    event_data["start"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS_EVENT) for TIME in event_data["start"]]
    event_data["stop"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS_EVENT) for TIME in event_data["stop"]]
    raw_event_data = pd.read_csv(os.path.join(config.EVENTS_F_R_DATA_TEST, os.path.basename(event_file)))
    raw_event_data["start"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in raw_event_data["start"]]
    raw_event_data["stop"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in raw_event_data["stop"]]
    for i in range(len(event_data)):
        total_results[event_data["event"][i]] += 1
        total_results_binary[event_data["event"][i]] += 1
        windows_length = event_data["stop"][i] - event_data["start"][i]
        # print "NEW EVENT:" , windows_length
        arr = {}
        # print "test"
        # print event_data["event"][i]
        for j in range(len(raw_event_data)):
            # if event_data["event"][i] == labeled_event_data["event"][j]:
            if abs(raw_event_data["start"][j] - event_data["start"][i]) < timedelta(seconds=15):
                # print abs(labeled_event_data["start"][j] - event_data["start"][i])
                # print "CORR1: ", event_data["event"][i], event_data["start"][i], event_data["stop"][i]
                # print "Z1: ", labeled_event_data["event"][j], labeled_event_data["start"][j], labeled_event_data["stop"][j]
                # print
                if raw_event_data["start"][j] < event_data["start"][i] and raw_event_data["stop"][j] > \
                        event_data["start"][i]:
                    arr[j] = min(raw_event_data["stop"][j], event_data["stop"][i]) - max(
                        raw_event_data["start"][j], event_data["start"][i])
                elif event_data["start"][i] < raw_event_data["start"][j] and event_data["stop"][i] > \
                        raw_event_data["start"][j]:

                    arr[j] = min(raw_event_data["stop"][j], event_data["stop"][i]) - max(
                        raw_event_data["start"][j], event_data["start"][i])
            else:
                # pass
                if arr:
                    break
        if arr:
            # print arr
            candidate = max(arr.values())
            i_candidate = [key for key, value in arr.iteritems() if value == candidate][0]
            if raw_event_data["event"][i_candidate] == event_data["event"][i]:
                k += candidate.total_seconds() / config.WINDOW_SIZE if windows_length > candidate else 1
                k_binary += 1
                results[event_data["event"][
                    i]] += candidate.total_seconds() / config.WINDOW_SIZE if windows_length > candidate else 1
                results_binary[event_data["event"][i]] += 1
                # print "OK: ", event_data["event"][i], candidate.total_seconds() / WINDOW_SIZE if windows_length > candidate else 1
                # event_data["event"][i] += "_OK"
                actual.append(event_data["event"][i])
                predicted.append(raw_event_data["event"][i_candidate])
            else:
                counter = 0
                for key in arr.keys():

                    if arr[key] > timedelta(seconds=numpy.floor(config.WINDOW_SIZE / 2.0)) and \
                            raw_event_data["event"][key] == event_data["event"][i]:
                        k += arr[key].total_seconds() / config.WINDOW_SIZE if windows_length > arr[key] else 1
                        k_binary += 1
                        results[event_data["event"][i]] += arr[
                                                               key].total_seconds() / config.WINDOW_SIZE if windows_length > \
                                                                                                            arr[
                                                                                                                key] else 1
                        results_binary[event_data["event"][i]] += 1
                        actual.append(event_data["event"][i])
                        predicted.append(raw_event_data["event"][key])
                        # print "TEST: ", event_data["event"][i], arr[key].total_seconds() / WINDOW_SIZE if windows_length > arr[key] else 1
                        # event_data["event"][i] += "_OK"
                        break
                    else:
                        counter += 1
                if counter == len(arr.keys()):
                    actual.append(event_data["event"][i])
                    predicted.append(raw_event_data["event"][i_candidate])
                # print event_data["event"][i],  labeled_event_data["event"][i_candidate]
            # print labeled_event_data["event"][i_candidate]

        all += 1
        all_binary += 1
        # event_data.to_csv(os.path.join(LABELED_FILE, os.path.basename(event_file)), index=False)
       # print "SUCCESS RATE: ", float(k_binary) / float(all_binary)
       # print results_binary
       # print total_results_binary
       # for key in results_binary:
       #     if total_results_binary[key] != 0:
       #         print key, float(results_binary[key]) / float(total_results_binary[key])
    print "SUMMARY (CPOS):", len(event_data), len(actual), len(predicted)
    results_binary.update({"events": k_binary,
                    "all_events": all})
    queue.put([results_binary, total_results_binary,actual,predicted])
##print float(k) / float(all)
# print results
# print total_results
# for key in results:
#    if total_results[key] != 0:
#        print key, float(results[key]) / float(total_results[key])

# print all
