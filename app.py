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

@app.route('/executeTSP', methods=['POST'])
def execute_TSP():
    datos = request.get_json()
    output = subprocess.check_output(['python', './tsp/tsp.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones'), datos.get('metodo')])
    return output

@app.route('/executeMaxCutLocal', methods=['POST'])
def execute_MaxCutLocal():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutLocal.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutRemoto', methods=['POST'])
def execute_MaxCutRemoto():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutRemoto.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutReal', methods=['POST'])
def execute_MaxCutReal():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutReal.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutAnnealer', methods=['POST'])
def execute_MaxCutAnnealer():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutAnnealer.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutAnnealerSimulatedAnnealingSolver', methods=['POST'])
def execute_MaxCutAnnealerSimulatedAnnealingSolver():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutAnnealerSimulatedAnnealingSampler.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMacCutAnnealerTabuSolver', methods=['POST'])
def execute_MaxCutAnnealerTabuSolver():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutAnnealerTabuSolver.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutSteepestDescentSolver', methods=['POST'])
def execute_MaxCutAnnealerSteepestDescentSolver():
    datos = request.get_json()
    output = subprocess.check_output(['python', './maxcut/maxCutSteepestDescentSolver.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

if __name__ == '__main__':
    # pdb.set_trace() # Para debug, checkpoint()
    # app.debug = True # Para debug
    app.run()