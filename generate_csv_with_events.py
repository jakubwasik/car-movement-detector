import glob
import os
import pandas as pd
from datetime import datetime, timedelta

DATE_FORMAT_FILE = '%Y-%m-%d_%H_%M_%S'
DATE_FORMAT_MS = '%Y-%m-%d %H:%M:%S.%f'
DATE_FORMAT_MS_RAW = '%d-%m-%Y %H:%M:%S:%f'
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
RAW_EVENTS_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_raw_data"
LABELED_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_labeled_data"
k=0
all=0
for event_file in glob.glob(os.path.join(LABELED_FILE, "*")):
    event_data = pd.read_csv(event_file)
    event_data["start"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in event_data["start"]]
    event_data["stop"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in event_data["stop"]]
    for i in range(len(event_data)):
        raw_event_data = pd.read_csv(os.path.join(RAW_EVENTS_FILE, os.path.basename(event_file)))
        raw_event_data["start"] = [datetime.strptime(TIME, DATE_FORMAT_MS_RAW) for TIME in raw_event_data["start"]]
        raw_event_data["stop"] = [datetime.strptime(TIME, DATE_FORMAT_MS_RAW) for TIME in raw_event_data["stop"]]
        for j in range(len(raw_event_data)):
            if event_data["event"][i] == raw_event_data["event"][j]:
                if raw_event_data["start"][j] - event_data["start"][i] > timedelta(seconds=0) and raw_event_data["start"][j] - event_data["start"][i] < event_data["stop"][i] - event_data["start"][i] - timedelta(seconds=2):
                    #print "CORR1: ", event_data["event"][i], event_data["start"][i], event_data["stop"][i]
                    #print "Z1: ", raw_event_data["event"][j], raw_event_data["start"][j], raw_event_data["stop"][j]
                    k+=1
                    event_data["event"][i] +=  "_OK"
                    break
                elif  event_data["start"][i] - raw_event_data["start"][j] > timedelta(seconds=0) and event_data["start"][i] - raw_event_data["start"][j] <  timedelta(seconds=3):
                    #rint "CORR2: ", event_data["event"][i], event_data["start"][i], event_data["stop"][i]
                    #print "Z2: ", raw_event_data["event"][j], raw_event_data["start"][j], raw_event_data["stop"][j]
                    k += 1
                    event_data["event"][i] +=  "_OK"
                    break
        all += 1
    #event_data.to_csv(event_file, index=False)


print float(k)/float(all)

