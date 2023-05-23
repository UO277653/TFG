from flask import Flask, render_template, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/executeMaxCutLocal', methods=['POST'])
def execute_MaxCutLocal():
    datos = request.get_json()
    print(datos)
    #print(request)

    output = subprocess.check_output(['python', 'maxCutLocal.py', datos.get('nodos'), datos.get('conexiones'), datos.get('repeticiones')])
    return output

@app.route('/executeMaxCutRemoto', methods=['POST'])
def execute_MaxCutRemoto():
    output = subprocess.check_output(['python', 'maxCutRemoto.py'])
    return output

@app.route('/executeMaxCutReal', methods=['POST'])
def execute_MaxCutReal():
    output = subprocess.check_output(['python', 'maxCutReal.py'])
    return output

@app.route('/executeMaxCutAnnealer', methods=['POST'])
def execute_MaxCutAnnealer():
    output = subprocess.check_output(['python', 'maxCutAnnealer.py'])
    return output

@app.route('/executeMaxCutAnnealerSimulatedAnnealingSolver', methods=['POST'])
def execute_MaxCutAnnealerSimulatedAnnealingSolver():
    output = subprocess.check_output(['python', 'maxCutAnnealerSimulatedAnnealingSampler.py'])
    return output

@app.route('/executeMacCutAnnealerTabuSolver', methods=['POST'])
def execute_MaxCutAnnealerTabuSolver():
    output = subprocess.check_output(['python', 'maxCutAnnealerTabuSolver.py'])
    return output

@app.route('/executeMaxCutSteepestDescentSolver', methods=['POST'])
def execute_MaxCutAnnealerSteepestDescentSolver():
    output = subprocess.check_output(['python', 'maxCutSteepestDescentSolver.py'])
    return output

if __name__ == '__main__':
    # pdb.set_trace() # Para debug, checkpoint()
    # app.debug = True # Para debug
    app.run()