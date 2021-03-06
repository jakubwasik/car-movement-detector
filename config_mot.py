BASE = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\\"
NORMALIZED_LABELED_TRAIN_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\normalized_labeled_train_data"
NORMALIZED_LABELED_TEST_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\normalized_labeled_test_data"
# FILE = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\DONOTTOUCH\labeled_data"
# FILE_TEST = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\DONOTTOUCH\test_data"
DATE_FORMAT_MS = '%d-%m-%Y %H:%M:%S:%f'
EVENTS_F_R_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\tests\events_from_raw_data"
EVENTS_F_R_DATA_TEST = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\tests\events_from_raw_data_test"
EVENTS_F_L_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\tests\events_from_labeled_data"
EVENTS_F_L_DATA_TEST = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\tests\events_from_labeled_data_test"
NORMALIZED_RAW_DATA_TEST= r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\normalized_raw_data_test"
NORMALIZED_RAW_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\normalized_raw_data"
NORMALIZED_RAW_DATA_TEST_COPY= r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\normalized_raw_data_test - kopia"

WORKSPACE_NORMALIZED_LABELED_TRAIN_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\workspaces\workspace_normalized_labeled_train_data"
WORKSPACE_NORMALIZED_LABELED_TEST_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\workspaces\workspace_normalized_labeled_test_data"
WORKSPACES_NORMALIZED_RAW_DATA_TEST= r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\workspaces\workspace_normalized_raw_data_test"
WORKSPACES_NORMALIZED_RAW_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\workspaces\workspace_normalized_raw_data"
FEATURES = ["sin_params", "mean_x", "std_x", "mean_z", "std_z", "speed_mean", "speed_std",
            "range_speed", "energy_x", "energy_z", "signChange","zero_crossings",
            "range_z", "range_x", "coeff_x",
            "coeff_z", "coeff_x_1", "freq_x", "freq_z", "iqr", "var_x", "var_z",
             "min_z", "max_z", "min_x", "max_x", "skew",
             "autocorr_peaks_x", "fft_peaks_x", "psd_peaks_x",
            "autocorr_peaks_z", "fft_peaks_z", "psd_peaks_z", "coeff_speed","mean_dx", "mean_dz","std_dx","std_dz","zero_crossings_dx", "energy_dz","energy_dx",
            "kurtosis",  "signal_to_noise_x", "signal_to_noise_z", "percentile_x_25",
            "percentile_x_50", "percentile_x_75", "percentile_z_25", "percentile_z_50"]
FEATURES = ['mean_x', 'mean_z', 'std_z', 'speed_mean', 'energy_x', 'signChange',  'coeff_x', 'freq_z', 'var_x', 'var_z', 'max_z', 'min_x', 'skew', 'fft_peaks_x', 'psd_peaks_x', 'autocorr_peaks_z', 'fft_peaks_z', 'psd_peaks_z', 'std_dx', 'energy_dx', 'kurtosis', 'percentile_z_25']
FREQ = 12
WINDOW_SIZE = 5.0
WINDOW_SIZE_SAMPLES = int(round(WINDOW_SIZE * 50))

# specific for events_from_labeled_data.py
DATE_FORMAT_FILE = '%Y-%m-%d_%H_%M_%S'
#calculate_perf_other_side
DATE_FORMAT_MS_EVENT = '%Y-%m-%d %H:%M:%S.%f'

DNT_LABELED_DATA= r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\DONOTTOUCH\\labeled_data"
ALLIGNED_SPEED = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\alligned_speed"
DNT_TEST_DATA = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\DONOTTOUCH\test_data"
ALLIGNED_SPEED_TEST = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\alligned_speed_test"

REF_DATA_FILE = r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\ref_value"
DATA_TO_CV =r"C:\Users\PHVD86\Documents\praca_magisterska\car-movement-detector\sensor data\data_to_cv"
