import os, json
import th_code.time_series_single_runs as time_series_single_runs
import th_code.time_series_custom_extraction as time_series_custom_extraction
import th_code.time_series_resample as time_series_resample
import th_code.lstm as lstm



def read_metrics():
    path = os.path.dirname(__file__)
    new_path = os.path.relpath('./conf/', path)
    with open(new_path + '/metrics.json') as file:
        metrics = json.load(file)
        return [metric.replace('/', '_') for metric in metrics] 
   
def extract():

    if not os.path.exists("uploads/logs/"):
        os.makedirs("uploads/logs/")
    if not os.path.exists("uploads/single_runs/"):
        os.makedirs("uploads/single_runs/")    
    if not os.path.exists("uploads/resampled/"):
        os.makedirs("uploads/resampled/")
    if not os.path.exists("uploads/models/"):
        os.makedirs("uploads/models/")
    if not os.path.exists("uploads/models/lstm"):
        os.makedirs("uploads/models/lstm")
    if not os.path.exists("uploads/generated"):
        os.makedirs("uploads/generated")

    time_series_custom_extraction.run(read_metrics())
    return "extraction finished"  
 
def resample():
    time_series_resample.run('uploads/single_runs/', os.listdir('uploads/single_runs/'))
    return "resampling finished"  
 
def train():
    lstm.run('uploads/resampled/', os.listdir('uploads/resampled/'))
    return "training finished"   

def gen():
    lstm.generate_data('uploads/models/lstm/',  os.listdir('uploads/models/lstm/'))
    return "generation finished"    