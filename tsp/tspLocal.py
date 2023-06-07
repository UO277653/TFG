##
#
# TSP ejecutar en simulador local
#
# Con 10 repeticiones suele hacer success con 4 nodos
##


import networkx as nx
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
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

num_qubits = 4**2 # Parámetro n
adj_matrix = nx.to_numpy_array(tsp.graph)
colors = ["r" for node in tsp.graph.nodes]
pos = nx.spring_layout(tsp.graph)
qp = tsp.to_quadratic_program()
print(qp.prettyprint())

#
# RESOLUCIÓN DEL PROBLEMA
#
quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=100)
qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 10) # PARAMETRO repeticiones
qaoa_optimizer = MinimumEigenOptimizer(qaoa)
result = qaoa_optimizer.solve(qp)
print(result)

