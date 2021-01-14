import imghdr
import os, json
import glob
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory, Blueprint
from werkzeug.utils import secure_filename
import threading
import th_code.time_series_single_runs as time_series_single_runs
import th_code.time_series_custom_extraction as time_series_custom_extraction
import th_code.time_series_resample as time_series_resample
import th_code.lstm as lstm
import th_code.generate_yaml as gen_yaml
import landing
import notebooks_lstm as nblstm

app = Flask(__name__)

if not os.path.exists("uploads/logs/"):
    os.makedirs("uploads/logs/")
if not os.path.exists("uploads/html/"):
    os.makedirs("uploads/html/")

with open('conf/selection.json', 'w') as file:
    json.dump([], file)


#app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
genlog = Blueprint('genlog', __name__)
app.register_blueprint(genlog, url_prefix='/genlog')
app.config['UPLOAD_EXTENSIONS'] = ['.yaml']
app.config['UPLOADS'] = 'uploads/'
app.config['FILES'] = 'logs/'
app.config['EXTRACTED_METRICS'] = '/single_runs/'
app.config['RESAMPLED_DATA'] = '/resampled/'
app.config['TRAINED_MODELS'] = '/models/lstm/'
app.config['GENERATED_DATA'] = '/generated/'
app.config['GENERATED_LOGS'] = '/generated_logs/'
app.config['HTML'] = 'html/'
app.config['STATE'] = 'start'

selected_files = []

last_num_of_files = [0,0,0,0,0]

def split_list(liste, iscsv=True):
    if iscsv:
        liste = ['_'.join(element.split('_')[1:])[:-4] for element in liste]
    else:
         liste = ['_'.join(element.split('_')[1:]) for element in liste]
    return liste




@app.route('/')
def index():

    return render_template('landing.html')

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(app.config['UPLOADS'] + app.config['FILES'] + filename)


    return render_template('landing.html')


@app.route('/start_run', methods=['POST'])
def start_run():
    for file in selected_files:
        filename = file.split('.')[0]
        x = threading.Thread(target=pipeline, args=[file, filename])
        x.start()
    return redirect(url_for('index'))

    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('landing.html')

def pipeline(file, filename):
        os.makedirs('uploads/' + filename)
        nblstm.create_notebook(file, filename)
        selected_files.remove(file)



def read_metrics():
    path = os.path.dirname(__file__)
    new_path = os.path.relpath('./conf/', path)
    with open(new_path + '/metrics.json') as file:
        metrics = json.load(file)
        return [metric.replace('/', '_') for metric in metrics] 
   
@app.route('/extract', methods=['GET'])   
def extract(file, filename):
    path = app.config['UPLOADS'] + filename + app.config['EXTRACTED_METRICS']
    if not os.path.exists(path):
        os.makedirs(path) 
    time_series_custom_extraction.run(read_metrics(), app.config['UPLOADS'] + app.config['FILES'], path, file)
    return "extraction finished"  

@app.route('/resample', methods=['GET'])   
def resample(file, filename):
    path = app.config['UPLOADS'] +  filename + app.config['EXTRACTED_METRICS']
    path2 = app.config['UPLOADS'] +  filename + app.config['RESAMPLED_DATA']
    if not os.path.exists(path2):
        os.makedirs(path2) 
    time_series_resample.run(path, path2, os.listdir(path))
    return "resampling finished"  

@app.route('/train', methods=['GET'])   
def train(file, filename):
    path = app.config['UPLOADS'] +  filename + app.config['RESAMPLED_DATA']
    path2 = app.config['UPLOADS'] +  filename + app.config['TRAINED_MODELS']
    path3 = app.config['UPLOADS'] +  filename + app.config['GENERATED_DATA']
    
    if not os.path.exists(path2):
        os.makedirs(path2) 
    if not os.path.exists(path3):
        os.makedirs(path3) 

    lstm.run(path, path2, path3, os.listdir(path))
    return "training finished"   

