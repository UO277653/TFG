##
#
# Max-Cut ejecutar en simulador
#
##

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.applications import \
    Maxcut
import sys

from qiskit import IBMQ

# Guardar parámetros
numeroNodos = sys.argv[1]
conexiones = sys.argv[2]
repeticiones = int(sys.argv[3])
elist = [tuple(map(int, elemento.split(','))) for elemento in conexiones.split(';')]

# Función opcional para representar el grafo
def draw_graph(G, colors, pos):
    default_axes = plt.axes(frameon=True)
    nx.draw_networkx(G, node_color=colors, node_size=600, alpha=0.8, ax=default_axes, pos=pos)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)


## DEFINICIÓN DEL PROBLEMA

# Número de nodos
n = int(numeroNodos)

# Creación del objeto NetworkX graph, que se usa después en la clase Maxcut
G = nx.Graph()

# Añadir los nodos del grafo
G.add_nodes_from(np.arange(0, n, 1))

# Añadir las conexiones del grafo
G.add_weighted_edges_from(elist)
colors = ["r" for node in G.nodes()]
pos = nx.spring_layout(G)

# Representar el problema de manera gráfica
draw_graph(G, colors, pos)

# Crear la matriz de pesos
w = np.zeros([n, n])
for i in range(n):
    for j in range(n):
        temp = G.get_edge_data(i, j, default=0)
        if temp != 0:
            w[i, j] = temp["weight"]

# Crear el objeto Maxcut
max_cut = Maxcut(w)
qp = max_cut.to_quadratic_program()

# Define el quantum_instance utilizando el simulador Qasm
# Usar IBMQ
provider = IBMQ.load_account()
quantum_instance = QuantumInstance(provider.get_backend('ibmq_qasm_simulator'), shots=1024)

# Definir el optimizador para QAOA
qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 1)

# Define el optimizador para el problema cuántico
qaoa_optimizer = MinimumEigenOptimizer(qaoa)

# Resuelve el problema utilizando el algoritmo QAOA
result = qaoa_optimizer.solve(qp)

# Imprime la solución
print(result)