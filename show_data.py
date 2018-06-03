import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
FILE = r"C:\Users\kuba\Desktop\sensor data\labeled_data\zmiana_pasa_na_prawy_2018-05-08-18-56-10_2018-05-08_18_56_39.csv"
data = pd.read_csv(FILE, sep=",",
                   dtype={"x": np.float, "y": np.float, "z": np.float})
print data.head(50)

x= np.array(data["x"], dtype=np.float)
plt.figure(figsize=(8, 5), dpi=80)
plt.plot(data["time"],x)
plt.ylim(x.min()-2, x.max()+2)

y= np.array(data["y"])
plt.figure(figsize=(8, 5), dpi=80)
plt.plot(y)
plt.ylim(y.min()-2, y.max()+2)

z= np.array(data["z"])
plt.figure(figsize=(8, 5), dpi=80)
plt.plot(z)
plt.ylim(z.min()-2, z.max()+2)
plt.yticks(np.linspace(z.min(), z.max(), 5, endpoint=True))
plt.show()