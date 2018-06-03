import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import glob
import matplotlib.pyplot as plt
FILE = r"C:\Users\kuba\Desktop\praca magisterska\sensor data\DONOTTOUCH\sensors"
#data = pd.read_csv(FILE, sep=",",
#                   dtype={"x": np.float, "y": np.float, "z": np.float})

for file in glob.glob(os.path.join(FILE,"raw_data_2018-05-30-16-32-53.csv")):
    print file
    data = pd.read_csv(file, sep=";")
    #data =  data[["time",'x','y','z']]
    new_data =  data[data.index.values % 2 == 0]
   # print data
    new_data.to_csv(file, sep= ';',index=False)

    #prev_speed = data["speed"][0]
    ##    if data["speed"][i] == 0 and abs(data["speed"][i] - prev_speed) > 9.5:
     ##       data["speed"][i] = prev_speed
      #  prev_speed = data["speed"][i]
    #data.to_csv(file, sep=",")

