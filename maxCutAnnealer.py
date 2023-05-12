##
#
# Max-Cut ejecutar en annealer
#
##

import dimod
from dwave.system import DWaveSampler, \
    EmbeddingComposite

## DEFINICIÓN DEL PROBLEMA
J = {(0,1):1, (0,2):1, (1,2):1, (0,3):1, (2,3):1} # Conexiones
h = {}

problem = dimod.BinaryQuadraticModel(h, J, 0.0, dimod.SPIN)
print("The problem we are going to solve is:")
print(problem)

sampler = EmbeddingComposite(DWaveSampler())
result = sampler.sample(problem , num_reads=10)
print("The solutions that we have obtained are")
print(result)