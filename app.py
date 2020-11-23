import imghdr
import os, json
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename
import threading
import th_code.time_series_single_runs as time_series_single_runs
import th_code.time_series_custom_extraction as time_series_custom_extraction
import th_code.time_series_resample as time_series_resample
import th_code.lstm as lstm
import landing

app = Flask(__name__)

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
if not os.path.exists("uploads/html"):
    os.makedirs("uploads/html")

#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.xes', '.yaml']
app.config['UPLOADS'] = 'uploads/'
app.config['FILES'] = 'uploads/logs/'
app.config['EXTRACTED_METRICS'] = 'uploads/single_runs/'
app.config['RESAMPLED_DATA'] = 'uploads/resampled/'
app.config['TRAINED_MODELS'] = 'uploads/models/lstm/'
app.config['GENERATED_DATA'] = 'uploads/generated/'
app.config['HTML'] = 'uploads/html/'
app.config['STATE'] = 'start'

last_num_of_files = [0,0,0,0,0]

def split_list(liste, iscsv=True):
    if iscsv:
        liste = ['_'.join(element.split('_')[1:])[:-4] for element in liste]
    else:
         liste = ['_'.join(element.split('_')[1:]) for element in liste]
    return liste


@app.route('/')
def index():


    files = os.listdir(app.config['FILES'])
    extracted_metrics = split_list(os.listdir(app.config['EXTRACTED_METRICS']))
    resampled_data = split_list(os.listdir(app.config['RESAMPLED_DATA']))
    trained_models = split_list(os.listdir(app.config['TRAINED_MODELS']), False)
    generated_data = split_list(os.listdir(app.config['GENERATED_DATA']))
    
    return render_template('landing.html', files=files, extracted_files=extracted_metrics, resampled_data=resampled_data, trained_models=trained_models, generated_data=generated_data)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['FILES'], filename))
    x = threading.Thread(target=pipeline)
    x.start()

    return redirect(url_for('index'))


@app.route('/start_run', methods=['POST'])
def start_run():
    print('start run')
    return redirect(url_for('index'))

@app.route('/state')
def state():
    changed = [0,0,0,0,0]
    if last_num_of_files[1] != len(os.listdir(app.config['EXTRACTED_METRICS'])):
        last_num_of_files[1] = len(os.listdir(app.config['EXTRACTED_METRICS']))
        changed[1] = 1
    if last_num_of_files[2] != len(os.listdir(app.config['RESAMPLED_DATA'])):
        last_num_of_files[2] = len(os.listdir(app.config['RESAMPLED_DATA']))
        changed[2] = 1
    if last_num_of_files[3] != len(os.listdir(app.config['TRAINED_MODELS'])):
        last_num_of_files[3] = len(os.listdir(app.config['TRAINED_MODELS']))
        changed[3] = 1
    if last_num_of_files[4] != len(os.listdir(app.config['GENERATED_DATA'])):
        last_num_of_files[4] = len(os.listdir(app.config['GENERATED_DATA']))
        changed[4] = 1

    return {'state': app.config['STATE'], 'changed':changed}

@app.route('/column1')
def column1():
    return render_template('column1.html', files=os.listdir(app.config['FILES']), state= app.config['STATE'])

@app.route('/column2')
def column2():
    items = [{'href':app.config['EXTRACTED_METRICS']+file, 'name':name} for(file, name) in zip(os.listdir(app.config['EXTRACTED_METRICS']), split_list(os.listdir(app.config['EXTRACTED_METRICS'])))]
    return render_template('column1.html', items=items, state=app.config['STATE'])


@app.route('/column3')
def column3():
    items = [{'href':app.config['RESAMPLED_DATA']+file, 'name':name} for(file, name) in zip(os.listdir(app.config['RESAMPLED_DATA']), split_list(os.listdir(app.config['RESAMPLED_DATA'])))]
    return render_template('column1.html', items=items, state= app.config['STATE'])


