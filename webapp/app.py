import subprocess

from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/maxcut')
def pagMaxCut():
    return render_template('maxcut.html')

@app.route('/tsp')
def pagTSP():
    return render_template('tsp.html')

@app.route('/knapsack')
def pagKnapsack():
    return render_template('knapsack.html')

@app.route('/graphColor')
def pagGraphColor():
    return render_template('graphColor.html')

@app.route('/executeTSP', methods=['POST'])
def execute_TSP():
    datos = request.get_json()
    output = subprocess.check_output(['python', './python/tsp.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones'), datos.get('metodo')])
    return output

@app.route('/executeKnapsack', methods=['POST'])
def execute_Knapsack():
    datos = request.get_json()
    output = subprocess.check_output(['python', './python/knapsack.py', datos.get('pesoMaximo'), datos.get('arrayValores'), datos.get('arrayPesos'), datos.get('metodo'), datos.get('repeticiones')])
    return output

@app.route('/executeGraphColor', methods=['POST'])
def execute_GraphColor():
    datos = request.get_json()
    output = subprocess.check_output(['python', './python/graphColor.py', datos.get('numeroNodos'), datos.get('numeroColores'), datos.get('numeroRep'), datos.get('conexiones'), datos.get('metodo')])
    return output

@app.route('/executeMaxCut', methods=['POST'])
def execute_MaxCut():
    datos = request.get_json()
    output = subprocess.check_output(['python', './python/maxCut.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones'), datos.get('metodo')])
    return output

@app.route('/configQiskit', methods=['POST'])
def configQiskit():

    datos = request.get_json()
    subprocess.run(['python', './python/configQiskit.py', datos.get('token')])

    return render_template('index.html')

@app.route('/configDWave', methods=['POST'])
def configDWave():

    datos = request.get_json()
    subprocess.run(['python', './python/configDWave.py', datos.get('token')])

    return render_template('index.html')

@app.route('/sesionQiskit')
def sesionQiskit():

    output = subprocess.check_output(['python', './python/consultarSesionQiskit.py'])
    return output

@app.route('/sesionDWave')
def sesionDWave():

    output = subprocess.check_output(['python', './python/consultarSesionDWave.py'])
    return output

if __name__ == '__main__':
    app.run()