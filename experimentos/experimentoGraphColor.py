import random

import dimod
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
from qiskit.providers.ibmq import least_busy

def formularProblemaDocplex(numeroNodos, numeroColores, edges):

    ##
    ## DATOS DEL PROBLEMA
    ##
    num_vertices = numeroNodos
    num_colors = numeroColores
    edges = edges

    ####################
    ## MODELO docplex ##
    ####################
    mdl = Model(name='Graph Coloring')

    # Diccionario para guardar las variables binarias
    x = {}

    # Crear variables binarias para cada vértice y combinación de color
    for j in range(num_vertices):
        for l in range(num_colors):
            x[j, l] = mdl.binary_var(name=f'x{j}{l}')

    # Definir función objetivo teniendo en cuenta penalty terms
    objective = mdl.sum((mdl.sum(x[j, l] for l in range(num_colors)) - 1) ** 2 for j in range(num_vertices))
    objective += mdl.sum(x[j, l] * x[h, l] for (j, h) in edges for l in range((num_colors)-1))

    # Para ayudar a distinguir mejor entre soluciones que cumplan las restricciones y las que no
    constanteEnergia = 20

    mdl.minimize(objective*constanteEnergia)

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

def metodoSimuladorLocal(qp, shots, reps):

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=shots)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = reps) # TODO cambiar a parametro
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    result = qaoa_optimizer.solve(qp)

    #print(result)

    return result

def metodoSimuladorReal(qp, reps, num_nodos):

    provider = IBMQ.load_account()

    backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= num_nodos and
                                                             not x.configuration().simulator and x.status().operational == True))

    qaoa_client = QAOAClient(provider=provider , backend=backend, reps=reps)

    qaoa = MinimumEigenOptimizer(qaoa_client)

    # Resuelve el problema utilizando el algoritmo QAOA
    result = qaoa.solve(qp)

    return result

def metodoAnnealer(bqm_binary, num_reads):

    # Resolver el modelo dimod
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(bqm_binary, num_reads=num_reads)

    # print(result)

    return result

def metodoExactoAnnealer(bqm_binary):

    sampler = dimod.ExactSolver()
    result = sampler.sample(bqm_binary)

    return result

def experimento1(numGrafosMin, numGrafosMax, numInstancias):

    #
    # Variables para ir guardando resultados
    #

    # Porcentaje de veces que se obtiene la solución óptima
    porcentajeSolucionOptimaQAOALocal, porcentajeSolucionOptimaQAOAReal, porcentajeSolucionOptimaAnnealer = 0, 0, 0

    # Porcentaje de veces que se obtiene una solución que cumple las restricciones
    porcentajeSolucionCumpleRestriccionesQAOALocal, porcentajeSolucionCumpleRestriccionesQAOAReal, porcentajeSolucionCumpleRestriccionesAnnealer  = 0, 0, 0

    # Energía media de las soluciones obtenidas
    energiaMediaQAOALocal, energiaMediaQAOAReal, energiaMediaAnnealer = 0, 0, 0

    # Energía media de las soluciones óptimas
    energiaMediaOptimaQAOALocal, energiaMediaOptimaQAOAReal, energiaMediaOptimaAnnealer = 0, 0, 0

    #
    # Generar grafos aleatorios
    #
    grafosAleatorios = []

    for num_vertices in range(numGrafosMin, numGrafosMax):
        # Número de instancias a generar para cada número de vértices
        instancias = generarGrafoAleatorioGraphColor(num_vertices, numInstancias)
        grafosAleatorios.extend(instancias)

    print(len(grafosAleatorios))

    for grafo in grafosAleatorios:

        print(f"Numero de nodos: ", grafo['numeroNodos'], "\nNumero de colores: ", grafo['numeroColores'], "\nConexiones: ", grafo['edges'])
        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroNodos'], grafo['numeroColores'], grafo['edges'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal = metodoSimuladorLocal(qp, shots, reps)
        # resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, grafo['edges'], grafo['numeroColores'])
        # estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultAnnealerOptimal)
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['edges'], grafo['numeroColores'])

        # Actualizar resultados
        porcentajeSolucionOptimaQAOALocal += estadisticasQAOALocal[0]
        porcentajeSolucionCumpleRestriccionesQAOALocal += estadisticasQAOALocal[1]
        energiaMediaQAOALocal += estadisticasQAOALocal[2]
        energiaMediaOptimaQAOALocal += estadisticasQAOALocal[3]

        # porcentajeSolucionOptimaQAOAReal += estadisticasQAOAReal[0]
        # porcentajeSolucionCumpleRestriccionesQAOAReal += estadisticasQAOAReal[1]
        # energiaMediaQAOAReal += estadisticasQAOAReal[2]
        # energiaMediaOptimaQAOAReal += estadisticasQAOAReal[3]

        porcentajeSolucionOptimaAnnealer += estadisticasAnnealer[0]
        porcentajeSolucionCumpleRestriccionesAnnealer += estadisticasAnnealer[1]
        energiaMediaAnnealer += estadisticasAnnealer[2]
        energiaMediaOptimaAnnealer += estadisticasAnnealer[3]

    ## Calcular medias
    # QAOA Local
    porcentajeSolucionOptimaQAOALocal /= len(grafosAleatorios) * 0.01
    porcentajeSolucionCumpleRestriccionesQAOALocal /= len(grafosAleatorios) * 0.01
    energiaMediaQAOALocal /= len(grafosAleatorios)
    energiaMediaOptimaQAOALocal /= len(grafosAleatorios)

    ## QAOA Real
    porcentajeSolucionOptimaQAOAReal /= len(grafosAleatorios) * 0.01
    porcentajeSolucionCumpleRestriccionesQAOAReal /= len(grafosAleatorios) * 0.01
    energiaMediaQAOAReal /= len(grafosAleatorios)
    energiaMediaOptimaQAOAReal /= len(grafosAleatorios)

    # Annealer
    porcentajeSolucionOptimaAnnealer /= len(grafosAleatorios) * 0.01
    porcentajeSolucionCumpleRestriccionesAnnealer /= len(grafosAleatorios) * 0.01
    energiaMediaAnnealer /= len(grafosAleatorios)
    energiaMediaOptimaAnnealer /= len(grafosAleatorios)

    print("")
    ## Imprimir resultados
    imprimirResultadosExperimento('QAOA local: ', porcentajeSolucionOptimaQAOALocal, porcentajeSolucionCumpleRestriccionesQAOALocal, energiaMediaQAOALocal, energiaMediaOptimaQAOALocal)
    # imprimirResultadosExperimento('QAOA Real: ', porcentajeSolucionOptimaQAOAReal, porcentajeSolucionCumpleRestriccionesQAOAReal, energiaMediaQAOAReal, energiaMediaOptimaQAOAReal)
    imprimirResultadosExperimento('Annealer: ', porcentajeSolucionOptimaAnnealer, porcentajeSolucionCumpleRestriccionesAnnealer, energiaMediaAnnealer, energiaMediaOptimaAnnealer)

