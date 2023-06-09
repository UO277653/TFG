import sys

import random
import dimod
import greedy
import neal
import tabu
from docplex.mp.model import Model
from dwave.system import DWaveSampler
from dwave.system import EmbeddingComposite
from qiskit import IBMQ
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.converters import \
    QuadraticProgramToQubo
from qiskit_optimization.runtime import QAOAClient
from qiskit_optimization.translators import \
    from_docplex_mp

#
# PARÁMETROS
#

#
# DEFINICIÓN DEL PROBLEMA
#

numeroNodos = int(sys.argv[1])
conexiones = sys.argv[2]
repeticiones = int(sys.argv[3])
metodo = sys.argv[4]

conexionesArray = []

if conexiones != "":
    # Dividir la cadena en partes separadas por ";"
    partesConexion = conexiones.split(";")

    # Crear una lista de tuplas a partir de las partes separadas
    conexionesArray = [tuple(map(int, parte.split(","))) for parte in partesConexion]

def formularProblemaDocplex(numeroNodos, conexionesArray, repeticiones):

    ##
    ## DATOS DEL PROBLEMA
    ##
    num_vertices = numeroNodos
    edges = [(x, y) for x, y in conexionesArray] # edges = [(x, y) for x, y, _ in conexionesArray]

    # Crear el modelo
    mdl = Model(name='MaxCut')

    # Variables de decisión
    z = mdl.integer_var_list(num_vertices, lb=-1, ub=1, name='z')

    # Función objetivo
    objective = mdl.sum(z[j] * z[k] for j, k in edges)

    mdl.minimize(objective)

    # Resolver el modelo
    solution = mdl.solve()

    return mdl

def formularProblemaQiskit(mdl):

    # Conversión a Qiskit a partir del docplex
    qp = from_docplex_mp(mdl)

    return qp

def formularProblemaDwave(qp):

    conv = QuadraticProgramToQubo()

    # Pasar QuadraticProgram a QUBO
    problemConverted = conv.convert(qp)

    # Pasar QUBO a bqm
    bqm_binary = dimod.as_bqm(problemConverted.objective.linear.to_array(), problemConverted.objective.quadratic.to_array(), dimod.BINARY)

    return bqm_binary


def metodoSimuladorLocal(qp):

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=100)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = 1) # TODO cambiar a parametro
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

def metodoAnnealer(bqm_binary): # TODO cambiar a parametro el num_reads

    # Resolver el modelo dimod
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(bqm_binary, num_reads=100)

    return result

def metodoSimulatedAnnealingSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = neal.SimulatedAnnealingSampler()
    result = solver.sample(bqm_binary, num_reads=200)

    return result

def metodoTabuSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = tabu.TabuSampler()
    result = solver.sample(bqm_binary , num_reads = 10)

    return result

def metodoSteepestDescentSolver(bqm_binary):

    # Resolver el modelo dimod
    solver = greedy.SteepestDescentSolver()
    result = solver.sample(bqm_binary , num_reads = 10)

    return result

