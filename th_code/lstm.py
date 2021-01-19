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
from sklearn.preprocessing import normalize
from matplotlib.lines import Line2D



def get_resampled_data(path, file):
    return glob.glob(path + file)

def get_all_resampled_data(path, file):
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

def train_models(path, path2, file):

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
            model_path = path2 + file_name
         
         #   os.mkdir(model_path)
            save_model(model, model_path)


def reshape_X(csv_file):
    df = pd.read_csv(csv_file, header=None)
    raw_seq = df[1].to_numpy()
    n_steps = 3
    X, y = split_series(raw_seq, n_steps)
    n_features = 1
    return X.reshape((X.shape[0], X.shape[1], n_features))

def train_models2(path, path2, path3, file, filename):

    physical_devices = tf.config.list_physical_devices('GPU') 
    if (len(physical_devices) > 0):
        tf.config.experimental.set_memory_growth(physical_devices[0], True)

    csv_files = get_resampled_data(path, file)

    



    for csv_file in csv_files:
        file_name = split_path(csv_file)[-1][:-4]
        csv_files_all = os.listdir('uploads/resampled/' + '_'.join(file_name.split('_')[1:]))

        y_label = 'motor load (in W)'
        if 'Torque' in file:
            y_label = 'motor torque (in Nm)'
        if 'Speed' in file:
            y_label = 'motor speed'
  
        df = pd.read_csv(csv_file, header=None)
        raw_seq = df[1].to_numpy()
        n_steps = 3
        X, y = split_series(raw_seq, n_steps)
        n_features = 1
        X = X.reshape((X.shape[0], X.shape[1], n_features))

        custom_lines = [Line2D([0], [0], color='red', lw=4), Line2D([0], [0], color='blue', lw=4)]
        plt.rcParams.update({'font.size': 24})
        fig, ax = plt.subplots(figsize=(30,9))
        ax.legend(custom_lines, ['real data', 'generated data'])
        ax.set(xlabel='time (100ms)', ylabel=y_label)
        num_of_models = len(csv_files_all)
        for i in range(num_of_models):
            model = Sequential()
            model.add(LSTM(15, activation='relu', input_shape=(n_steps, n_features)))
            model.add(Dense(1))
            model.compile(optimizer='adam', loss='mse')
            callbacks = [EarlyStopping(monitor='loss', patience=5)]
            model.fit(X, y, epochs=12, verbose=0, callbacks=callbacks)

            X_input = reshape_X('uploads/resampled/' + '_'.join(file_name.split('_')[1:]) + '/' + csv_files_all[i])
            yhat = model.predict(X_input, verbose=0)
            
            pd.DataFrame(yhat).to_csv(path3 + file_name + '_' + str(i) + '.csv', header=None)

            #   ax.plot(range(len(yhat)), yhat, color='blue', linewidth=4)
            ax.scatter(range(len(yhat)), yhat, color='blue')
            with open(path2 + '/status', 'w') as file:
                file.write('_'.join(file_name.split('_')[1:]) + ': ' + str(i+1) + '/' + str(num_of_models))

        #   ax.plot(range(len(y)), y, color='red', linewidth=3, label='original data')
        ax.scatter(range(len(y)), y, color='red', label='original data')
        fig.savefig('uploads/vis/' + filename + '.pdf')
        fig.savefig('uploads/vis/' + filename + '.png')

def generate_data(path, path2, path3, files):
    
    for file in files:

        resampled_path = path3 + file + '.csv'
        model_path = path + file

        df = pd.read_csv(resampled_path, header=None)

        n_features = 1
        raw_seq = df[1].to_numpy()
        n_steps = 3
        X2, y2 = split_series(raw_seq, n_steps)
        X2 = X2.reshape((X2.shape[0], X2.shape[1], n_features))
        x_input2 = X2


        custom_lines = [Line2D([0], [0], color='blue', lw=4),
                        Line2D([0], [0], color='red', lw=1)]

        fig, ax = plt.subplots(figsize=(30,10))
        
        ax.legend(custom_lines, ['real data', 'generated data'])
        #plt.figure(figsize=(30,10))
        ax.scatter(range(len(y2)), y2, color='blue', alpha=0.2, marker='o')
        
        model = load_model(model_path)
        yhat_container = []
        for i in range(10):
            yhat = model.predict(x_input2, verbose=0)
            yhat_container.append(yhat)
            ax.scatter(range(len(yhat)), yhat, color='red', marker='x')
            

            #pd.DataFrame(yhat).to_csv(path2 + '/' + file + '_' + str(i) + '.csv', header=None)
       

        #return generate_yaml.get_data(data.keys())


def epochs(path, path2, file):

#    physical_devices = tf.config.list_physical_devices('GPU') 
#    tf.config.experimental.set_memory_growth(physical_devices[0], True)

    csv_files = get_resampled_data(path, file)
    
    for csv_file in csv_files:
        file_name = split_path(csv_file)[-1][:-4]
     
        if not glob.glob('uploads/models/lstm/' + file_name):

            y_label = 'motor load (in W)'
            if 'Torque' in file:
                y_label = 'motor torque (in Nm)'
            if 'Speed' in file:
                y_label = 'motor speed'
              
            df = pd.read_csv(csv_file, header=None)
            raw_seq = df[1].to_numpy()
            n_steps = 3
            X, y = split_series(raw_seq, n_steps)
            n_features = 1
            X = X.reshape((X.shape[0], X.shape[1], n_features))

           
            num_of_models = 8 
            for i in range(num_of_models):
                custom_lines = [Line2D([0], [0], color='red', lw=4), Line2D([0], [0], color='blue', lw=4)]
                plt.rcParams.update({'font.size': 24})
                fig, ax = plt.subplots(figsize=(30,9))
                ax.legend(custom_lines, ['real data', 'generated data'])
                ax.set(xlabel='time (100ms)', ylabel=y_label)

                model = Sequential()
                model.add(LSTM(5, activation='relu', input_shape=(n_steps, n_features)))
                model.add(Dense(1))
                model.compile(optimizer='adam', loss='mse')
                callbacks = [EarlyStopping(monitor='loss', patience=5)]
                model.fit(X, y, epochs=i, verbose=0, callbacks=callbacks)
               
                yhat = model.predict(X, verbose=0)
    
               # ax.plot(range(len(yhat)), yhat, color='blue', linewidth=4)
                ax.scatter(range(len(yhat)), yhat, color='blue')
                with open('uploads/' + file_name.split('_')[0] + '/models/lstm/status', 'w') as file:
                    file.write('_'.join(file_name.split('_')[1:]) + ': ' + str(i+1) + '/' + str(num_of_models))

                ax.scatter(range(len(y)), y, color='red', label='original data')
             #   ax.plot(range(len(y)), y, color='red', linewidth=3, label='original data')
                fig.savefig('uploads/vis/' + file_name + '.pdf')
                fig.savefig('uploads/vis/' + file_name + '.png')


def run_epoch(path, path2, files):   
    print("epochs start")    
    for file in files:                     
        epochs(path, path2, file)
    print('\n')
    print("epochs end")  
    print("--------------------------------")

def run(path, path2, path3, files, filename):   
    print("lstm training start")    
    for file in files:                     
        train_models2(path, path2, path3, file, filename)
    print('\n')
    print("lstm training end")  
    print("--------------------------------")