@app.route('/yaml', methods=['GET'])   
def yaml(file, filename):
    path = app.config['UPLOADS'] +  filename + app.config['GENERATED_DATA']
    path2 = app.config['UPLOADS'] + app.config['GENERATED_LOGS']
    path3 = app.config['UPLOADS'] +  filename + app.config['GENERATED_LOGS']
    if not os.path.exists(path):
        os.makedirs(path) 
    if not os.path.exists(path2):
        os.makedirs(path3) 
    if not os.path.exists(path3):
        os.makedirs(path3) 
    
    gen_yaml.get_data(path, path2, path3, read_metrics(), filename)
    return "yaml finished"  

@app.route('/yaml2', methods=['GET'])   
def yaml2():
    path = app.config['UPLOADS'] + 'fc1c330d-18ed-48ed-9671-4ba3005323f6' + app.config['GENERATED_DATA']
    path2 = app.config['UPLOADS'] + app.config['GENERATED_LOGS']
    path3 = app.config['UPLOADS'] +  'fc1c330d-18ed-48ed-9671-4ba3005323f6' + app.config['GENERATED_LOGS']
    if not os.path.exists(path):
        os.makedirs(path) 
    if not os.path.exists(path3):
        os.makedirs(path3) 
    
    gen_yaml.get_data(path, path2, path3, read_metrics(), 'fc1c330d-18ed-48ed-9671-4ba3005323f6')
    return "yaml finished"   

@app.route('/gen', methods=['GET'])   
def gen(file, filename):
    path = app.config['UPLOADS'] +  filename + app.config['TRAINED_MODELS']
    path2 = app.config['UPLOADS'] +  filename + app.config['GENERATED_DATA']
    path3= app.config['UPLOADS'] +  filename + app.config['RESAMPLED_DATA']
    if not os.path.exists(path2):
        os.makedirs(path2) 
    lstm.generate_data(path, path2, path3, os.listdir(path))
    return "generation finished"    
    
@app.route('/state_eval')
def state_eval():

    return {'logs':landing.create_logs_table(), 'runs':landing.create_runs_table()}


@app.route('/delete_log/<name>', methods=['GET', 'POST'])
def delete_log(name):
    if not name.split('.')[0] in ['0b679131-af02-4f1a-bba2-f8d1441b0ca7', '1ab2f9dd-62ff-4433-8d88-605744403ab2', '1c65003f-2c69-449a-9e8b-7dc8ddda07d4']:
        fullPath = os.path.join('uploads', 'logs', name)
        os.remove(fullPath)
    return redirect(url_for('index'))

@app.route('/delete_run/<name>', methods=['GET', 'POST'])
def delete_run(name):
    fullPath = os.path.join('uploads', 'html', name + '.html')
    os.remove(fullPath)
    return redirect(url_for('index'))

@app.route('/uploads/logs/<filename>', methods=['GET', 'POST'])
def download_logs(filename):
    return send_from_directory(app.config['UPLOADS'] + app.config['FILES'], filename)

@app.route('/uploads/runs/<filename>.html', methods=['GET', 'POST'])
def download_runs(filename):
      return send_from_directory(app.config['UPLOADS'] + app.config['HTML'], filename + '.html')

@app.route('/uploads/runs/logs/<filename>.zip', methods=['GET', 'POST'])
def download_runs_logs(filename):
      return send_from_directory(app.config['UPLOADS'] + app.config['GENERATED_LOGS'], filename + '.zip')


@app.route('/use_log/<filename>', methods=['GET', 'POST'])
def use_log(filename):

    if filename in selected_files:
        selected_files.remove(filename)
    else:
        selected_files.append(filename)

    with open('conf/selection.json', 'w') as file:
        json.dump(selected_files, file)

    return redirect(url_for('index'))
    
    
    
if __name__ == "__main__":

    app.run(threaded=False)
    
 

