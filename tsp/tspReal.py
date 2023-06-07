##
#
# TSP ejecutar en ordenador cuántico real
#
##


import matplotlib.pyplot as plt
import networkx as nx
from qiskit_optimization.applications import Tsp
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.algorithms.minimum_eigensolvers import NumPyMinimumEigensolver
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization.runtime import QAOAClient
from qiskit import IBMQ

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

# Utilizar ordenador real
provider = IBMQ.load_account()
qaoa_client = QAOAClient(provider=provider , backend=provider.get_backend("ibm_lagos"), reps=1) # PARAMETRO repeticiones

qaoa = MinimumEigenOptimizer(qaoa_client)

# Resuelve el problema utilizando el algoritmo QAOA
result = qaoa.solve(qp)

# Imprime la solución
print(result)