def experimento1():

    # Variables para ir guardando resultados

    # Porcentaje de veces que se obtiene la solución óptima
    porcentajeSolucionOptimaQAOALocal, porcentajeSolucionOptimaQAOAReal, porcentajeSolucionOptimaAnnealer = 0, 0, 0

    # Porcentaje de veces que se obtiene una solución que cumple las restricciones
    porcentajeSolucionCumpleRestriccionesQAOALocal, porcentajeSolucionCumpleRestriccionesQAOAReal, porcentajeSolucionCumpleRestriccionesAnnealer  = 0, 0, 0

    # Energía media de las soluciones obtenidas
    energiaMediaQAOALocal, energiaMediaQAOAReal, energiaMediaAnnealer = 0, 0, 0

    # Energía media de las soluciones óptimas
    energiaMediaOptimaQAOALocal, energiaMediaOptimaQAOAReal, energiaMediaOptimaAnnealer = 0, 0, 0

    grafosAleatorios = []

    for num_vertices in range(5, 11):
        num_instancias = 5  # Número de instancias a generar para cada número de vértices
        instancias = generarGrafoAleatorio(num_vertices, num_instancias)
        grafosAleatorios.extend(instancias)

    print(grafosAleatorios)

    for grafo in grafosAleatorios:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroVertices'], grafo['conexiones'], 1)
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal = metodoSimuladorLocal(qp)
        ##resultQAOAReal = metodoSimuladorReal(qp) # TODO de momento no
        #resultAnnealer = metodoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal)
        ##estadisticasQAOAReal = obtenerEstadisticas(resultQAOAReal) # TODO de momento no
        #estadisticasAnnealer = obtenerEstadisticas(resultAnnealer)

        # Actualizar resultados
        porcentajeSolucionOptimaQAOALocal += estadisticasQAOALocal[0]
        #porcentajeSolucionOptimaQAOAReal += estadisticasQAOAReal['solucion_optima'] # TODO de momento no
        #porcentajeSolucionOptimaAnnealer += estadisticasAnnealer['solucion_optima']

        porcentajeSolucionCumpleRestriccionesQAOALocal += estadisticasQAOALocal[1]
        ##porcentajeSolucionCumpleRestriccionesQAOAReal += estadisticasQAOAReal['solucion_cumple_restricciones'] # TODO de momento no
        #porcentajeSolucionCumpleRestriccionesAnnealer += estadisticasAnnealer['solucion_cumple_restricciones']

        energiaMediaQAOALocal += estadisticasQAOALocal[2]
        ##energiaMediaQAOAReal += estadisticasQAOAReal['energia_media'] # TODO de momento no
        #energiaMediaAnnealer += estadisticasAnnealer['energia_media']

        energiaMediaOptimaQAOALocal += estadisticasQAOALocal[3]
        ##energiaMediaOptimaQAOAReal += estadisticasQAOAReal['energia_media_optima'] # TODO de momento no
        #energiaMediaOptimaAnnealer += estadisticasAnnealer['energia_media_optima']

    # Calcular medias
    porcentajeSolucionOptimaQAOALocal /= len(grafosAleatorios)
    #porcentajeSolucionOptimaQAOAReal /= len(grafosAleatorios)
    #porcentajeSolucionOptimaAnnealer /= len(grafosAleatorios)

    porcentajeSolucionCumpleRestriccionesQAOALocal /= len(grafosAleatorios)
    #porcentajeSolucionCumpleRestriccionesQAOAReal /= len(grafosAleatorios)
    #porcentajeSolucionCumpleRestriccionesAnnealer /= len(grafosAleatorios)

    energiaMediaQAOALocal /= len(grafosAleatorios)
    #energiaMediaQAOAReal /= len(grafosAleatorios)
    #energiaMediaAnnealer /= len(grafosAleatorios)

    energiaMediaOptimaQAOALocal /= len(grafosAleatorios)
    #energiaMediaOptimaQAOAReal /= len(grafosAleatorios)
    #energiaMediaOptimaAnnealer /= len(grafosAleatorios)

    # Imprimir resultados
    print('Porcentaje de veces que se obtiene la solución óptima:')
    print('QAOA local: ' + str(porcentajeSolucionOptimaQAOALocal))
    #print('QAOA real: ' + str(porcentajeSolucionOptimaQAOAReal))
    #print('Annealer: ' + str(porcentajeSolucionOptimaAnnealer))

    print('Porcentaje de veces que se obtiene una solución que cumple las restricciones:')
    print('QAOA local: ' + str(porcentajeSolucionCumpleRestriccionesQAOALocal))
    #print('QAOA real: ' + str(porcentajeSolucionCumpleRestriccionesQAOAReal))
    #print('Annealer: ' + str(porcentajeSolucionCumpleRestriccionesAnnealer))

    print('Energía media de las soluciones obtenidas:')
    print('QAOA local: ' + str(energiaMediaQAOALocal))
    #print('QAOA real: ' + str(energiaMediaQAOAReal))
    #print('Annealer: ' + str(energiaMediaAnnealer))

    print('Energía media de las soluciones óptimas:')
    print('QAOA local: ' + str(energiaMediaOptimaQAOALocal))
    #print('QAOA real: ' + str(energiaMediaOptimaQAOAReal))
    #print('Annealer: ' + str(energiaMediaOptimaAnnealer))


