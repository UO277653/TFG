from flask import Flask, render_template, request, jsonify
import subprocess
import pdb;

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_script():
    output = subprocess.check_output(['python', 'maxcut.py'])
    # pdb.set_trace() # Para debug
    return output

if __name__ == '__main__':
    # pdb.set_trace() # Para debug, checkpoint()
    # app.debug = True # Para debug
    app.run()