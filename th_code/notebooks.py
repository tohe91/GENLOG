import nbformat as nbf

nb = nbf.v4.new_notebook()

text = """\
# Time-series Generative Adversarial Network (TimeGAN)
"""

code1 = """\
import warnings
warnings.filterwarnings('ignore')
"""

code2 = """\
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
from pathlib import Path
from tqdm import tqdm
import os

from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import GRU, Dense, RNN, GRUCell, Input
from tensorflow.keras.losses import BinaryCrossentropy, MeanSquaredError
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.utils import plot_model

import matplotlib.pyplot as plt
import seaborn as sns
"""

code3 = """\
gpu_devices = tf.config.experimental.list_physical_devices('GPU')
if gpu_devices:
    print('Using GPU')
    tf.config.experimental.set_memory_growth(gpu_devices[0], True)
else:
    print('Using CPU')
    """
    
code4 = """\
sns.set_style('white')
"""

text2 = """\
# Prepare Data
"""

code5 = """\
seq_len = 24
n_seq = 1
batch_size = 128

def select_data():
    df = pd.read_csv('../data/run.csv', header=None)
    df = df.drop([0], axis=1)
    return df
select_data()

"""

text3 = """\
# Plot Series
"""

code6 = """\
df = select_data()
df.plot()
"""

text4 = """\
# Normalize Data
"""

code7 = """\
scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(df).astype(np.float32)
"""

text5 = """\
# Create rolling window sequences
"""

code8 = """\
data = []
for i in range(len(df) - seq_len):
    data.append(scaled_data[i:i + seq_len])

n_windows = len(data)
"""

code = """\

"""

code = """\

"""

code = """\

"""

nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(code1),
               nbf.v4.new_code_cell(code2),               
               nbf.v4.new_code_cell(code3),
               nbf.v4.new_code_cell(code4),   
               nbf.v4.new_markdown_cell(text2),  
               nbf.v4.new_code_cell(code5),
               nbf.v4.new_markdown_cell(text3),
               nbf.v4.new_code_cell(code6), 
               nbf.v4.new_markdown_cell(text4),
               nbf.v4.new_code_cell(code7),  
               nbf.v4.new_markdown_cell(text5),
               nbf.v4.new_code_cell(code8),                
               ]
               
nbf.write(nb, '../notebooks/test.ipynb')