def generarGrafoAleatorio(numeroVertices, numInstancias):
    instancias = []

    for _ in range(numInstancias):
        # Generar todas las posibles conexiones entre los vértices
        conexiones = [(i, j) for i in range(numeroVertices) for j in range(i + 1, numeroVertices)]

        # Seleccionar aleatoriamente un subconjunto de conexiones
        numConexiones = random.randint(1, len(conexiones))
        conexionesSeleccionadas = random.sample(conexiones, numConexiones)

        # Crear el diccionario de la instancia
        instancia = {
            'numeroVertices': numeroVertices,
            'conexiones': conexionesSeleccionadas
        }

        instancias.append(instancia)

    return instancias

def obtenerEstadisticasQAOA(result):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = result.optimal
    print("¿Se ha obtenido la solución óptima?", solucion_optima)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = result.feasible
    print("¿La solución cumple las restricciones?", cumple_restricciones)

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = result.fval
    print("Energía de la solución obtenida:", energia_solucion_obtenida)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = result.fval_optimal
    print("Energía de la solución óptima:", energia_solucion_optima)

    # Crear un array con los valores
    resultados = [solucion_optima, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Devolver el array de resultados
    return resultados

def obtenerEstadisticas(result):

    # Contadores de estadísticas
    solucion_optima = 0
    solucion_cumple_restricciones = 0
    energias = []
    energia_optima = float('inf')

    # Recorrer los resultados obtenidos
    for sample in result.samples():
        # Verificar si la solución es óptima
        if sample.energy == result.optimal_value:
            solucion_optima += 1

        # Verificar si la solución cumple las restricciones
        #if cumpleRestricciones(sample):  # Definir función cumpleRestricciones()
        #    solucion_cumple_restricciones += 1

        # Agregar la energía de la solución a la lista
        energias.append(sample.energy)

        # Actualizar la energía óptima si corresponde
        if sample.energy < energia_optima:
            energia_optima = sample.energy

    # Calcular porcentajes y energía media
    porcentaje_solucion_optima = solucion_optima / len(result.samples()) * 100
    porcentaje_solucion_cumple_restricciones = solucion_cumple_restricciones / len(result.samples()) * 100
    energia_media = sum(energias) / len(energias)

    # Imprimir resultados
    print("Porcentaje de veces que se obtiene la solución óptima:", porcentaje_solucion_optima)
    print("Porcentaje de veces que se obtiene una solución que cumple las restricciones:", porcentaje_solucion_cumple_restricciones)
    print("Energía media de las soluciones obtenidas:", energia_media)
    print("Energía de la solución óptima:", energia_optima)

# Generar los modelos
mdl = formularProblemaDocplex(numeroNodos, conexionesArray, repeticiones)
qp = formularProblemaQiskit(mdl)
bqm = formularProblemaDwave(qp)

result = None

# Resolver el problema utilizando el método seleccionado
if metodo == "simuladorLocal":
    result = metodoSimuladorLocal(qp)
elif metodo == "simuladorRemoto":
    result = metodoSimuladorRemoto(qp)
elif metodo == "simuladorReal":
    result = metodoSimuladorReal(qp)
elif metodo == "annealer":
    result = metodoAnnealer(bqm)
elif metodo == "annealerSimulatedAnnealingSolver":
    result = metodoSimulatedAnnealingSolver(bqm)
elif metodo == "annealerTabuSolver":
    result = metodoTabuSolver(bqm)
elif metodo == "annealerSteepestDescentSolver":
    result = metodoSteepestDescentSolver(bqm)
elif metodo == "experimento1":
    experimento1()

print(result)



