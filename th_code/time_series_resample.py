import numpy as np
import pandas as pd
from datetime import datetime
import glob
import os
import matplotlib.pyplot as plt


def resample(path, path2, files):

        dfs = []
        
        for file in files:
            df = pd.read_csv(path + file)
            df = df.drop_duplicates(subset=['timestamp'])
            df.index = df.timestamp
            df = df.drop('timestamp', axis=1)
            df.index = pd.to_datetime(df.index)
            df = df.resample('100L').pad()
            df = df.dropna()
            df = df.reset_index()
            df = df.drop('timestamp', axis=1)
            dfs.append(df)
            write_csv(df, path2, file)
        """
        sizes = [df.shape[0] for df in dfs]
        if len(sizes) > 3:
            median = np.median(sizes)
            dfs_cleaned = []
            for df in dfs:
                if df.shape[0] >= median*0.8 and df.shape[0] <= median*1.2:
                    dfs_cleaned.append(df)
            
            sizes = [df.shape[0] for df in dfs_cleaned]
            num_of_bins = 3
            
            quantiles = pd.qcut(sizes, num_of_bins, duplicates='drop').categories
            if len(quantiles) == num_of_bins:
                bin = [ [] for i in range(num_of_bins) ]

                for df in dfs_cleaned:
                    for j in range(num_of_bins):
                        if df.shape[0] >= quantiles[j].left and df.shape[0] < quantiles[j].right:
                            bin[j].append(df)
 

                for j in range(num_of_bins):
                    if len(bin[j]) > 0:
                        min_length = np.min([df.shape[0] for df in bin[j]])
                        bin_shaped = []
                        for df in bin[j]:
                            df = df[0:min_length]
                            bin_shaped.append(df)
                        write_csv(bin_shaped,j,file)
                        """


def write_csv(df, path2, file):
    print("write resampled " + file)
    df.to_csv(path2 + file, header=False)
 

def run(path, path2, files):   
    print("resample start")                        
    resample(path, path2, files)
    print("resample end")  
    print("--------------------------------")