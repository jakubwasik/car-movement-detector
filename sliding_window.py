import os
import shutil
import threading
from datetime import datetime
from multiprocessing import Pool, freeze_support, Process
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
import calculate_perf_other_side
import calculate_performance
from detect_peaks import detect_peaks
import getpass
if getpass.getuser() == "PHVD86":
    import config_mot as config
else:
    import config

start = datetime.now()

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


def get_first_n_peaks(x, y, no_peaks=1):
    x_, y_ = list(x), list(y)
    if len(x_) >= no_peaks:
        return x_[:no_peaks], y_[:no_peaks]
    else:
        missing_no_peaks = no_peaks - len(x_)
        return x_ + [0] * missing_no_peaks, y_ + [0] * missing_no_peaks

def get_psd_values(y_values, T, N, f_s):
    f_values, psd_values = welch(y_values, fs=f_s, nperseg=len(y_values))
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
        temp_features = features_from_window(acc_data=acc_data, gps_data=gps_data, feature_list=feature_list)
        if i ==0:
            features = np.zeros((len(glob.glob(os.path.join(filepath, "*gps*"))), len(temp_features)))
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
    fft_energy_x = freq_x.sum()
    fft_energy_z = freq_z.sum()
    freq_x = freq_x[:config.FREQ]
    freq_z = freq_z[:config.FREQ]
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
        temp_features = np.append(temp_features, locals()[feature])
    return temp_features

def generate_event_file(raw_data_test):
    acc_data = pd.read_csv(raw_data_test, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(acc_data["time"][0], config.DATE_FORMAT_MS)
    stop = datetime.strptime(acc_data["time"][len(acc_data) - 1], config.DATE_FORMAT_MS)
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for event_file in glob.glob(os.path.join(config.NORMALIZED_LABELED_TEST_DATA, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], config.DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            event_data = pd.read_csv(event_file)
            start_event = event_data["time"][0]
            stop_event = event_data["time"][len(event_data) - 1]
            event_name = os.path.basename(event_file).split('_2018')[0]
            results = results.append(pd.DataFrame(data=[[start_event,
                                                         stop_event,
                                                         event_name]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(config.EVENTS_F_L_DATA_TEST, "events_" + os.path.basename(raw_data_test)), index=False)

def sliding_window(args):
    acc_data = pd.read_csv(args[1], sep=";", names=["time", "x", "y", "z"])
    gps_data = pd.read_csv(args[2], sep=";", names=["time", "latitude", "longitude", "speed"])
    acc_data["time"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in acc_data['time']]
    gps_data["time"] = [datetime.strptime(TIME, config.DATE_FORMAT_MS) for TIME in gps_data['time']]
    results = pd.DataFrame(data=[], columns=["start", "stop", "event"])
    for i in range(0, len(acc_data) - 600, 100):
        if i + config.WINDOW_SIZE_SAMPLES >= len(acc_data):
            break
        elif i < 400:
            pass
        else:
            start = gps_data["time"].searchsorted(acc_data["time"][i])[0]
            stop = gps_data["time"].searchsorted(acc_data["time"][i + config.WINDOW_SIZE_SAMPLES])[0]
            # print "test: "
            # print acc_data["time"][i], gps_data["time"][start]
            # print acc_data["time"][i + WINDOW_SIZE_SAMPLES], gps_data["time"][stop]
            features = features_from_window(acc_data[i:i + config.WINDOW_SIZE_SAMPLES], gps_data[start:stop], args[3]).reshape(1,-1)
            if args[4] != None:
                features = args[4].transform(features)
            #print features.shape
            #features = args[4].transform(features)
            event = args[0].predict(features)[0]
            # print [acc_data["time"][i].strftime(DATE_FORMAT_MS), acc_data["time"][i + WINDOW_SIZE].strftime(DATE_FORMAT_MS), event]
            results = results.append(pd.DataFrame(data=[[acc_data["time"][i].strftime(config.DATE_FORMAT_MS),
                                                         acc_data["time"][i + config.WINDOW_SIZE_SAMPLES].strftime(config.DATE_FORMAT_MS),
                                                         event]], columns=["start", "stop", "event"]))
    results.to_csv(os.path.join(config.EVENTS_F_R_DATA_TEST, "events_" + os.path.basename(args[1])), index=False)


def execute(feature_list):
    if os.path.isdir(config.EVENTS_F_R_DATA_TEST):
        shutil.rmtree(config.EVENTS_F_R_DATA_TEST)
        os.makedirs(config.EVENTS_F_R_DATA_TEST)
    for file in glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST_COPY, "*")):
        shutil.copy2(file, config.NORMALIZED_RAW_DATA_TEST)
    retval = features(config.NORMALIZED_LABELED_TRAIN_DATA, feature_list)
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
    clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=0)
    clf.fit(scaler.transform(retval["features"]), retval["tags"])
    # clf.best_estimator_
    print clf.best_score_
    print clf.best_params_
    #clf = BaggingClassifier(base_estimator=clf, n_estimators=50, random_state=2017, verbose=1,
    #                            n_jobs=4).fit(scaler.transform(retval["features"]), retval["tags"])

    parameter_grid = {'max_depth': np.linspace(1, 60, 50, endpoint=True),
                      'max_features':np.linspace(1, len(config.FEATURES), 1, endpoint=True),
                      'min_samples_split' : np.linspace(0.1, 1.0, 10, endpoint=True),
                      'min_samples_leaf': np.linspace(0.1, 0.5, 5, endpoint=True)}
    #parameter_grid = {
    #    'solver' : ['lsqr'],
    #    'shrinkage': [ 'auto', None],
    #    'n_components': [np.linspa(20, len(FEATURES)-4, 1, endpoint=True)],
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
    #clf = MLPClassifier(activation='tanh',solver='lbfgs',hidden_layer_sizes=(35, 34))
    #ann_params = {
    #    'hidden_layer_sizes' : arr,
    #    'activation' :  ['identity', 'logistic','tanh','relu'],
    #    'solver': ['lbfgs']
    #}
    #clf = GridSearchCV(ann, ann_params, n_jobs=4, verbose=0)
    #clf.fit(scaler.transform(retval["features"]), retval["tags"])

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
    test_retval = features(config.NORMALIZED_LABELED_TEST_DATA, feature_list)
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
    if os.path.isdir(config.EVENTS_F_L_DATA_TEST):
        shutil.rmtree(config.EVENTS_F_L_DATA_TEST)
        os.makedirs(config.EVENTS_F_L_DATA_TEST)
    pool = Pool(4)
    pool.map(generate_event_file,
             glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST, "raw*")))
    pool.close()
    pool.join()
    args = []
    pool = Pool(4)
    for acc_file in glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST, "raw*")):
        date = acc_file.split("_")[-1]
        gps_file = glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST, "gps_data_{0}*".format(date[:-6])))[0]
        args.append([clf, acc_file, gps_file, feature_list, scaler])
    pool.map(sliding_window, args)
    pool.close()
    pool.join()
    p1 = Process(target=calculate_perf_other_side.get_success_rate_from_labeled_events)
    p2 = Process(target=calculate_performance.get_success_rate_from_raw_events)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    print datetime.now() - start

def run_process(process):
    os.system('python {}'.format(process))


if __name__ == '__main__':
    arr_of_features = []
   # run_process("allign_gps.py")
   # run_process('rorate_matrix.py')
    execute(config.FEATURES)
    #for i in range(4, len(FEATURES)):
     #   temp_features = list(FEATURES)
      #  print "\n\nWITHOUT FEATURE: {0}".format(temp_features[i])
       # del(temp_features[i])
        #execute(temp_features)

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