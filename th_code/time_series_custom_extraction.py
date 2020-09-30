import yaml
import os
import json
import csv
import glob
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
    if (len(os.listdir('uploads/single_runs')) < len(metrics)):
        structure = ['data', 'data_receiver']
        last = 'data'
        kvs = ['name', 'value', 'timestamp']
    
        for file in files:
            print('processing file:', file)
            
            results = []
            for k in range(len(metrics)):
                results.append([["value", "timestamp"]]) 
            
            f = path2 / 'single_runs' / file[0:-9]

            with open(base_path / file, 'r') as stream:
                docs = yaml.load_all(stream, Loader=yaml.SafeLoader)
                count = 0
                for doc in docs:
                    
                    for k,v in doc.items(): 
                        if count > 0:
                            current = v
                            is_valid = True
                            for struct in structure:
                                if current != None:
                                    if struct in current:
                                        current = current[struct]
                                    else:
                                        is_valid = False
                                else:
                                    is_valid = False
                            if is_valid:    
                                if current != None:
                                    for sub in current:
                                        if sub[last] != None:
                                            for item in sub[last]:
                                            #    print('item', item)
                                            #    print('item:name', item[kvs[0]])
                                                timestamp = item[kvs[2]]
                                                for k in range(len(metrics)):
                                                    if item[kvs[0]] == metrics[k].replace('_', '/'):
                                                        results[k].append([float(item[kvs[1]]), timestamp])
                        count += 1

            
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
    