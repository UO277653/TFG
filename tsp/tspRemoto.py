##
#
# TSP ejecutar en simulador remoto
#
##

import networkx as nx
from qiskit import IBMQ
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.applications import Tsp

#
# DEFINICIÓN DEL PROBLEMA
#

# Lista de nodos
nodos = [0, 1, 2, 3]

# Lista de aristas con pesos, conexiones
aristas = [(0, 1, 10), (0, 2, 5), (0, 3, 8), (1, 2, 12), (1, 3, 6), (2, 3, 4)]

# Creación del grafo
G = nx.Graph()

# Añadir nodos y conexiones al grafo
G.add_nodes_from(nodos)

for (u, v, weight) in aristas:
    G.add_edge(u, v, weight=weight)

# Crear objeto del problema
tsp = Tsp(G)

num_qubits = 4**2 ## Parámetro n
adj_matrix = nx.to_numpy_array(tsp.graph)
colors = ["r" for node in tsp.graph.nodes]
pos = nx.spring_layout(tsp.graph)
qp = tsp.to_quadratic_program()

#
# RESOLUCIÓN DEL PROBLEMA
#

# Define el quantum_instance utilizando el simulador Qasm
# Usar IBMQ
provider = IBMQ.load_account()
quantum_instance = QuantumInstance(provider.get_backend('ibmq_qasm_simulator'), shots=1024)

# Definir el optimizador para QAOA
qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 1) # PARAMETRO repeticiones

# Define el optimizador para el problema cuántico
qaoa_optimizer = MinimumEigenOptimizer(qaoa)

# Resuelve el problema utilizando el algoritmo QAOA
result = qaoa_optimizer.solve(qp)

# Imprime la solución
print(result)

