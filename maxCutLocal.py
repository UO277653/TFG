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


# Función opcional para representar el grafo (para la aplicación puede ser útil)
def draw_graph(G, colors, pos):
    default_axes = plt.axes(frameon=True)
    nx.draw_networkx(G, node_color=colors, node_size=600, alpha=0.8, ax=default_axes, pos=pos)
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)


## DEFINICIÓN DEL PROBLEMA

# Número de nodos
n = 4

# Creación del objeto NetworkX graph, que se usa después en la clase Maxcut
G = nx.Graph()

# Añadir los nodos del grafo
G.add_nodes_from(np.arange(0, n, 1))

# Añadir las conexiones del grafo
elist = [(0, 1, 1.0), (0, 2, 1.0), (0, 3, 1.0), (1, 2, 1.0), (2, 3, 1.0)]
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

# Crear el objeto Maxcut y
max_cut = Maxcut(w)
qp = max_cut.to_quadratic_program()

# Define el quantum_instance utilizando el simulador Aer
quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=1024)

# Definir el optimizador para QAOA
qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 1)

# Define el optimizador para el problema cuántico
qaoa_optimizer = MinimumEigenOptimizer(qaoa)

# Resuelve el problema utilizando el algoritmo QAOA
result = qaoa_optimizer.solve(qp)

# Imprime la solución
print(result)