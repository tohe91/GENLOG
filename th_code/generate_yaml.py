import yaml
import os
import numpy as np
import pandas as pd
import glob
from datetime import datetime
from datetime import timedelta
from zipfile import ZipFile 

path = os.path.dirname(__file__)
path2 = os.path.relpath('../templates', path)
base_path = path2 + '/logs/'
folder_path = ''
output = []

def get_data(path, path2, path3, metrics, filename):   

    print("yaml start")    

    for i in range(len(metrics)):
        metrics[i] = metrics[i].replace('_', '/')


    datetimeFormat = '%Y-%m-%dT%H-%M-%S'
    now = datetime.now()
    stamp = now.strftime(datetimeFormat)
    folder_path = path3

    length = int(len(os.listdir(path)) / len(metrics))

    for i in range(length):
        dfs = {}
        for metric in metrics:
            
            filename2 = '_'.join(filename.split('_')[:-1]) + '_' + metric.replace('/', '_') + '_' + str(i) + '.csv'
            dfs[metric] = pd.read_csv(path + filename2, header=None)   
            
        write_back(dfs, metrics, folder_path, filename + '-genlog' + str(i))
         
    with ZipFile(path2 + filename + '.zip','w') as zip: 
        for file in os.listdir(path3): 
            zip.write(path3 + file, os.path.basename(path3 + file)) 
    

    print('\n')
    print("yaml end")  
    print("--------------------------------")
    return folder_path


def extract_first_last(metrics):
    starts = list(np.zeros(len(metrics)))
    ends = list(np.zeros(len(metrics)))
    numof = list(np.zeros(len(metrics)))
    time_steps = list(np.zeros(len(metrics)))

    datetimeFormat = '%Y-%m-%dT%H:%M:%S.%f'
   
    with open('uploads/templates/batch15.yaml') as stream:
        docs = yaml.load_all(stream, Loader=yaml.SafeLoader)
        for doc in docs:
            for k,v in doc.items():      
                if 'data' in v:  
                    if 'data_receiver' in v['data']:         
                        if v['data']['data_receiver'] != None:
                            for v2 in v['data']['data_receiver']: 
                                if v2['data'] != None:
                                    for v3 in v2['data']: 
                                        for k in range(len(metrics)):
                                            if v3['name'] == metrics[k]:
                                                timestamp = v3['timestamp'][:-6]
                                                if starts[k] == 0:
                                                    starts[k] = datetime.strptime(timestamp, datetimeFormat)
                                                ends[k] = datetime.strptime(timestamp, datetimeFormat)
                                                numof[k] = numof[k] + 1
    
    for i in range(len(metrics)):
        diff = ends[i]- starts[i]
        time_steps[i] = diff.microseconds / numof[i]

    return [starts, ends, time_steps]


def resample(data, metrics):

    first_last_steps = extract_first_last(metrics)

    dfs = {}
    i = 0
    for key in metrics:
        df = data[key]
      #  df.index = pd.to_datetime(df.index)
      #  print('start:', first_last_steps[0][i])
        df['timestamp'] = first_last_steps[0][i]
        tdelta = pd.to_timedelta(df.index*100, unit="ms")
        df['timestamp'] = df['timestamp'] + tdelta
        df.index = df['timestamp']
        df = df.drop('timestamp', axis=1)
        df.index = pd.to_datetime(df.index)
        df = df.resample(str(int(first_last_steps[2][i])) + 'L').pad()
        df = df.reset_index()
        df[0] = df['timestamp']
        df = df.drop(['timestamp'], axis=1)
    #    print(int(first_last_steps[2][i]))
    #    print(df.head())
    #    print()
        dfs[key] = df
        i += 1
    return dfs
   
def Sort(li):
    first = li.pop(0)
    li = sorted(li, key = lambda x: x[1])   
    li.insert(0,first)
    return li 


def write_back(data, metrics, folder_path, filename2, file = None, depth = 0, f = None):
    datetimeFormat = '%Y-%m-%dT%H-%M-%S'
    now = datetime.now()
    stamp = now.strftime(datetimeFormat)
    dump_file = open(folder_path + filename2 + '.xes.yaml',"w")
    data = resample(data, metrics)
    
    metric_indecies = list(np.ones(len(metrics)))
    with open('uploads/templates/batch15.yaml') as stream:
        docs = yaml.load_all(stream, Loader=yaml.SafeLoader)
        for doc in docs:
            for k,v in doc.items():      
                if 'data' in v:  
                    if 'data_receiver' in v['data']:         
                        if v['data']['data_receiver'] != None:
                            for v2 in v['data']['data_receiver']: 
                                if v2['data'] != None:
                                    for v3 in v2['data']: 
                                        for k in range(len(metrics)):
                                            #print('k', k)
                                            if v3['name'] == metrics[k]:
                                               # print(data[metrics[k]][1][metric_indecies[k]])
                                                if len(data[metrics[k]][1]) > metric_indecies[k]:
                                                    v3['value'] = float(data[metrics[k]][1][metric_indecies[k]])
                                                    v3['timestamp'] = str(data[metrics[k]][0][metric_indecies[k]]).replace(' ', 'T')[:-3] + '+01:00'
                                                metric_indecies[k] = metric_indecies[k] + 1
            dump_file.write("---\n")
            yaml.dump(doc, dump_file)
        yaml.dump_all(documents=docs, stream=stream)
      #  yaml.dump_all(docs, dump_file)
    dump_file.close()
                                            

   

    
    