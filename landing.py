# import things
from flask_table import Table, Col,LinkCol, ButtonCol
import os
from pathlib import Path
from datetime import datetime
import app

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
            item = Item('O', entry, file_size_conversion(size), ctime, 'DOWNLOAD', 'DELETE')
            allFiles.append(item)
    return allFiles

def runs(path):

    listOfFile = os.listdir(path)
    allFiles = list()
    for entry in listOfFile:
        fullPath = os.path.join(path, entry)
        if os.path.isdir(fullPath):
            allFiles = allFiles + logs(fullPath)
        else:
            label = 'Run 1'
            ctime = datetime.fromtimestamp(os.path.getctime(fullPath)).strftime('%Y-%m-%d  %H:%M:%S')
            item = ItemRuns(entry, label, ctime, 'OPEN', 'DELETE')
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
    return ItemTable(items)

def create_runs_table():

    items = runs('uploads/html')
    return ItemTableRuns(items)
