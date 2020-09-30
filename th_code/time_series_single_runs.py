import yaml
import os
import json
import csv
from datetime import datetime
from pathlib import Path

path = os.path.dirname(__file__)
path2 = Path(path).parent / 'uploads'
print(path2.parent)
#path2 = os.path.relpath('../uploads', path)
base_path = path2 / 'logs'

output = []
def machining():
    files = []
    
    for file in os.listdir(base_path):

        if file.endswith(".yaml"):
            
            fp = open(base_path / file)
            for j, line in enumerate(fp):
                if j == 29:
                  
                    if 'GV12 Turn Machining' in line:
                        files.append(file)
                elif j > 29:
                    break
            fp.close()
                               


    if not os.path.exists(path2 / 'machining'):
        os.makedirs(path2 / 'machining')
    f = path2 / 'machining' / 'machining_files.json'
    writeJSON(f ,files)
    return files


def Sort(li):
    first = li.pop(0)
    li = sorted(li, key = lambda x: x[1])   
    li.insert(0,first)
    return li 

def writeJSON(file, output):
    with open(file, 'w') as file:
        json.dump(output, file)

def writeOutput(file, output):
    with open(file,"w+") as f:
        f.write(output)

    with open(file,"w+") as file:
        yaml.dump(output, file)

def write_csv(file, output):
    with open(file, 'w+', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(output)

def extract(metrics, file = None, depth = 0, f = None):

    files = machining()
  
    for file in files:
        print('processing file:', file)
        results = []
        for k in range(len(metrics)):
            results.append([["value", "timestamp"]]) 
        
        if not os.path.exists(path2 / 'single_runs'):
            os.makedirs(path2 / 'single_runs')
        f = path2 / 'single_runs' / file[0:-9]

        with open(base_path / file, 'r') as stream:
            docs = yaml.load_all(stream, Loader=yaml.SafeLoader)
            for doc in docs:
                for k,v in doc.items():      
                    if 'data' in v:  
                        if 'data_receiver' in v['data']:         
                            if v['data']['data_receiver'] != None:
                                for v2 in v['data']['data_receiver']: 
                                    if v2['data'] != None:
                                        for v3 in v2['data']: 
                                            timestamp = v3['timestamp']
                                          #  if i > 12:
                                              #  timestamp = v3['timestamp'][:-6]
                                            for k in range(len(metrics)):
                                                if v3['name'] == metrics[k].replace('_', '/'):
                                                    results[k].append([float(v3['value']), timestamp])
        
        for k in range(len(metrics)):
            result = results[k]
            if len(result) > 2:
                result = Sort(result) 
                metric = metrics[k].replace('/', '_')
                write_csv(str(f) + "_" + metric + ".csv", result)

       
                                     
def run(metrics):   
    print("single runs start")                                   
    extract(metrics)
    print("single runs end")  
    print("--------------------------------")
    