@app.route('/column4')
def column4():
    items = [{'href':app.config['TRAINED_MODELS']+file, 'name':name} for(file, name) in zip(os.listdir(app.config['TRAINED_MODELS']), split_list(os.listdir(app.config['TRAINED_MODELS']),iscsv=False))]
    return render_template('column1.html', items=items, state= app.config['STATE'])


@app.route('/column5')
def column5():
    items = [{'href':app.config['GENERATED_DATA']+file, 'name':name} for(file, name) in zip(os.listdir(app.config['GENERATED_DATA']), split_list(os.listdir(app.config['GENERATED_DATA'])))]
    return render_template('column1.html', items=items, state= app.config['STATE'])

    
def pipeline():
    app.config['STATE'] = 'extract'
    print(extract())
    app.config['STATE'] = 'resample'
    print(resample())
    app.config['STATE'] = 'train'
    print(train())
    app.config['STATE'] = 'gen'
    print(gen())
    app.config['STATE'] = 'end'

@app.route('/uploads/single_runs/<filename>')
def upload1(filename):
    return send_from_directory(app.config['EXTRACTED_METRICS'], filename)
@app.route('/uploads/resampled/<filename>')
def upload2(filename):
    return send_from_directory(app.config['RESAMPLED_DATA'], filename)
@app.route('/uploads/models/lstm/<filename>')
def upload3(filename):
    return send_from_directory(app.config['TRAINED_MODELS'], filename)
@app.route('/uploads/generated/<filename>')
def upload4(filename):
    return send_from_directory(app.config['GENERATED_DATA'], filename)

    
    
def read_metrics():
    path = os.path.dirname(__file__)
    new_path = os.path.relpath('./conf/', path)
    with open(new_path + '/metrics.json') as file:
        metrics = json.load(file)
        return [metric.replace('/', '_') for metric in metrics] 
   
@app.route('/extract', methods=['GET'])   
def extract():
    time_series_custom_extraction.run(read_metrics())
    return "extraction finished"  

@app.route('/resample', methods=['GET'])   
def resample():
    time_series_resample.run(app.config['EXTRACTED_METRICS'], os.listdir(app.config['EXTRACTED_METRICS']))
    return "resampling finished"  

@app.route('/train', methods=['GET'])   
def train():
    lstm.run(app.config['RESAMPLED_DATA'], os.listdir(app.config['RESAMPLED_DATA']))
    return "training finished"   

@app.route('/gen', methods=['GET'])   
def gen():
    lstm.generate_data(app.config['TRAINED_MODELS'],  os.listdir(app.config['TRAINED_MODELS']))
    return "generation finished"    
    
@app.route('/state_eval')
def state_eval():
    
    return {'logs':landing.create_logs_table(), 'runs':landing.create_runs_table()}


@app.route('/delete_log/<name>', methods=['GET', 'POST'])
def delete_log(name):
    fullPath = os.path.join('uploads', 'logs', name)
    os.remove(fullPath)
    return redirect(url_for('index'))

@app.route('/delete_run/<name>', methods=['GET', 'POST'])
def delete_run(name):
    fullPath = os.path.join('uploads', 'html', name)
    os.remove(fullPath)
    return redirect(url_for('index'))

@app.route('/uploads/logs/<filename>', methods=['GET', 'POST'])
def download_logs(filename):
    return send_from_directory(app.config['FILES'], filename)

@app.route('/uploads/runs/<filename>', methods=['GET', 'POST'])
def download_runs(filename):
      return send_from_directory(app.config['HTML'], filename)


@app.route('/use_log/<filename>', methods=['GET', 'POST'])
def use_log(filename):
    fullPath = os.path.join('uploads', 'logs', filename)
    print(fullPath)
    return redirect(url_for('index'))
    
    
    
if __name__ == "__main__":

    app.run(threaded=False)
    
 

