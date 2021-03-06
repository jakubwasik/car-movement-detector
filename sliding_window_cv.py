import os
import shutil
import threading
from datetime import datetime
from glob import glob
from multiprocessing import Pool
import numpy as np
import pandas as pd
import glob
import matplotlib.pyplot as plt
import scipy
from sklearn import svm, linear_model, neighbors
from scipy.signal import butter, lfilter, freqz, welch
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectFromModel, RFE, chi2, SelectKBest, RFECV
from sklearn.model_selection import GridSearchCV, cross_val_score
from scipy.fftpack import fft
from scipy.fftpack import fftfreq
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, Normalizer
from sklearn.model_selection import train_test_split
import re

DATE_FORMAT_FILE = '%Y-%m-%d_%H_%M_%S'
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
FILE_TO_CV = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\data_to_cv"
FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_test_data"
# FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\labeled_data"
# FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\test_data"
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
OUT_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_raw_data"
OUT_FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\tests\events_from_raw_data_test"
RAW_FILE_TEST = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized_test"
RAW_FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\sensors_normalized"
from detect_peaks import detect_peaks
WINDOW_SIZE = int(round(5 * 50))
FEATURES = ["mean_x", "std_x", "mean_z", "std_z", "speed_mean", "speed_std",
            "range_speed", "energy_x", "energy_z", "signChange","zero_crossings",
            "range_z", "range_x", "coeff_x",
            "coeff_z", "coeff_x_1", "freq_x", "freq_z", "iqr", "var_x", "var_z",
             "min_z", "max_z", "min_x", "max_x", "skew",
             "autocorr_peaks_x", "fft_peaks_x", "psd_peaks_x",
            "autocorr_peaks_z", "fft_peaks_z", "psd_peaks_z"]

FREQ = 12
import errno, os, stat, shutil

def handleRemoveReadonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise Exception()

def get_first_n_peaks(x, y, no_peaks=1):
    x_, y_ = list(x), list(y)
    if len(x_) >= no_peaks:
        return x_[:no_peaks], y_[:no_peaks]
    else:
        missing_no_peaks = no_peaks - len(x_)
        return x_ + [0] * missing_no_peaks, y_ + [0] * missing_no_peaks

def get_psd_values(y_values, T, N, f_s):
    f_values, psd_values = welch(y_values, fs=f_s)
    return f_values, psd_values

