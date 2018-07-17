import os
import shutil
import threading
from datetime import datetime
from multiprocessing import Pool, freeze_support
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
import scipy
from sklearn import svm, linear_model, neighbors
from scipy.signal import butter, lfilter, freqz, welch
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.feature_selection import SelectFromModel, RFE, chi2, SelectKBest, RFECV
from sklearn.model_selection import GridSearchCV, cross_val_score
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
from sklearn.naive_bayes import GaussianNB
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, Normalizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
import re

from syntatic_method import butter_lowpass_filter, error, process_event, make_str_from_coeff

start = datetime.now()
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"
# FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\labeled_data"
# FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_raw_data"
OUT_FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_raw_data_test"
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized_test"
RAW_FILE_TEMP = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized_test - kopia"
WINDOW_SIZE = int(round(6 * 50))


def sliding_window(args):
    acc_data = pd.read_csv(args[0], sep=";", names=["time", "x", "y", "z"])
    acc_data["time"] = [datetime.strptime(TIME, DATE_FORMAT_MS) for TIME in acc_data['time']]
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for i in range(0, len(acc_data) - 600, 50):
        if i + WINDOW_SIZE >= len(acc_data):
            break
        elif i < 400:
            pass
        else:
            filtered_data_x = butter_lowpass_filter(acc_data["x"][i:i + WINDOW_SIZE], 2, 50)
            filtered_data_z = butter_lowpass_filter(acc_data["z"][i:i + WINDOW_SIZE], 2, 50)
            coeff_arr_x = process_event(filtered_data_x)
            string_to_match_x = make_str_from_coeff(coeff_arr_x)
            coeff_arr_z = process_event(filtered_data_z)
            string_to_match_z = make_str_from_coeff(coeff_arr_z)

            skret_w_prawo = re.search("^d?c?[ab]+?[abcd]*?[efg]+d?$", string_to_match_x)
            skret_w_lewo = re.search("^d?e?[gf]+?[fged]*?[cba]+d?$", string_to_match_x)
            zm_pasa_lewy = re.search("^[fe]+?d?[cba]{1,3}[gfed]+?[ab]?$", string_to_match_x)
            zm_pasa_prawy = re.search("^[bc]+?d?[efg]{1,3}[abcd]+?[eg]?$", string_to_match_x)
            hamowanie = re.search("^[abc]{2,5}[bcdef]*[efg]?d?$", string_to_match_z)
            przyspieszanie = re.search("^d{2,4}?[efg]+d?[abc]+.*?$", string_to_match_z)
            zatrzymanie = re.search("^[ab]+?[bcdef]*?[fg]+.*?[cde]{1,5}$", string_to_match_z)
            event = ""
            if przyspieszanie:
                if event:
                    print "[w przyspieszanie]Juz sklasyfikowano na {0}".format(event)
                event = "przyspieszanie_na_swiatlach"
            if zatrzymanie:
                if event:
                    print "[w zatrzymanie] Juz sklasyfikowano na {0}".format(event)
                event = "zatrzymanie_na_swiatlach"

            if hamowanie:
                if event:
                    print "[w hamowanie]Juz sklasyfikowano na {0}".format(event)
                event = "hamowanie"

            if zm_pasa_lewy:
                if event:
                    print "[w zm_pasa_lewy]Juz sklasyfikowano na {0}".format(event)
                event = "zmiana_pasa_na_lewy"
            if zm_pasa_prawy:
                if event:
                    print "[w zm_pasa_prawy]Juz sklasyfikowano na {0}".format(event)
                event = "zmiana_pasa_na_prawy"

            if skret_w_prawo:
                event = "skret_w_prawo"

            if skret_w_lewo:
                if event:
                    print "[w skret w lewo] Juz sklasyfikowano na {0}".format(event)
                event = "skret_w_lewo"

            if not event:
                event = "indle"

            results = results.append(pd.DataFrame(data=[[acc_data["time"][i].strftime(DATE_FORMAT_MS),
                                                         acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS),
                                                         event]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(OUT_FILE_TEST, "events_" + os.path.basename(args[0])), index=False)


def execute():
    if os.path.isdir(OUT_FILE_TEST):
        shutil.rmtree(OUT_FILE_TEST)
        os.makedirs(OUT_FILE_TEST)
    for file in glob.glob(os.path.join(RAW_FILE_TEMP, "*")):
        shutil.copy2(file, RAW_FILE)
    run_process("events_from_labeled_data.py")
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(RAW_FILE, "raw*")):
        args.append([acc_file])
    pool.map(sliding_window, args)
    pool.close()
    pool.join()
    processes = ('calculate_perf_other_side.py', 'calculate_performance.py')

    pool = Pool(processes=2)
    pool.map(run_process, processes)
    pool.close()
    pool.join()
    print datetime.now() - start


def run_process(process):
    os.system('python {}'.format(process))


if __name__ == '__main__':
    arr_of_features = []
    # run_process("allign_gps.py")
    # run_process('rorate_matrix.py')
    execute()
    # for i in range(4, len(FEATURES)):
    #    temp_features = list(FEATURES)
    #    print "\n\nWITHOUT FEATURE: {0}".format(temp_features[i])
    #    del(temp_features[i])
    #    execute(temp_features)
