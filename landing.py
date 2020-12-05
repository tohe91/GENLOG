# import things
from flask_table import Table, Col,LinkCol, ButtonCol
import os
from pathlib import Path
from datetime import datetime
import app
import json

class ItemTable(Table):
    check = ButtonCol('Use', 'use_log', url_kwargs=dict(filename='name'), attr='check', column_html_attrs = {'class': 'no_pad'})
    name = Col('Name')
    size = Col('Size')
    date = Col('Upload Date')
    open = ButtonCol('Actions', 'download_logs', url_kwargs=dict(filename='name'), attr='open', column_html_attrs = {'class': 'no_pad'})
    delete = ButtonCol('', 'delete_log', url_kwargs=dict(name='name'), attr='delete')
    
    

class ItemTableRuns(Table):
    name = Col('Name')
    label = Col('Label')
    date = Col('Creation Date')
    open = ButtonCol('Actions', 'download_runs', url_kwargs=dict(filename='name'), attr='open', column_html_attrs = {'class': 'no_pad'})
    delete = ButtonCol('', 'delete_run', url_kwargs=dict(name='name'), attr='delete')

    


class Item(object):
    def __init__(self, check, name, size, date, open, delete = None):
        self.check = check
        self.name = name
        self.size = size
        self.date = date
        self.delete = delete
        self.open = open

class ItemRuns(object):
    def __init__(self, name, label, date, open, delete = None, check=True):
        self.name = name
        self.label = label
        self.date = date
        self.delete = delete
        self.open = open
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
          
            item = Item(check, entry, file_size_conversion(size), ctime, 'DOWNLOAD', delete)
            allFiles.append(item)
    return allFiles

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
            item = ItemRuns(entry, label, ctime, 'OPEN', delete)
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
    table_items = table_items.replace('<button type="submit">empty</button>', '')
    return table_items