def get_fft_values(y_values, T, N, f_s):
    f_values = np.fft.fftfreq(len(y_values))
    fft_values_ = fft(y_values)
    fft_values = 2.0/N * np.abs(fft_values_[0:N//2])
    return f_values, fft_values
 
def autocorr(x):
    result = np.correlate(x, x, mode='full')
    return result[len(result)//2:]

def get_autocorr_values(y_values, T, N, f_s):
    autocorr_values = autocorr(y_values)
    x_values = np.array([T * jj for jj in range(0, N)])
    return x_values, autocorr_values

def get_features(x_values, y_values, mph=None):
    indices_peaks = detect_peaks(y_values, mph=mph)
    peaks_x, peaks_y = get_first_n_peaks(x_values[indices_peaks], y_values[indices_peaks])
    return peaks_x + peaks_y

def peak_freq(frequencies):
    freqs = np.fft.fftfreq(len(frequencies))
    idx = np.argmax(frequencies)
    return np.abs(50 * freqs[idx])
def features(filepath, feature_list):
    i = 0
    tags = []
    events = []
    for gps_file in glob.glob(os.path.join(filepath, "*gps*")):
        event, date = gps_file.split("_gps_")
        acc_file = glob.glob(os.path.join(filepath, "{event}_2018*{date}".format(**locals())))
        acc_data = pd.read_csv(acc_file[0], sep=",")
        gps_data = pd.read_csv(gps_file, sep=",")
        x = np.array(acc_data["x"])
        #x = butter_lowpass_filter(x, 4, 50)
        #x = butter_highpass_filter(x, 0.5, 50)
        z = np.array(acc_data["z"])
        #z = butter_lowpass_filter(z, 4, 50)
        #z = butter_highpass_filter(z, 0.5, 50)
        # z=z_new
        freq_x = 2.0/len(x) * np.abs(fft(x))
        freq_z = 2.0/len(z) * np.abs(fft(z))
        #peak_frequency_x = peak_freq(freq_x)
        #peak_frequency_z = peak_freq(freq_z)
        fft_energy_x = freq_x.sum()
        fft_energy_z = freq_z.sum()
        freq_x = freq_x[:FREQ]
        freq_z = freq_z[:FREQ]
        dx = scipy.gradient(x)
        dz = scipy.gradient(z)
        mean_dx = np.mean(dx)
        std_dx = np.std(dx)
        mean_dz = np.mean(dz)
        std_dz = np.std(dz)
        energy_dx = dx.sum()
        energy_dz = dz.sum()
        energy_x = x.sum()
        energy_z = z.sum()
        zero_crossings_dx = len(np.where(np.diff(np.sign(dx))))
        range_z = z.max() - z.min()
        range_x = x.max() - x.min()
        speed = np.array(gps_data["speed"])
        #h_mean_x = scipy.stats.hmean(x)
        #h_mean_z = scipy.stats.hmean(z)
        #h_mean_speed = scipy.stats.hmean(speed)
        range_speed = speed.max() - speed.min()
        time = np.linspace(0, len(acc_data["time"]) * 0.02, len(acc_data["time"]))
        time_speed = np.linspace(0, len(gps_data["time"]) * 0.02, len(gps_data["time"]))
        coeff_x = np.polyfit(time, x, 3)
        coeff_x_1 = np.polyfit(time, x, 1)
        coeff_z = np.polyfit(time, z, 3)
        iqr = scipy.stats.iqr(x)
        signChange = np.sign(x).sum()
        zero_crossings = len(np.where(np.diff(np.sign(x))))
        coeff_speed = np.polyfit(time_speed, speed, 2)
        mean_x = np.mean(x)
        std_x = np.std(x)
        mean_z = np.mean(z)
        std_z = np.std(z)
        var_x = np.var(x)
        var_z = np.var(z)
        min_x = x.min()
        max_x = x.max()
        min_z = z.min()
        max_z = z.max()
        speed_mean = np.mean(speed)
        speed_std = np.std(speed)
        skew = scipy.stats.skew(x)
        kurtosis = scipy.stats.kurtosis(x)
        #std_x = std_x if std_x != 0 else 0.0001
        #std_z = std_z if std_z != 0 else 0.0001
        signal_to_noise_x = mean_x / std_x
        signal_to_noise_z = mean_z / std_z
        percentile_x_25 = np.percentile(x, 25)
        percentile_x_50 = np.percentile(x, 50)
        percentile_x_75 = np.percentile(x, 75)
        percentile_z_25 = np.percentile(z, 25)
        percentile_z_50 = np.percentile(z, 50)
        percentile_z_75 = np.percentile(z, 75)
        signal_min_x = np.nanpercentile(x, 5)
        signal_max_x = np.nanpercentile(x, 100 - 5)
        # ijk = (100 - 2*percentile)/10
        mph = signal_min_x + (signal_max_x - signal_min_x) * 0.2
        N = len(x)
        f_s = 50
        t_n = N * f_s
        T = t_n / N
        max_peak_height = 0.1 * np.nanmax(x)
        psd_peaks_x = get_features(*get_psd_values(x, T, N, f_s))
        fft_peaks_x = get_features(*get_fft_values(x, T, N, f_s))
        autocorr_peaks_x = get_features(*get_autocorr_values(x, T, N, f_s))
        signal_min_z = np.nanpercentile(z, 5)
        signal_max_z = np.nanpercentile(z, 100 - 5)
        # ijk = (100 - 2*percentile)/10
        mph = signal_min_z + (signal_max_z - signal_min_z) * 0.2
        N = len(z)
        f_s = 50
        t_n = N * f_s
        T = t_n / N
        max_peak_height = 0.1 * np.nanmax(z)
        psd_peaks_z = get_features(*get_psd_values(z, T, N, f_s))
        fft_peaks_z = get_features(*get_fft_values(z, T, N, f_s))
        autocorr_peaks_z = get_features(*get_autocorr_values(z, T, N, f_s))
        #signal_to_noise_speed = speed_mean / speed_std
        temp_features=np.array([])
        for feature in feature_list:
            #print feature, locals()[feature]
            temp_features=np.append(temp_features, locals()[feature])
        if i ==0:
            features = np.zeros((len(glob.glob(os.path.join(filepath, "*gps*"))), len(temp_features)))
        #temp_features = np.array(
        #    [mean_x, std_x, mean_z, std_z, speed_mean, speed_std, range_speed, energy_x, energy_z, signChange,
        #     zero_crossings, mean_dx, std_dx, mean_dz, std_dz, energy_dx, energy_dz, zero_crossings_dx, range_z, range_x
        #     ])
        #temp_features = np.concatenate(
        #    (temp_features, coeff_x, coeff_z, coeff_x_1, coeff_speed, freq_x, freq_z))
        features[i] += temp_features
        tags.append(event.split("\\")[-1])
        events.append(acc_file)
        i += 1
    return {
        "features": features,
        "tags": tags,
        "events": events
    }


def features_from_window(acc_data, gps_data, feature_list):
    i = 0
    tags = []
    events = []
    x = np.array(acc_data["x"])
    #x = butter_lowpass_filter(x, 4, 50)
    z = np.array(acc_data["z"])
    #z = butter_lowpass_filter(z, 4, 50)
    #z = butter_highpass_filter(z, 0.5, 50)
    # z=z_new
    freq_x = 2.0 / len(x) * np.abs(fft(x))
    freq_z = 2.0 / len(z) * np.abs(fft(z))
    peak_frequency_x = peak_freq(freq_x)
    peak_frequency_z = peak_freq(freq_z)
    fft_energy_x = freq_x.sum()
    fft_energy_z = freq_z.sum()
    freq_x = freq_x[:FREQ]
    freq_z = freq_z[:FREQ]
    dx = scipy.gradient(x)
    dz = scipy.gradient(z)
    mean_dx = np.mean(dx)
    std_dx = np.std(dx)
    mean_dz = np.mean(dz)
    std_dz = np.std(dz)
    energy_dx = dx.sum()
    energy_dz = dz.sum()
    energy_x = x.sum()
    energy_z = z.sum()
    #h_mean_x = scipy.stats.hmean(x)
    #h_mean_z = scipy.stats.hmean(z)
    zero_crossings_dx = len(np.where(np.diff(np.sign(dx))))
    range_z = z.max() - z.min()
    range_x = x.max() - x.min()
    speed = np.array(gps_data["speed"])
    #h_mean_speed = scipy.stats.hmean(speed)
    range_speed = speed.max() - speed.min()
    time = np.linspace(0, len(acc_data["time"]) * 0.02, len(acc_data["time"]))
    time_speed = np.linspace(0, len(gps_data["time"]) * 0.02, len(gps_data["time"]))
    coeff_x = np.polyfit(time, x, 3)
    coeff_x_1 = np.polyfit(time, x, 1)
    signChange = np.sign(x).sum()
    zero_crossings = len(np.where(np.diff(np.sign(x))))
    coeff_z = np.polyfit(time, z, 3)
    coeff_speed = np.polyfit(time_speed, speed, 2)
    iqr = scipy.stats.iqr(x)
    mean_x = np.mean(x)
    std_x = np.std(x)
    mean_z = np.mean(z)
    std_z = np.std(z)
    min_x = x.min()
    max_x = x.max()
    min_z = z.min()
    max_z = z.max()
    speed_mean = np.mean(speed)
    speed_std = np.std(speed)
    var_x = np.var(x)
    var_z = np.var(z)
    skew = scipy.stats.skew(x)
    kurtosis = scipy.stats.kurtosis(x)
    signal_to_noise_x = mean_x / std_x
    signal_to_noise_z = mean_z / std_z
    #std_x = std_x if std_x != 0 else 0.0001
    #std_z = std_z if std_z != 0 else 0.0001
    percentile_x_25 = np.percentile(x, 25)
    percentile_x_50 = np.percentile(x, 50)
    percentile_x_75 = np.percentile(x, 75)
    percentile_z_25 = np.percentile(z, 25)
    percentile_z_50 = np.percentile(z, 50)
    percentile_z_75 = np.percentile(z, 75)
    signal_min_x = np.nanpercentile(x, 5)
    signal_max_x = np.nanpercentile(x, 100 - 5)
    # ijk = (100 - 2*percentile)/10
    mph = signal_min_x + (signal_max_x - signal_min_x)* 0.2
    N = len(x)
    f_s = 50
    t_n = N * f_s
    T = t_n / N
    max_peak_height = 0.1 * np.nanmax(x)
    psd_peaks_x = get_features(*get_psd_values(x, T, N, f_s))
    fft_peaks_x = get_features(*get_fft_values(x, T, N, f_s))
    autocorr_peaks_x = get_features(*get_autocorr_values(x, T, N, f_s))
    signal_min_z = np.nanpercentile(z, 5)
    signal_max_z = np.nanpercentile(z, 100 - 5)
    # ijk = (100 - 2*percentile)/10
    mph = signal_min_z + (signal_max_z - signal_min_z)* 0.2
    N = len(z)
    f_s = 50
    t_n = N * f_s
    T = t_n / N
    max_peak_height = 0.1 * np.nanmax(z)
    psd_peaks_z = get_features(*get_psd_values(z, T, N, f_s))
    fft_peaks_z = get_features(*get_fft_values(z, T, N, f_s))
    autocorr_peaks_z = get_features(*get_autocorr_values(z, T, N, f_s))
    #signal_to_noise_speed = speed_mean / speed_std
    temp_features = np.array([])
    for feature in feature_list:
        #print feature, locals()[feature]
        temp_features = np.append(temp_features, locals()[feature])
    # temp_features = np.array(
    #    [mean_x, std_x, mean_z, std_z, speed_mean, speed_std, range_speed, energy_x, energy_z, signChange,
    #     zero_crossings, mean_dx, std_dx, mean_dz, std_dz, energy_dx, energy_dz, zero_crossings_dx, range_z, range_x
    #     ])
    # temp_features = np.concatenate(
    #    (temp_features, coeff_x, coeff_z, coeff_x_1, coeff_speed, freq_x, freq_z))

    return temp_features.reshape(1, -1)



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
            features = features_from_window(acc_data[i:i + WINDOW_SIZE], gps_data[start:stop], args[3])
            features = args[4].transform(features)
            # print features.shape
            # features = args[4].transform(features)
            event = args[0].predict(features)[0]
            # print [acc_data["time"][i].strftime(DATE_FORMAT_MS), acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS), event]
            results = results.append(pd.DataFrame(data=[[acc_data["time"][i].strftime(DATE_FORMAT_MS),
                                                         acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS),
                                                         event]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(OUT_FILE_TEST, "events_" + os.path.basename(args[1])), index=False)


def copy_train_set(file):
    raw_data = pd.read_csv(file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(raw_data["time"][0], DATE_FORMAT_MS)
    stop = datetime.strptime(raw_data["time"][len(raw_data) - 1], DATE_FORMAT_MS)
    for event_file in glob.glob(os.path.join(FILE_TO_CV, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            gps_file = glob.glob(os.path.join(FILE_TO_CV, "*gps*{0}*".format(event_file[-23:-4])))[0]
            shutil.copy2(event_file, FILE)
            shutil.copy2(gps_file, FILE)


def copy_test_set(file):
    raw_data = pd.read_csv(file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(raw_data["time"][0], DATE_FORMAT_MS)
    stop = datetime.strptime(raw_data["time"][len(raw_data) - 1], DATE_FORMAT_MS)
    for event_file in glob.glob(os.path.join(FILE_TO_CV, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            gps_file = glob.glob(os.path.join(FILE_TO_CV, "*gps*{0}*".format(event_file[-23:-4])))[0]
            shutil.copy2(event_file, FILE_TEST)
            shutil.copy2(gps_file, FILE_TEST)
    shutil.copy2(file, RAW_FILE_TEST)


def execute(feature_list):
    start = datetime.now()
    files = glob.glob(os.path.join(RAW_FILE, "raw_data*"))
    train_set, test_set, train_label, test_label = train_test_split(files, [os.path.basename(f) for f in files])
    if os.path.isdir(FILE):
        shutil.rmtree(FILE, onerror=handleRemoveReadonly)
        os.makedirs(FILE)
    if os.path.isdir(FILE_TEST):
        shutil.rmtree(FILE_TEST, onerror=handleRemoveReadonly)
        os.makedirs(FILE_TEST)
    if os.path.isdir(RAW_FILE_TEST):
        shutil.rmtree(RAW_FILE_TEST, onerror=handleRemoveReadonly)
        os.makedirs(RAW_FILE_TEST)

    if os.path.isdir(OUT_FILE_TEST):
        shutil.rmtree(OUT_FILE_TEST, onerror=handleRemoveReadonly)
        os.makedirs(OUT_FILE_TEST)
    if os.path.isdir(OUT_FILE):
        shutil.rmtree(OUT_FILE, onerror=handleRemoveReadonly)
        os.makedirs(OUT_FILE)
    p2 = Pool(4)
    p2.map(copy_test_set, test_set)
    p2.close()
    p2.join()
    retval = features(FILE, feature_list)
    scaler = StandardScaler().fit(retval["features"])
    print retval["features"].shape
    # print retval["features"].shape
    # pca = PCA(0.8)
    # pca.fit(retval["features"])
    # retval["features"] = pca.transform(retval["features"])
    # print retval["features"].shape
    svr = svm.SVC()
    exponential_range = [pow(10, i) for i in range(-4, 1)]
    # exponential_range = np.logspace(-10, 1, 35 )
    parameters = {'kernel': ['linear', 'rbf', ], 'C': exponential_range, 'gamma': exponential_range}
    clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=0)
    clf.fit(scaler.transform(retval["features"]), retval["tags"])
    # clf.best_estimator_
    print clf.best_score_
    print clf.best_params_
    # model = RFECV(clf.best_estimator_, 40, verbose=3)
    # retval["features"] = model.fit_transform(retval["features"], retval["tags"])
    # print retval["features"].shape
    # print model.support_
    # clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=4)
    # clf.fit(retval["features"], retval["tags"])
    # print clf.best_estimator_
    # print clf.best_score_
    # print clf.best_params_
    # print retval["features"].shape

    # scores = cross_val_score(clf, retval["features"], retval["tags"], cv=10, n_jobs=8, verbose=False)
    # print scores
    #   print 'Sprawnosc klasyfikatora:'
    # print scores
    test_retval = features(FILE_TEST, feature_list)
    # test_retval["features"] = model.transform(test_retval["features"])
    y = clf.predict(scaler.transform(test_retval["features"]))
    y1 = clf.predict(scaler.transform(retval["features"]))
    # print y, tags
    k = 0
    for i in range(len(y)):
        if y[i] != test_retval["tags"][i]:
            k += 1
            # print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print "ZLE SKLASYFIKOWANO: {0}".format(k)
    k = 0
    for i in range(len(y1)):
        if y1[i] != retval["tags"][i]:
            k += 1
            # print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print "ZLE SKLASYFIKOWANO (ALL): {0}".format(k)
    run_process("events_from_labeled_data.py")
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(RAW_FILE_TEST, "raw*")):
        date = acc_file.split("_")[-1]
        gps_file = glob.glob(os.path.join(RAW_FILE, "gps_data_{0}*".format(date[:-6])))[0]
        args.append([clf, acc_file, gps_file, feature_list, scaler])
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
    execute(FEATURES)
    # for i in range(4, len(FEATURES)):
    #    temp_features = list(FEATURES)
    #    print "\n\nWITHOUT FEATURE: {0}".format(temp_features[i])
    #    del (temp_features[i])
    #    execute(temp_features)
