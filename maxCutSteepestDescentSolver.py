##
#
# Max-Cut ejecutar con steepest descent
#
##

import dimod
import greedy

## DEFINICIÓN DEL PROBLEMA
J = {(0,1):1, (0,2):1, (1,2):1, (0,3):1, (2,3):1} # Conexiones
h = {}

problem = dimod.BinaryQuadraticModel(h, J, 0.0, dimod.SPIN)
print("The problem we are going to solve is:")
print(problem)

solver = greedy.SteepestDescentSolver()
solution = solver.sample(problem , num_reads = 10)
print(solution.aggregate())