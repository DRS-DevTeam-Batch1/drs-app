import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

data = [
    {"x": 2.4, "y": 1.2, "z": 0.6, "t": 0.1},
    {"x": 2.2, "y": 1.0, "z": 0.4, "t": 0.1},
]

# Or


df = pd.read_csv('input.csv') #contains list of inputs like x,y,z,t


df.dropna(inplace=True)


scaler = MinMaxScaler()

df[['x', 'y', 'z']] = scaler.fit_transform(df[['x', 'y', 'z']])
