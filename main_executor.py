import logging, os, shutil, glob
from multiprocessing import Pool, Process, Queue
import pandas as pd
from datetime import datetime
from sklearn import svm
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler

import calculate_perf_other_side
import calculate_performance
import config
import sliding_window

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
    def __init__(self, normalize_data = True, cross_validation=False):
        self.logger = loggerFactory.getLogger()
        self.now = datetime.now()
        self.clf = None
        self.scaler = None
        self.normalize_data = normalize_data
        self.cv = cross_validation
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
                                                             config.FEATURES)
        self.test_features_vector = sliding_window.features(self.test_data,
                                                            config.FEATURES)

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
            p1 = Pool(4)
            p1.map(_copy_train_set, train_set)
            p1.close()
            p1.join()
            p2 = Pool(4)
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
        self.clf = GridSearchCV(svr, parameters, n_jobs=4, verbose=0)
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
        pool = Pool(4)
        pool.map(sliding_window.generate_event_file,
                 glob.glob(os.path.join(self.test_raw_data, "raw*")))
        pool.close()
        pool.join()
        self.logger.info("Done!")

    def run_sliding_window(self):
        self.logger.info("Running sliding window...")
        args = []
        pool = Pool(4)
        for acc_file in glob.glob(os.path.join(self.test_raw_data, "raw*")):
            date = acc_file.split("_")[-1]
            gps_file = glob.glob(os.path.join(config.NORMALIZED_RAW_DATA, "gps_data_{0}*".format(date[:-6])))[0]
            args.append([self.clf, acc_file, gps_file, config.FEATURES, self.scaler])
        pool.map(sliding_window.sliding_window, args)
        pool.close()
        pool.join()
        self.logger.info("Done!")

    def collect_results(self):
        self.logger.info("Collecting results...")
        p1 = Process(target=calculate_perf_other_side.get_success_rate_from_labeled_events)
        p2 = Process(target=calculate_performance.get_success_rate_from_raw_events)
        p1.start()
        p2.start()
        p1.join()
        p2.join()
        self.logger.info("Done!")
        print datetime.now() - self.now


if __name__ == '__main__':
    me = MainExecutor()
    me.train_SVM_classifier()
    me.test_SVM_classfier()
    me.generate_event_file()
    me.run_sliding_window()
    me.collect_results()
