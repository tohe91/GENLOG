import th_code.time_series_single_runs as time_series_single_runs
import th_code.time_series_resample as time_series_resample
import th_code.lstm as lstm
#import measuring
import sys
import os
import json

arg1 = 4
arg2 = 16

def read_metrics():
    path = os.path.dirname(__file__)
    new_path = os.path.relpath('../conf/', path)
    with open(new_path + '/metrics.json') as file:
        metrics = json.load(file)
        return [metric.replace('/', '_') for metric in metrics]

try:
    arg1 = int(sys.argv[1])

    arg2 = int(sys.argv[2])

   # measuring.run(arg1,arg2)

 #   time_series_single_runs.run(read_metrics(), arg1, arg2)
    time_series_resample.run(read_metrics(), arg1, arg2)
 #   time_series_aggregations_outliers.run(arg1, arg2)
    lstm.run(read_metrics(), arg1, arg2)
    
except ValueError as err:
    print(err)


