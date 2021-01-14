# import things
from flask_table import Table, Col,LinkCol, ButtonCol
import os
from pathlib import Path
from datetime import datetime
import app
import json
last_runs = {}
class ItemTable(Table):
    check = ButtonCol('Use', 'use_log', url_kwargs=dict(filename='name'), attr='check', column_html_attrs = {'class': 'no_pad'})
    name = Col('Name')
    size = Col('Size')
    date = Col('Upload Date')
    open = ButtonCol('Actions', 'download_logs', url_kwargs=dict(filename='name'), attr='open', column_html_attrs = {'class': 'no_pad'})
    delete = ButtonCol('', 'delete_log', url_kwargs=dict(name='name'), attr='delete'),
    status = Col('Status')
    

class ItemTableRuns(Table):
    name = Col('Name')
    label = Col('Label')
    date = Col('Creation Date')
    open = ButtonCol('Actions', 'download_runs', url_kwargs=dict(filename='name'), attr='open', column_html_attrs = {'class': 'no_pad'})
    logs = ButtonCol('', 'download_runs_logs', url_kwargs=dict(filename='name'), attr='logs')
    delete = ButtonCol('', 'delete_run', url_kwargs=dict(name='name'), attr='delete')

    


class Item(object):
    def __init__(self, check, name, size, date, open, delete, status):
        self.check = check
        self.name = name
        self.size = size
        self.date = date
        self.open = open
        self.delete = delete
        self.status = status

class ItemRuns(object):
    def __init__(self, name, label, date, open, logs, delete, check=True):
        self.name = name
        self.label = label
        self.date = date
        self.delete = delete
        self.open = open
        self.logs = logs
        self.check = check


def logs(path):

    listOfFile = os.listdir(path)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(path, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + logs(fullPath)
        else:
            size = os.path.getsize(fullPath)
            ctime = datetime.fromtimestamp(os.path.getctime(fullPath)).strftime('%Y-%m-%d  %H:%M:%S')
            check = 'O'
            delete = 'DELETE'
        
            selection = []
            with open('conf/selection.json') as file:
                selection = json.load(file)

            if entry in selection:
                check = '\u2713'
            if entry.split('.')[0] in ['0b679131-af02-4f1a-bba2-f8d1441b0ca7', '1ab2f9dd-62ff-4433-8d88-605744403ab2', '1c65003f-2c69-449a-9e8b-7dc8ddda07d4']:
                delete = 'empty'
            status = set_status(entry.split('.')[0])
            item = Item(check, entry, file_size_conversion(size), ctime, 'DOWNLOAD', delete, status)
            allFiles.append(item)
    return allFiles

def set_status(name):
    status = 'started'
    if os.path.exists('uploads/' + name + '/single_runs'):
        status = 'extracting..'
    if os.path.exists('uploads/' + name + '/resampled'):
        status = 'resampling..'
    if os.path.exists('uploads/' + name + '/models'):
        model_status = ''
        if os.path.exists('uploads/' + name + '/models/lstm/status'):
            model_status = open('uploads/' + name + '/models/lstm/status').read()
        status = 'training models - ' + model_status
    if os.path.exists('uploads/' + name + '/generated_logs'):
        total = len(os.listdir('uploads/resampled/Axis_X_aaLoad'))
        current = len(os.listdir('uploads/' + name + '/generated_logs'))
        status = 'embedding data into log files ' + str(current) + '/' + str(total)

    if not os.path.exists('uploads/' + name):
        if name in last_runs:
            status = 'last run finished at ' + last_runs[name]
        else:
            status = ''
    return status
    

def runs(path):
    listOfFile = sorted(os.listdir(path))
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(path, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + logs(fullPath)
        else:
            delete = 'DELETE'
            if entry.split('.')[0] in ['0b679131-af02-4f1a-bba2-f8d1441b0ca7_1', '1ab2f9dd-62ff-4433-8d88-605744403ab2_1', '1c65003f-2c69-449a-9e8b-7dc8ddda07d4_1']:
                delete = 'empty'

            run_index = entry.split('_')[1].split('.')[0]
            label = 'Run ' + run_index
            ctime = datetime.fromtimestamp(os.path.getctime(fullPath)).strftime('%Y-%m-%d  %H:%M:%S')
            last_runs[entry.split('.')[0].split('_')[0]] = ctime 
            item = ItemRuns(entry.split('.')[0], label, ctime, 'EVALUATE', 'DOWNLOAD GEN LOGS', delete)
        allFiles.append(item)
    return allFiles

def file_size_conversion(size):
    if size/(1024*1024*1027) >= 1:
        return '{:.2f}'.format(size/(1024*1024*1024)) + ' GiB'
    elif size/(1024*1024) >= 1:
        return '{:.2f}'.format(size/(1024*1024)) + ' MiB'
    elif size/1024 >= 1:
        return '{:.2f}'.format(size/1024) + ' KiB'
    return '{:.2f}'.format(size) + ' Bytes'

def create_logs_table():

    items = logs('uploads/logs')
    table_items = ItemTable(items).__html__()
    table_items = table_items.replace('/delete_log', 'delete_log')
    table_items = table_items.replace('/uploads/logs', 'uploads/logs')
    table_items = table_items.replace('/use_log', 'use_log')
    table_items = table_items.replace('<button type="submit">empty</button>', '')
    return table_items

def create_runs_table():

    items = runs('uploads/html')
    table_items = ItemTableRuns(items).__html__()
    table_items = table_items.replace('/delete_run', 'delete_run')
    table_items = table_items.replace('/uploads/runs', 'uploads/runs')
    table_items = table_items.replace('/uploads/runs/logs', 'uploads/runs/logs')
    table_items = table_items.replace('<button type="submit">empty</button>', '')
    return table_items