def imprimirResultadosExperimento(metodo, porcentajeSolucionOptima, porcentajeSolucionCumpleRestricciones, energiaMedia, energiaMediaOptima):

    print('Porcentaje de veces que se obtiene la solución óptima:')
    print(metodo + str(porcentajeSolucionOptima))
    print('Porcentaje de veces que se obtiene una solución que cumple las restricciones:')
    print(metodo + str(porcentajeSolucionCumpleRestricciones))
    print('Energía media de las soluciones obtenidas:')
    print(metodo + str(energiaMedia))
    print('Energía media de las soluciones óptimas:')
    print(metodo + str(energiaMediaOptima))
    print("")

def generarGrafoAleatorioGraphColor(numeroVertices, numInstancias):
    instancias = []

    for _ in range(numInstancias):

        numeroNodos = numeroVertices
        numeroColores = random.randint(2,numeroNodos)
        edges = []

        # Generar conexiones aleatorias
        for i in range(numeroNodos):
            for j in range(i + 1, numeroNodos):
                if random.random() < 0.6:
                    edges.append((i, j))

        # Crear el diccionario de la instancia
        instancia = {
            'numeroNodos': numeroNodos,
            'numeroColores': numeroColores,
            'edges': edges
        }

        instancias.append(instancia)

    return instancias

def cumpleRestriccionesGraphColorAnnealer(result, conexiones, numeroColores):

    nodos = int(len(result[0])/numeroColores)

    colores = {}

    # Restricción 1: cada vértice recibe solamente un color
    for i in range(nodos):
        sum = 0
        for j in range(numeroColores):
            sum += result[0][j+((numeroColores)*i)]
            if(result[0][j+((numeroColores)*i)] != 0):
                colores[i] = j
        if sum > 1:
            return False

    # Restricción 2: vértices adyacentes no pueden tener el mismo color
    for i, j in conexiones:
            if(colores[i] == colores[j]):
                return False

    return True

def obtenerEstadisticasAnnealer(result, optimalResult, conexiones, numColores):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    print("\nAnnealer: ¿Se ha obtenido la solución óptima?", solucion_optima==solucion_obtenida)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesGraphColorAnnealer(result.first, conexiones, numColores)
    print("Annealer: ¿La solución cumple las restricciones?", cumple_restricciones)

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = solucion_obtenida
    print("Annealer: Energía de la solución obtenida:", energia_solucion_obtenida)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = solucion_optima
    print("Annealer: Energía de la solución óptima:", energia_solucion_optima)

    # Crear un array con los valores
    resultados = [solucion_optima==solucion_obtenida, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Devolver el array de resultados
    return resultados


def obtenerEstadisticasQAOA(result, optimalResult, conexiones, numColores):

    n = 0

    todosDatos = optimalResult.data()

    for valor in result.x:

        # Filtrar entre todas las soluciones la que se ha obtenido con QAOA
        todosDatos = [solucion for solucion in todosDatos if solucion.sample.get(n) == valor]
        n += 1

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy == todosDatos[0].energy ## Comparar con el resultado optimo
    print("\nQAOA: ¿Se ha obtenido la solución óptima?", solucion_optima)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesGraphColorAnnealer(todosDatos[0], conexiones, numColores)
    print("QAOA: ¿La solución cumple las restricciones?", cumple_restricciones)

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = todosDatos[0].energy
    print("QAOA: Energía de la solución obtenida:", energia_solucion_obtenida)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = optimalResult.first.energy
    print("QAOA: Energía de la solución óptima:", energia_solucion_optima)

    # Crear un array con los valores
    resultados = [solucion_optima, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Devolver el array de resultados
    return resultados

reps = 1
shots = 1024
num_reads = 100

experimento1(3, 5, 1)