import sys

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

#
# PARÁMETROS
#
numeroNodos = sys.argv[1]
conexiones = sys.argv[2]
repeticiones = int(sys.argv[3])
metodo = sys.argv[4]

elist = [tuple(map(int, elemento.split(','))) for elemento in conexiones.split(';')]

#
# DEFINICIÓN DEL PROBLEMA
#

def formularProblemaDocplex():

    ##
    ## DATOS DEL PROBLEMA
    ##
    cities = list(range(int(numeroNodos)))
    connections = elist

    # Pesos
    w = {(j, k): cost for j, k, cost in connections}
    # Número de nodos
    m = len(cities)

    ####################
    ## MODELO docplex ##
    ####################
    mdl = Model(name="TSP")

    # Variables binarias
    x = {(j, l): mdl.binary_var(name=f"x{j}{l}") for j in cities for l in cities}

    # Restricción 1
    for j in cities:
        mdl.add_constraint(mdl.sum(x[(j, l)] for l in cities) == 1)

    # Restricción 2
    for l in cities:
        mdl.add_constraint(mdl.sum(x[(j, l)] for j in cities) == 1)

    # Expresión del costo
    total_cost = mdl.sum(w[(j, k)] * x[(j, l)] * x[(k, (l + 1))] for l in range(len(cities)) for j in cities for k in cities if j != k if(j,k) in w if (j,l) in x and(k, l+1) in x)
    mdl.minimize(total_cost)

    # Resolver el modelo docplex
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
    # Define el quantum_instance utilizando el simulador Qasm
    # Usar IBMQ
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
    result = sampler.sample(bqm_binary, num_reads=200)

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
mdl = formularProblemaDocplex()
qp = formularProblemaQiskit(mdl)
bqm = formularProblemaDwave(qp)

result = None

# Resolver el problema utilizando el método seleccionado
if metodo == "simuladorLocal":
    result = metodoSimuladorLocal(qp)
elif metodo == "simuladorRemoto":
    result = metodoSimuladorRemoto(qp)
elif metodo == "simuladorReal":
    result = metodoSimuladorReal(qp)
elif metodo == "annealer":
    result = metodoAnnealer(bqm)
elif metodo == "annealerSimulatedAnnealingSolver":
    result = metodoSimulatedAnnealingSolver(bqm)
elif metodo == "annealerTabuSolver":
    result = metodoTabuSolver(bqm)
elif metodo == "annealerSteepestDescentSolver":
    result = metodoSteepestDescentSolver(bqm)

print(result)



