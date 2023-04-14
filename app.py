from flask import Flask, render_template, request
import subprocess


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute', methods=['POST'])
def execute_script():
    # Aquí colocas el código que quieres ejecutar al hacer clic en el botón
    # por ejemplo:
    output = subprocess.check_output(['python', 'maxcut.py'])
    return output

if __name__ == '__main__':
    app.run()