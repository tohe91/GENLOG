import json
import os
import th_code.lstm as lstm

path = os.path.dirname(__file__)
path_conf = os.path.relpath('../conf/', path)


def get_user_conf():
    user_batches = dict()
    user_metrics = dict()
    if os.path.exists(path_conf + '/user_conf/batches.json'):
        with open(path_conf + '/user_conf/batches.json') as f:
            user_batches = json.load(f)
    if os.path.exists(path_conf + '/user_conf/batches_metrics.json'):
        with open(path_conf + '/user_conf/batches_metrics.json') as f:
            user_metrics = json.load(f)
            user_metrics['batch6_Spindle-driveLoad'] = 'ready'
            
    return {'batches': user_batches, 'metrics': user_metrics}

def train_models(conf):
    lstm.train_handler(conf['metrics'])
    


train_models(get_user_conf())