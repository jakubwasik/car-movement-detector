import glob
import os
import re

import numpy as np
import pandas as pd
import scipy
import matplotlib.pyplot as plt
def get_rotation_matrix(a, b):
    a = a/ np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    #print a,b
    dot = np.matmul(a,b)
    cross = np.cross(a,b)
    print cross
    norm = lambda x: np.linalg.norm(x)
    G = np.array([[dot, -norm(cross), 0],
                  [norm(cross), dot, 0],
                  [0, 0, 1]])
    FFi = np.array([a, (b-dot*a)/norm(b-dot*a), np.cross(b,a)])
    FFi = np.transpose(FFi)
    return np.matmul(np.matmul(FFi, G),np.linalg.inv(FFi))

U =  get_rotation_matrix(np.array([0.1436521028, 9.71950125, -0.478840338]),np.array([0, 9.73234959014, 0]))
print U
print np.matmul(U,np.array([0.1436521028, 9.71950125, -0.478840338]))

"""
b = a.head(1000)
#b.plot()
#plt.show()
x_mean = b["x"][0:10].mean() * 1.0079785882269034
y_mean = b["y"][0:10].mean()* 1.0079785882269034
z_mean = b["z"][0:10].mean()* 1.0079785882269034
#print x_mean,y_mean,z_mean
alpha_z = scipy.arctan2(x_mean, y_mean)
alpha_x= scipy.arctan2(-z_mean,np.sqrt(x_mean*x_mean+y_mean*y_mean))
#yaw = scipy.arcco`s(y_mean/np.sqrt(x_mean*x_mean+y_mean*y_mean+x_mean*x_mean))

#print alpha_z * 180 / np.pi
#print alpha_x * 180 / np.pi
#print np.sqrt(x_mean*x_mean+y_mean*y_mean+ z_mean*z_mean)
"""


#Rz = np.array([[np.cos(yaw), - np.sin(yaw), 0],
#               [np.sin(yaw), np.cos(np.sin(yaw)), 0],
#               [0, 0, 1]])

#yaw -> y
#roll - z
#pitch - x
#print Ry
#wynik = Rz#*np.array(b["x"][1], b["y"][1], b["z"][1])
#print Rz, Rx
"""
U =np.array([[ 0.999890995269873,  -0.014760269498081,   0.000363349096881],
             [0.014760269498081,   0.998679831625406,  -0.049200897847438],
             [0.000363349096881,   0.049200897847438 ,  0.998788836355533]])

print np.matmul(U, np.array([x_mean,y_mean,z_mean]))
print np.matmul(np.linalg.inv(U), np.array([0,9.81,0]))
#c = np.linalg.inv(np.matmul(Rz, Rx))
#print  np.matmul(np.array([x_mean, y_mean, z_mean]),c)
#print wynik*np.array([b["x"][0], b["y"][0], b["z"][0]])
"""