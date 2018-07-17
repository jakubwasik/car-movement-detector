import glob
import os

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import re
from scipy.signal import butter, lfilter, freqz

PATH = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data"
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\normalized_data\skret_w_prawo_2018-05-25-18-38-45_2018-05-25_18_53_04.csv"


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y


def error(raw_data, linear_coeff, last_data):
    t = np.arange(0, len(raw_data) * 0.02, 0.02)
    t = t[0:len(raw_data)]
    lin_x = linear_coeff * t
    raw_data = raw_data - last_data
    error = np.sum((lin_x - raw_data) ** 2)
    return error

def error_alternative(raw_data, linear_coeff, last_data):
    t = np.arange(0, len(raw_data) * 0.02, 0.02)
    t = t[0:len(raw_data)]
    lin_x = linear_coeff * t
    raw_data = raw_data - raw_data[0]
    error = np.sum((lin_x - raw_data) ** 2)
    return error



def process_event(data):
    linear_approximation = np.zeros(len(data))
    coeff_arr = []
    x = np.array(data)
    last_data = data[0]
    for i in range(0, len(data), SIZE):
        e_prev = error_alternative(x[i:i + SIZE], base[0], last_data)
        best_coeff = base[0]
        for elem in base[1:]:
            e = error_alternative(x[i:i + SIZE], elem, last_data)
            # print e_prev, elem, e
            if np.abs(e) < np.abs(e_prev):
                best_coeff = elem
            e_prev = e
        t = np.arange(0, len(x[i:i + SIZE]) * 0.02, 0.02)
        t = t[0:len(x[i:i + SIZE])]
        coeff_arr.append(best_coeff)
        linear_approximation[i:i + SIZE] = t * best_coeff + x[i]#+  last_data
        # print linear_approximation
        if i + SIZE > len(data):
            last_data = linear_approximation[SIZE - 1]
            #plt.plot(np.arange(i, len(data)), linear_approximation[i:i + SIZE], color="black")
        else:
            last_data = linear_approximation[i + SIZE - 1]
            #plt.plot(np.arange(i, i + SIZE), linear_approximation[i:i + SIZE], color="black")
    return coeff_arr


to_str = {1.7: "a", 1: "b", 0.56: "c", 0: "d", -0.56: "e", -1: "f", -1.7: "g"}


def make_str_from_coeff(coeff_arr):
    string = ""
    for coeff in coeff_arr:
        string += to_str[coeff]
    return string


SIZE = 60

# data["x"].plot()

counter = 0
all = 0
base = [1.7, 1, 0.56, 0, -0.56, -1, -1.7]
if __name__ == "__main__":
    pass
    """
    for file in glob.glob(os.path.join(PATH, "*prawo_2018*")):
        data = pd.read_csv(file)
        data["x"].plot()
        data["x"] = butter_lowpass_filter(data["x"], 3, 50)
        data["x"].plot()
        coeff_arr = process_event(data)
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
    
        out = re.search("^d?c?[ab]+?[abcd]*?[defg]+$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        #plt.show()
    print "Total result: %f" % (float(counter)/float(all))
    counter = 0
    all = 0
    for file in glob.glob(os.path.join(PATH, "*lewo_2018*")):
        data = pd.read_csv(file)
        data["x"].plot()
        data["x"] = butter_lowpass_filter(data["x"], 3, 50)
        data["x"].plot()
        coeff_arr = process_event(data)
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
    
        out = re.search("^d?e?[gf]+?[fged]*?[dcba]+$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        #plt.show()
    print "Total result: %f" % (float(counter)/float(all))
    
    counter = 0
    all = 0
    
    for file in glob.glob(os.path.join(PATH, "*prawy_2018*")):
        data = pd.read_csv(file)
        data["x"].plot()
        data["x"] = butter_lowpass_filter(data["x"], 3, 50)
        data["x"].plot()
        coeff_arr = process_event(data["x"])
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
        out = re.search("^d?[bc]+?[dbc]*?[defg]+[abcd]+?[eg]?$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        plt.show()
    print "Total result: %f" % (float(counter)/float(all))
    
    counter = 0
    all = 0
    for file in glob.glob(os.path.join(PATH, "*_2018*")):
        data = pd.read_csv(file)
        data["x"].plot()
        data["x"] = butter_lowpass_filter(data["x"], 3, 50)
        data["x"].plot()
        coeff_arr = process_event(data)
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
        out = re.search("^d?[fe]+?[dfe]*?[dcba]+[gfed]+?[ab]?$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        #plt.show()
    print "Total result: %f" % (float(counter)/float(all))
    
    counter = 0
    all = 0
    for file in glob.glob(os.path.join(PATH, "hamowanie_2018*")):
        data = pd.read_csv(file)
        data["z"].plot()
        data["z"] = butter_lowpass_filter(data["z"], 3, 50)
        data["z"].plot()
        coeff_arr = process_event(data["z"])
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
        out = re.search("^d?[abc]+?[abcd]*?[defg]+[abc]?$", string_to_match)
        #out = re.search("^d?[abc]{0,2}[defg]+[abc]?$", string_to_match) more restict
        #out = re.search("^d?[abc]{0,2}[defg]+[abc]?$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        #plt.show()
    print "Total result: %f" % (float(counter)/float(all))
    to_str = {1.7: "a", 1: "b", 0.56: "c", 0: "d", -0.56: "e", -1: "f", -1.7: "g"}
    
    counter = 0
    all = 0
    for file in glob.glob(os.path.join(PATH, "za*ch_2018*")):
        data = pd.read_csv(file)
        data["z"].plot()
        data["z"] = butter_lowpass_filter(data["z"], 3, 50)
        data["z"].plot()
        coeff_arr = process_event(data["z"])
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
        out = re.search("^d?[abc]+?[abcdefg]{3,10}[efg]+[cda]?$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        #plt.show()
    print "Total result: %f" % (float(counter)/float(all))
       """
    counter = 0
    all = 0
    for file in glob.glob(os.path.join(PATH, "prz*ch_2018*")):
        data = pd.read_csv(file)
        data["z"].plot()
        data["z"] = butter_lowpass_filter(data["z"], 3, 50)
        data["z"].plot()
        coeff_arr = process_event(data["z"])
        string_to_match = make_str_from_coeff(coeff_arr)
        #print data["x"][i:i+15]
    
        out = re.search("^[efg]+?[abcd]+?[efgd]+?[abcd]+$", string_to_match)
        print string_to_match
        if out:
            print "Ok: ", out.group()
            counter +=1
        all += 1
        plt.show()
    print "Total result: %f" % (float(counter)/float(all))
