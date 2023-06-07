import dimod
import networkx as nx
from dimod.utilities import qubo_to_ising
from dwave.system import DWaveSampler, \
    EmbeddingComposite
from qiskit import IBMQ
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.applications import Tsp
from qiskit_optimization.converters import \
    QuadraticProgramToQubo
from qiskit_optimization.runtime import QAOAClient
import sys

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

def formularProblema():

    # Lista de nodos
    nodos = [0, 1, 2, 3] # TODO cambiar a parametro

    # Lista de aristas con pesos, conexiones
    aristas = [(0, 1, 10), (0, 2, 5), (0, 3, 8), (1, 2, 12), (1, 3, 6), (2, 3, 4)] # TODO cambiar a parametro

    # Creación del grafo
    G = nx.Graph()

    # Añadir nodos y conexiones al grafo
    G.add_nodes_from(nodos)

    for (u, v, weight) in aristas:
        G.add_edge(u, v, weight=weight)

    # Crear objeto del problema
    tsp = Tsp(G)

    qp = tsp.to_quadratic_program()
    print(qp.prettyprint())

    return qp

def metodoSimuladorLocal(qp):

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=100)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 10) # TODO cambiar a parametro
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    result = qaoa_optimizer.solve(qp)

    return result

def metodoSimuladorRemoto(qp):
    # Define el quantum_instance utilizando el simulador Qasm
    # Usar IBMQ
    provider = IBMQ.load_account()
    quantum_instance = QuantumInstance(provider.get_backend('ibmq_qasm_simulator'), shots=1024)

    # Definir el optimizador para QAOA
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 1) # TODO cambiar a parametro

    # Define el optimizador para el problema cuántico
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)

    # Resuelve el problema utilizando el algoritmo QAOA
    result = qaoa_optimizer.solve(qp)

    return result


def metodoSimuladorReal(qp):

    # Utilizar ordenador real
    provider = IBMQ.load_account()
    qaoa_client = QAOAClient(provider=provider , backend=provider.get_backend("ibm_lagos"), reps=1) # TODO cambiar a parametro

    qaoa = MinimumEigenOptimizer(qaoa_client)

    # Resuelve el problema utilizando el algoritmo QAOA
    result = qaoa.solve(qp)

    return result

def metodoAnnealer(qp): # TODO tengo que asegurarme que está bien primero

    # Conversión utilizando QuadraticProgramToQubo
    converter = QuadraticProgramToQubo()
    qp_convertido = converter.convert(qp)

    # Obtener la representación QUBO del problema
    qubo_dict = qp_convertido.objective.quadratic.to_dict()

    # Convertir el QUBO a una representación Ising
    h, J, offset = qubo_to_ising(qubo_dict)

    # Generar el modelo con los parámetros anteriores
    bqm = dimod.BinaryQuadraticModel.from_ising(h, J, offset)

    # Resolución del problema utilizando el annealer
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(bqm, num_reads=10)

    return result

## ME QUEDE AQUI, hasta que no sepa que annealer y los otros son equivalentes igual mejor esperar

qp = formularProblema()

# switch con el parametro del metodo, en base a eso ejecuto el metodo que corresponda
# pasandole como parametro qp y guardando el resultado
result = None

if metodo == "simuladorLocal":
    result = metodoSimuladorLocal(qp)
elif metodo == "simuladorRemoto":
    result = metodoSimuladorRemoto(qp)
elif metodo == "simuladorReal":
    result = metodoSimuladorReal(qp)
elif metodo == "annealer":
    result = metodoAnnealer(qp)



print(result)