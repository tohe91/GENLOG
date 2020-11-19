from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import save_model
from tensorflow.keras.models import load_model
from tensorflow.keras.callbacks import EarlyStopping
from numpy import array
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import glob
import tensorflow as tf
import random
import os
import th_code.generate_yaml as generate_yaml




def get_resampled_data(path, file):
    return glob.glob(path + file)


def split_series(series, steps):
    X = list()
    y = list()
    for i in range(len(series)):
        offset = i + steps
        if offset < len(series)-1:
            X.append(series[i:offset])
            y.append(series[offset])
    return array(X), array(y)

def split_path(path):
    if '\\' in path:
        return path.split('\\')
    return path.split('/')

def train_models(path, file):

#    physical_devices = tf.config.list_physical_devices('GPU') 
#    tf.config.experimental.set_memory_growth(physical_devices[0], True)

    csv_files = get_resampled_data(path, file)
    
    for csv_file in csv_files:
        file_name = split_path(csv_file)[-1][:-4]
     
        if not glob.glob('uploads/models/lstm/' + file_name):
              
            df = pd.read_csv(csv_file, header=None)
            raw_seq = df[1].to_numpy()
            n_steps = 3
            X, y = split_series(raw_seq, n_steps)
            n_features = 1
            X = X.reshape((X.shape[0], X.shape[1], n_features))

            model = Sequential()
        #  model.add(LSTM(50, activation='relu', return_sequences=True, input_shape=(n_steps, n_features)))
        #  model.add(LSTM(50, activation='relu'))
            model.add(LSTM(50, activation='relu', input_shape=(n_steps, n_features)))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mse')
            callbacks = [EarlyStopping(monitor='loss', patience=10)]
            model.fit(X, y, epochs=100, verbose=0, callbacks=callbacks)
         #   model.save('../models/lstm/test')
            model_path = 'uploads/models/lstm/' + file_name
            print(model_path)
         #   os.mkdir(model_path)
            save_model(model, model_path)


def generate_data(path, files):
    
    for file in files:

        if not glob.glob('uploads/generated/' + file + '.csv'):

            resampled_path = 'uploads/resampled/' + file + '.csv'
            model_path = path + file

            df = pd.read_csv(resampled_path, header=None)

            n_features = 1
            raw_seq = df[1].to_numpy()
            n_steps = 3
            X2, y2 = split_series(raw_seq, n_steps)
            X2 = X2.reshape((X2.shape[0], X2.shape[1], n_features))
            x_input2 = X2

            plt.figure(figsize=(30,10))

            model = load_model(model_path)

            yhat = model.predict(x_input2, verbose=0)
            
            plt.scatter(range(len(y2)), y2, color='red', marker='x')
            plt.scatter(range(len(yhat)), yhat, color='blue', alpha=0.2, marker='o')

            pd.DataFrame(yhat).to_csv('uploads/generated/' + file + '.csv', header=None)

        #return generate_yaml.get_data(data.keys())



def run(path, files):   
    print("lstm training start")    
    for file in files:                     
        train_models(path, file)
    print('\n')
    print("lstm training end")  
    print("--------------------------------")
