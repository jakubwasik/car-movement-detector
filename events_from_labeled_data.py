import glob
import os
import pandas as pd
from datetime import datetime

DATE_FORMAT_FILE = '%Y-%m-%d_%H_%M_%S'
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\events_from_labeled_data_test"
i=0
for acc_file in glob.glob(os.path.join(RAW_FILE, "raw_data*")):
    acc_data = pd.read_csv(acc_file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(acc_data["time"][0], DATE_FORMAT_MS)
    stop = datetime.strptime(acc_data["time"][len(acc_data) - 1], DATE_FORMAT_MS)
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for event_file in glob.glob(os.path.join(FILE, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            i+=1
            event_data = pd.read_csv(event_file)
            start_event = event_data["time"][0]
            stop_event = event_data["time"][len(event_data) - 1]
            event_name = os.path.basename(event_file).split('_2018')[0]
            results = results.append(pd.DataFrame(data=[[start_event,
                                                         stop_event,
                                                         event_name]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(OUT_FILE, "events_" + os.path.basename(acc_file)), index=False)

print i
