import logging, os, shutil, glob
from multiprocessing import Pool, Process, Queue, Manager
import pandas as pd
from datetime import datetime

import sys
from sklearn import svm
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler
from sqlalchemy.sql.functions import sysdate

import calculate_perf_other_side
import calculate_performance
import getpass
import sliding_window
if getpass.getuser() == "PHVD86":
    import config_mot as config
else:
    import config


def _copy_train_set(file):
    raw_data = pd.read_csv(file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(raw_data["time"][0], config.DATE_FORMAT_MS)
    stop = datetime.strptime(raw_data["time"][len(raw_data) - 1], config.DATE_FORMAT_MS)
    for event_file in glob.glob(os.path.join(config.DATA_TO_CV, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], config.DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            gps_file = glob.glob(os.path.join(config.DATA_TO_CV, "*gps*{0}*".format(event_file[-23:-4])))[0]
            shutil.copy2(event_file, config.WORKSPACE_NORMALIZED_LABELED_TRAIN_DATA)
            shutil.copy2(gps_file, config.WORKSPACE_NORMALIZED_LABELED_TRAIN_DATA)


def _copy_test_set(file):
    raw_data = pd.read_csv(file, sep=";", names=["time", "x", "y", "z"])
    start = datetime.strptime(raw_data["time"][0], config.DATE_FORMAT_MS)
    stop = datetime.strptime(raw_data["time"][len(raw_data) - 1], config.DATE_FORMAT_MS)
    for event_file in glob.glob(os.path.join(config.DATA_TO_CV, "*2018*2018*")):
        event_start = datetime.strptime(event_file[-23:-4], config.DATE_FORMAT_FILE)
        if start < event_start and stop > event_start:
            gps_file = glob.glob(os.path.join(config.DATA_TO_CV, "*gps*{0}*".format(event_file[-23:-4])))[0]
            shutil.copy2(event_file, config.WORKSPACE_NORMALIZED_LABELED_TEST_DATA)
            shutil.copy2(gps_file, config.WORKSPACE_NORMALIZED_LABELED_TEST_DATA)
    shutil.copy2(file, config.WORKSPACES_NORMALIZED_RAW_DATA_TEST)
class loggerFactory:
    @staticmethod
    def getLogger():
        logging.basicConfig(format="%(levelname)s: %(asctime)s : %(message)s")
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        return logger

class MainExecutor(object):
    def __init__(self, normalize_data = True, cross_validation=False, features = None):
        self.logger = loggerFactory.getLogger()
        self.now = datetime.now()
        self.clf = None
        self.scaler = None
        self.normalize_data = normalize_data
        self.cv = cross_validation
        self.features = features if features != None else config.FEATURES
        if self.cv:
            self.test_data = config.WORKSPACE_NORMALIZED_LABELED_TEST_DATA
            self.train_data = config.WORKSPACE_NORMALIZED_LABELED_TRAIN_DATA
            self.test_raw_data = config.WORKSPACES_NORMALIZED_RAW_DATA_TEST
            self.train_raw_data = config.WORKSPACES_NORMALIZED_RAW_DATA
        else:
            self.test_data = config.NORMALIZED_LABELED_TEST_DATA
            self.train_data = config.NORMALIZED_LABELED_TRAIN_DATA
            self.test_raw_data = config.NORMALIZED_RAW_DATA_TEST
            self.train_raw_data = config.NORMALIZED_RAW_DATA
        self.prepare_workspaces()
        self.train_features_vector = sliding_window.features(self.train_data,
                                                             self.features)
        self.test_features_vector = sliding_window.features(self.test_data,
                                                            self.features)
        self.m = Manager()
        self.q_all = self.m.Queue()
        self.q_only_events = self.m.Queue()

    def _set_test_data(self):
        for file in glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST, "*")):
            os.remove(file)
        for file in glob.glob(os.path.join(config.NORMALIZED_RAW_DATA_TEST_COPY, "*")):
            shutil.copy2(file, config.NORMALIZED_RAW_DATA_TEST)

    def _remove_content(self, path):
        for file in glob.glob(os.path.join(path, "*")):
            os.remove(file)



    def prepare_workspaces(self):
        self.logger.info("Preparing wokspaces...")
        if os.path.isdir(config.EVENTS_F_R_DATA_TEST):
            shutil.rmtree(config.EVENTS_F_R_DATA_TEST)
            os.makedirs(config.EVENTS_F_R_DATA_TEST)
        if os.path.isdir(config.EVENTS_F_L_DATA_TEST):
            shutil.rmtree(config.EVENTS_F_L_DATA_TEST)
            os.makedirs(config.EVENTS_F_L_DATA_TEST)
        if self.cv:
            files = glob.glob(os.path.join(config.NORMALIZED_RAW_DATA, "raw_data*"))
            train_set, test_set, train_label, test_label = train_test_split(files, [os.path.basename(f) for f in files])
            self._remove_content(config.WORKSPACE_NORMALIZED_LABELED_TEST_DATA)
            self._remove_content(config.WORKSPACE_NORMALIZED_LABELED_TRAIN_DATA)
            self._remove_content(config.WORKSPACES_NORMALIZED_RAW_DATA)
            self._remove_content(config.WORKSPACES_NORMALIZED_RAW_DATA_TEST)
            p1 = Pool(8)
            p1.map(_copy_train_set, train_set)
            p1.close()
            p1.join()
            p2 = Pool(8)
            p2.map(_copy_test_set, test_set)
            p2.close()
            p2.join()
        else:
            self._set_test_data()

        self.logger.info("Done!")

    def train_SVM_classifier(self):
        svr = svm.SVC()
        exponential_range = [pow(10, i) for i in range(-4, 1)]
        # exponential_range = np.logspace(-10, 1, 35 )
        parameters = {'kernel': ['linear', 'rbf', ], 'C': exponential_range, 'gamma': exponential_range}
        self.clf = GridSearchCV(svr, parameters, n_jobs=8, verbose=0)
        if self.normalize_data:
            self.scaler = StandardScaler().fit(self.train_features_vector["features"])
            self.clf.fit(self.scaler.transform(self.train_features_vector["features"]), self.train_features_vector["tags"])
        else:
            self.clf.fit(self.train_features_vector["features"], self.train_features_vector["tags"])
        self.logger.info(self.clf.best_score_)
        self.logger.info(self.clf.best_params_)

    def test_SVM_classfier(self):
        if self.normalize_data and self.scaler:
            test_output = self.clf.predict(self.scaler.transform(self.test_features_vector["features"]))
            train_output = self.clf.predict(self.scaler.transform(self.train_features_vector["features"]))
        else:
            test_output = self.clf.predict(self.test_features_vector["features"])
            train_output = self.clf.predict(self.train_features_vector["features"])
        # print y, tags
        k = 0
        for i in range(len(test_output)):
            if test_output[i] != self.test_features_vector["tags"][i]:
                k += 1
                # print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
        self.logger.info("ZLE SKLASYFIKOWANO: {0}".format(k))
        k = 0
        for i in range(len(train_output)):
            if train_output[i] != self.train_features_vector["tags"][i]:
                k += 1
                # print "\nZLE SKLASYFIKOWANO: ", test_retval['events'][i], "SKLASYFIKOWANO JAKO: ", y[i],
        self.logger.info("ZLE SKLASYFIKOWANO (ALL): {0}".format(k))

    def generate_event_file(self):
        self.logger.info("Generating event file...")
        pool = Pool(8)
        pool.map(sliding_window.generate_event_file,
                 glob.glob(os.path.join(self.test_raw_data, "raw*")))
        pool.close()
        pool.join()
        self.logger.info("Done!")

    def run_sliding_window(self):
        self.logger.info("Running sliding window...")
        args = []
        pool = Pool(8)
        for acc_file in glob.glob(os.path.join(self.test_raw_data, "raw*")):
            date = acc_file.split("_")[-1]
            gps_file = glob.glob(os.path.join(config.NORMALIZED_RAW_DATA, "gps_data_{0}*".format(date[:-6])))[0]
            args.append([self.clf, acc_file, gps_file, self.features, self.scaler])
        pool.map(sliding_window.sliding_window, args)
        pool.close()
        pool.join()
        self.logger.info("Done!")

    def collect_results(self):
        self.logger.info("Collecting results...")
       # p1 = Process(target=calculate_perf_other_side.get_success_rate_from_labeled_events)
       # p2 = Process(target=calculate_performance.get_success_rate_from_raw_events)
        p1 = Pool(4)

        p1.map(calculate_performance.get_success_rate_from_raw_events,
               [(elem, self.q_all) for elem in glob.glob(os.path.join(config.EVENTS_F_R_DATA_TEST, "*"))])
        p2 = Pool(4)
        p2.map(calculate_perf_other_side.get_success_rate_from_labeled_events,
               [(elem, self.q_only_events) for elem in glob.glob(os.path.join(config.EVENTS_F_L_DATA_TEST, "*"))])
        p1.close()
        p2.close()
        p1.join()
        p2.join()
        correct_events_q_all = 0
        all_events_q_all = 0
        specific_events_1 = {}
        specific_events_1_all = {}
        i = 0
        while not self.q_all.empty():
            temp1, temp2 = self.q_all.get()
            if i ==0:
                specific_events_1 = temp1
                specific_events_1_all = temp2
            else:
                for key, value in temp1.iteritems():
                    specific_events_1[key] += value
                for key, value in temp2.iteritems():
                    specific_events_1_all[key] += value
            i += 1
        correct_events_q_only_events = 0
        all_events_q_only_events = 0
        specific_events = {}
        specific_events_all = {}
        i = 0
        while not self.q_only_events.empty():
            temp1, temp2 = self.q_only_events.get()
            if i == 0:
                specific_events = temp1
                specific_events_all = temp2
            else:
                for key, value in temp1.iteritems():
                    specific_events[key] += value
                for key, value in temp2.iteritems():
                    specific_events_all[key] += value
            i+=1
        success_rate_only_events = float(specific_events["events"]) / float(specific_events["all_events"])
        print("SUCCESS RATE NOTICED EVENTS: {0}".format(success_rate_only_events))
        del(specific_events["events"])
        del(specific_events["all_events"])
        print specific_events
        print specific_events_all
        for key in specific_events_all:
            print key, float(specific_events[key]) / float(specific_events_all[key])
        success_rate_all = float(specific_events_1["events"]) / float(specific_events_1["all_events"])
        print("SUCCESS RATE ALL EVENTS: {0}".format(success_rate_all))
        del(specific_events_1["events"])
        del(specific_events_1["all_events"])
        print specific_events_1
        print specific_events_1_all
        for key in specific_events_1_all:
            print key, float(specific_events_1[key]) / float(specific_events_1_all[key])

        print datetime.now() - self.now
        return success_rate_all


if __name__ == '__main__':
    me = MainExecutor(features=config.FEATURES)
    me.train_SVM_classifier()
    me.test_SVM_classfier()
    me.generate_event_file()
    me.run_sliding_window()
    me.collect_results()
    sys.exit(0)
    prev_value = 0
    reduced_features = config.FEATURES
    for j in range(1,len(config.FEATURES)):
        results = dict()
        for i in reversed(range(1, len(reduced_features))):
            temp_features = list(reduced_features)
            print "\n\nWITHOUT FEATURE: {0}".format(temp_features[i])
            del (temp_features[i])
            print "TEMP_FEATURES: ", temp_features
            me = MainExecutor(features=temp_features)
            me.train_SVM_classifier()
            me.test_SVM_classfier()
            me.generate_event_file()
            me.run_sliding_window()
            results[i] = me.collect_results()
        candidate = max(results.values())
        if candidate < prev_value:
            break
        prev_value = candidate
        i_candidate = [key for key, value in results.iteritems() if value == candidate][-1]
        print "deleting: ", reduced_features[i_candidate]
        del(reduced_features[i_candidate])
        print "REDUCED FEATURES: ", reduced_features
