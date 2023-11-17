import sys

import random
import dimod
import greedy
import neal
import tabu
from docplex.mp.model import Model
from dwave.system import DWaveSampler
from dwave.system import EmbeddingComposite
from qiskit import IBMQ
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.converters import \
    QuadraticProgramToQubo
from qiskit_optimization.runtime import QAOAClient
from qiskit_optimization.translators import \
    from_docplex_mp

from util import *

#
# DEFINICIÓN DEL PROBLEMA
#

numeroNodos = int(sys.argv[1])
conexiones = sys.argv[2]
repeticiones = int(sys.argv[3])
metodo = sys.argv[4]

conexionesArray = []

if conexiones != "":
    # Dividir la cadena en partes separadas por ";"
    partesConexion = conexiones.split(";")

    # Crear una lista de tuplas a partir de las partes separadas
    conexionesArray = [tuple(map(int, parte.split(","))) for parte in partesConexion]

def formularProblemaDocplex(numeroNodos, conexionesArray, repeticiones):

    ##
    ## DATOS DEL PROBLEMA
    ##
    num_vertices = numeroNodos
    edges = [(x, y) for x, y, _ in conexionesArray]

    # Crear el modelo
    mdl = Model(name='MaxCut')

    # Variables de decisión
    z = mdl.integer_var_list(num_vertices, lb=-1, ub=1, name='z')

    # Función objetivo
    objective = mdl.sum(z[j] * z[k] for j, k in edges)

    mdl.minimize(objective)

    # Resolver el modelo
    solution = mdl.solve()

    return mdl

def formularProblemaQiskit(mdl):

    # Conversión a Qiskit a partir del docplex
    qp = from_docplex_mp(mdl)

    return qp

def formularProblemaDwave(qp):

    conv = QuadraticProgramToQubo()

    # Pasar QuadraticProgram a QUBO
    problemConverted = conv.convert(qp)

    # Pasar QUBO a bqm
    bqm_binary = dimod.as_bqm(problemConverted.objective.linear.to_array(), problemConverted.objective.quadratic.to_array(), dimod.BINARY)

    return bqm_binary


def metodoSimuladorLocal(qp):

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=100)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = repeticiones)
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    result = qaoa_optimizer.solve(qp)

    return result

def metodoSimuladorRemoto(qp):

    # Usar IBMQ para obtener acceso al simulador remoto
    provider = IBMQ.load_account()
    quantum_instance = QuantumInstance(provider.get_backend('ibmq_qasm_simulator'), shots=1024)

    # Definir el optimizador para QAOA
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = repeticiones)

    # Define el optimizador para el problema cuántico
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)

    # Resuelve el problema utilizando el algoritmo QAOA
    result = qaoa_optimizer.solve(qp)

    return result

def metodoSimuladorReal(qp):

    # Utilizar ordenador real
    provider = IBMQ.load_account()
    qaoa_client = QAOAClient(provider=provider , backend=provider.get_backend("ibm_lagos"), reps=repeticiones)

    qaoa = MinimumEigenOptimizer(qaoa_client)

    # Resuelve el problema utilizando el algoritmo QAOA
    result = qaoa.solve(qp)

    return result

def metodoAnnealer(bqm_binary):

    # Resolver el modelo dimod
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(bqm_binary, num_reads=100)

    return result

def metodoSimulatedAnnealingSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = neal.SimulatedAnnealingSampler()
    result = solver.sample(bqm_binary, num_reads=200)

    return result

def metodoTabuSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = tabu.TabuSampler()
    result = solver.sample(bqm_binary , num_reads = 10)

    return result

def metodoSteepestDescentSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = greedy.SteepestDescentSolver()
    result = solver.sample(bqm_binary , num_reads = 10)

    return result

# Generar los modelos
mdl = formularProblemaDocplex(numeroNodos, conexionesArray, repeticiones)
qp = formularProblemaQiskit(mdl)
bqm = formularProblemaDwave(qp)

result = None

# Resolver el problema utilizando el método seleccionado
if metodo == "simuladorLocal":
    result = metodoSimuladorLocal(qp)
    print(printQiskit(result))

elif metodo == "simuladorRemoto":
    result = metodoSimuladorRemoto(qp)
    print(printQiskit(result))

elif metodo == "simuladorReal":
    result = metodoSimuladorReal(qp)
    print(printQiskit(result))

elif metodo == "annealer":
    result = metodoAnnealer(bqm)
    print(printResultDWave(result))

elif metodo == "annealerSimulatedAnnealingSolver":
    result = metodoSimulatedAnnealingSolver(bqm)
    print(printResultDWave(result))

elif metodo == "annealerTabuSolver":
    result = metodoTabuSolver(bqm)
    print(printResultDWave(result))

elif metodo == "annealerSteepestDescentSolver":
    result = metodoSteepestDescentSolver(bqm)
    print(printResultDWave(result))
