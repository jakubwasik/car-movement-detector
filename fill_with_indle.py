import glob
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
DATE_FORMAT_MS_FOR_LABELED = '%Y-%m-%d %H:%M:%S.%f'
RAW_FILE = r"C:\Users\kuba\Desktop\sensor data\sensors_normalized"
FILE = r"C:\Users\kuba\Desktop\sensor data\normalized_data"
OUT_FILE = r"C:\Users\kuba\Desktop\sensor data\events_from_labeled_data_with_indle"
IN_FILE = r"C:\Users\kuba\Desktop\sensor data\events_from_labeled_data"
i=0
for acc_file in glob.glob(os.path.join(RAW_FILE, "raw_data*")):
    acc_data = pd.read_csv(acc_file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(acc_data["time"][0], DATE_FORMAT_MS)
    stop_final = datetime.strptime(acc_data["time"][len(acc_data) - 1], DATE_FORMAT_MS)
    events_from_labeled_file = pd.read_csv(
        os.path.join(OUT_FILE, "events_" + os.path.basename(acc_file)))
    events_from_labeled_file = events_from_labeled_file.sort_values(by=["start"])
    events_from_labeled_file = events_from_labeled_file.reset_index(drop=True)
    events_from_labeled_file["start"] = [datetime.strptime(TIME, DATE_FORMAT_MS_FOR_LABELED) for TIME in
                                         events_from_labeled_file['start']]
    events_from_labeled_file["stop"] = [datetime.strptime(TIME, DATE_FORMAT_MS_FOR_LABELED) for TIME in
                                        events_from_labeled_file['stop']]
    print start, stop_final
    size = len(events_from_labeled_file)
    for i in range(size+1):
        if i == size:
            stop = stop_final
        else:
            stop = events_from_labeled_file["start"][i]
        print stop
        arr = np.arange(start, stop, timedelta(seconds=7))
        for j in range(0,len(arr)-1, 1):
            events_from_labeled_file = events_from_labeled_file.append(pd.DataFrame(data=[[arr[j],
                                                         arr[j+1],
                                                         "indle"]], columns=["start", "stop", "event"]),
                                                                       ignore_index=True)
        start = events_from_labeled_file["stop"][i]
        print start
    events_from_labeled_file = events_from_labeled_file.sort_values(by=["start"])
    events_from_labeled_file = events_from_labeled_file.reset_index(drop=True)
    events_from_labeled_file.to_csv(os.path.join(OUT_FILE, "events_" + os.path.basename(acc_file)),
                                    index=False)





"""
    
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
"""