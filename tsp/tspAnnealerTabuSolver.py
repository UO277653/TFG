##
#
# TSP ejecutar con tabu solver
#
##

import dimod
import tabu
import sys

conexiones = sys.argv[2]
coleccion = {}

# Dividir la cadena por el punto y coma (;) para obtener cada elemento separado
elementos = conexiones.split(";")

# Recorrer cada elemento y crear una tupla para cada uno
for elemento in elementos:
    valores = elemento.split(",")
    tupla = (int(valores[0]), int(valores[1]))
    valor = int(valores[2])
    coleccion[tupla] = valor

## DEFINICIÓN DEL PROBLEMA
J = coleccion  # Conexiones
h = {}

problem = dimod.BinaryQuadraticModel(h, J, 0.0, dimod.SPIN)
print("The problem we are going to solve is:")
print(problem)

solver = tabu.TabuSampler()
solution = solver.sample(problem , num_reads = 10)
print(solution.aggregate())