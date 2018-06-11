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
from scipy.signal import butter, lfilter, freqz
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
WINDOW_SIZE = int(round(5 * 50))
FEATURES = ["mean_x", "std_x", "mean_z", "std_z", "speed_mean", "speed_std",
            "range_speed", "energy_x", "energy_z", "signChange","zero_crossings",
                "energy_dx",
             "range_z", "range_x", "coeff_x",
            "coeff_z", "coeff_x_1", "freq_x", "freq_z", "iqr", "var_x", "var_z"]

FREQ = 12
# "coeff_speed","mean_dx", "mean_dz","std_dx","std_dz","zero_crossings_dx",, "energy_dz"
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
        freq_x = np.abs(fft(x))
        freq_x = freq_x[:FREQ]
        freq_z = np.abs(fft(z))
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
        speed_mean = np.mean(speed)
        speed_std = np.std(speed)
        #skew = scipy.stats.skew(x)
        #kurtosis = scipy.stats.kurtosis(x)
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
    freq_x = np.abs(fft(x))
    freq_z = np.abs(fft(z))
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
    speed_mean = np.mean(speed)
    speed_std = np.std(speed)
    var_x = np.var(x)
    var_z = np.var(z)
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
    #skew = scipy.stats.skew(x)
    #kurtosis = scipy.stats.kurtosis(x)
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
            #print features.shape
            #features = args[4].transform(features)
            event = args[0].predict(features)[0]
            # print [acc_data["time"][i].strftime(DATE_FORMAT_MS), acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS), event]
            results = results.append(pd.DataFrame(data=[[acc_data["time"][i].strftime(DATE_FORMAT_MS),
                                                         acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS),
                                                         event]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(OUT_FILE_TEST, "events_" + os.path.basename(args[1])), index=False)


def execute(feature_list):
    if os.path.isdir(OUT_FILE_TEST):
        shutil.rmtree(OUT_FILE_TEST)
        os.makedirs(OUT_FILE_TEST)
    for file in glob.glob(os.path.join(RAW_FILE_TEMP, "*")):
        shutil.copy2(file, RAW_FILE)
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
    #exponential_range = np.logspace(-10, 1, 35 )
    parameters = {'kernel': ['linear', 'rbf', ], 'C': exponential_range, 'gamma': exponential_range}
    #clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=0)
    #clf.fit(scaler.transform(retval["features"]), retval["tags"])
    # clf.best_estimator_

    parameter_grid = {'max_depth': np.linspace(1, 60, 50, endpoint=True),
                      'max_features':np.linspace(1, len(FEATURES), 1, endpoint=True),
                      'min_samples_split' : np.linspace(0.1, 1.0, 10, endpoint=True),
                      'min_samples_leaf': np.linspace(0.1, 0.5, 5, endpoint=True)}
    #parameter_grid = {
    #    'solver' : ['lsqr'],
    #    'shrinkage': [ 'auto', None],
    #    'n_components': [np.linspace(20, len(FEATURES)-4, 1, endpoint=True)],
    #}
    #clf = LinearDiscriminantAnalysis()
    #clf = GaussianNB()
    #clf = DecisionTreeClassifier()
    #clf = GridSearchCV(clf, parameter_grid, n_jobs=4, verbose=0)
    #clf.fit(scaler.transform(retval["features"]), retval["tags"])

    arr = [(elem,) for elem in np.arange(3,50)]
    for i in range(1,50):
        arr += [(i, elem) for elem in np.arange(3, 50)]
        arr += [(elem, i) for elem in np.arange(3, 50)]
    ann = MLPClassifier(verbose=1, warm_start=True, max_iter=200)
    ann_params = {
        'hidden_layer_sizes' : arr,
        'activation' :  ['identity', 'logistic','tanh','relu'],
        'solver': ['lbfgs']
    }
    clf = GridSearchCV(ann, ann_params, n_jobs=4, verbose=0)
    clf.fit(scaler.transform(retval["features"]), retval["tags"])
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
            #print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print "ZLE SKLASYFIKOWANO: {0}".format(k)
    k = 0
    for i in range(len(y1)):
        if y1[i] != retval["tags"][i]:
            k += 1
            #print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
    print "ZLE SKLASYFIKOWANO (ALL): {0}".format(k)
    run_process("events_from_labeled_data.py")
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(RAW_FILE, "raw*")):
        date = acc_file.split("_")[-1]
        gps_file = glob.glob(os.path.join(RAW_FILE, "gps_data_{0}*".format(date[:-6])))[0]
        args.append([clf, acc_file, gps_file, feature_list, scaler])
    pool.map(sliding_window, args)
    pool.close()
    pool.join()
    processes = ('calculate_perf_other_side.py', 'calculate_performance.p y')

    pool = Pool(processes=2)
    pool.map(run_process, processes)
    pool.close()
    pool.join()
    print datetime.now() - start
def run_process(process):
    os.system('python {}'.format(process))

if __name__ == '__main__':
    arr_of_features = []
    run_process("allign_gps.py")
    run_process('rorate_matrix.py')
    execute(FEATURES)
  #  for i in range(4, len(FEATURES)):
   #     temp_features = list(FEATURES)
    #    print "\n\nWITHOUT FEATURE: {0}".format(temp_features[i])
     ##  execute(temp_features)

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