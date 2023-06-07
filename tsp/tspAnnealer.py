import dimod
import networkx as nx
from dimod.utilities import qubo_to_ising
from dwave.system import DWaveSampler, \
    EmbeddingComposite
from qiskit_optimization.applications import Tsp
from qiskit_optimization.converters import \
    QuadraticProgramToQubo

# Definición del problema TSP utilizando Qiskit
nodos = [0, 1, 2, 3]
aristas = [(0, 1, 10), (0, 2, 5), (0, 3, 8), (1, 2, 12), (1, 3, 6), (2, 3, 4)]
G = nx.Graph()
G.add_nodes_from(nodos)
G.add_weighted_edges_from(aristas)
tsp = Tsp(G)
qp = tsp.to_quadratic_program()

# Conversión utilizando QuadraticProgramToQubo
converter = QuadraticProgramToQubo()
qp_convertido = converter.convert(qp)

# Obtener la representación QUBO del problema
qubo_dict = qp_convertido.objective.quadratic.to_dict()

### PASAR GRAFO DIRECTAMENTE
## Generar el modelo con el grafo
#bqm = dimod.BinaryQuadraticModel.from_networkx_graph(tsp.graph, vartype=dimod.SPIN, node_attribute_name="nodos", edge_attribute_name="aristas")
##bqm = dimod.BinaryQuadraticModel.from_networkx_graph(G, vartype=dimod.SPIN, node_attribute_name="nodos", edge_attribute_name="aristas")

### PASAR QUBO DIRECTAMENTE
## Generar el modelo con la representación QUBO
bqm = dimod.BinaryQuadraticModel.from_qubo(qubo_dict)

# Resolución del problema utilizando el annealer
sampler = EmbeddingComposite(DWaveSampler())
result_annealer = sampler.sample(bqm, num_reads=10)
print("Solutions obtained using the annealer:")
print(result_annealer)
