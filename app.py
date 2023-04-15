from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_script():
    output = subprocess.check_output(['python', 'maxcut.py'])
    return jsonify({'output': output.decode('utf-8')})

if __name__ == '__main__':
    app.run()