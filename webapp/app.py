from flask import Flask, render_template, request, jsonify
import subprocess

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
    output = subprocess.check_output(['python', './tsp/tsp.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones'), datos.get('metodo')])
    return output

@app.route('/executeKnapsack', methods=['POST'])
def execute_Knapsack():
    datos = request.get_json()
    output = subprocess.check_output(['python', './knapsack/knapsack.py', datos.get('pesoMaximo'), datos.get('arrayValores'), datos.get('arrayPesos'), datos.get('metodo')])
    return output

@app.route('/executeGraphColor', methods=['POST'])
def execute_GraphColor():
    datos = request.get_json()
    output = subprocess.check_output(['python', './graphColor/graphColor.py', datos.get('numeroNodos'), datos.get('numeroColores'), datos.get('numeroRep'), datos.get('conexiones'), datos.get('metodo')])
    return output

@app.route('/executeMaxCut', methods=['POST'])
def execute_MaxCut():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCut.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones'), datos.get('metodo')])
    return output

if __name__ == '__main__':
    # pdb.set_trace() # Para debug, checkpoint()
    # app.debug = True # Para debug
    app.run()