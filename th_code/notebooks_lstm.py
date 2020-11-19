import nbformat as nbf
import os
from nbconvert.preprocessors import ExecutePreprocessor
from shutil import copyfile

nb = nbf.v4.new_notebook()

text = """\
# LONG SHORT TERM MEMMORY
"""

code1 = """\
from main import extract, resample, train, gen
"""

code2 = """\
extract()
"""

code3 = """\
resample()
"""

code4 = """\
train()
"""

code5 = """\
gen()
"""

nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(code1),
               nbf.v4.new_code_cell(code2),               
               nbf.v4.new_code_cell(code3),
               nbf.v4.new_code_cell(code4),   
               nbf.v4.new_code_cell(code5),
               ]
               
#nbf.write(nb, '../lstm.ipynb')
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
ep.preprocess(nb, {'metadata': {'path': '../'}})
with open('../lstm.ipynb', 'w', encoding='utf-8') as f:
    nbf.write(nb, f)

os.system('jupyter nbconvert --to html ../lstm.ipynb ../lstm.html')
copyfile('../lstm.html', '../uploads/html/lstm.html')