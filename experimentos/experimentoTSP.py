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


def formularProblemaDocplex(numeroNodos, conexionesArray):

    ##
    ## DATOS DEL PROBLEMA
    ##
    cities = list(range(int(numeroNodos)))
    connections = conexionesArray

    # Pesos
    w = {(j, k): cost for j, k, cost in connections}

    ####################
    ## MODELO docplex ##
    ####################
    mdl = Model(name="TSP")

    # Variables binarias
    x = {(j, l): mdl.binary_var(name=f"x{j}{l}") for j in cities for l in cities}

    # Restricción 1
    for j in cities:
        mdl.add_constraint(mdl.sum(x[(j, l)] for l in cities) == 1)

    # Restricción 2
    for l in cities:
        mdl.add_constraint(mdl.sum(x[(j, l)] for j in cities) == 1)

    # Expresión del costo
    total_cost = mdl.sum(w[(j, k)] * x[(j, l)] * x[(k, (l + 1))] for l in range(len(cities)) for j in cities for k in cities if j != k if(j,k) in w if (j,l) in x and(k, l+1) in x)
    mdl.minimize(total_cost)

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

    return result

def metodoExactoAnnealer(bqm_binary):

    sampler = dimod.ExactSolver()
    result = sampler.sample(bqm_binary)

    return result

def experimento1(numGrafosMin, numGrafosMax, numInstancias, pesoMaximo):

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
        instancias = generarGrafoAleatorioTSP(num_vertices, numInstancias, pesoMaximo)
        grafosAleatorios.extend(instancias)

    print(len(grafosAleatorios))

    for grafo in grafosAleatorios:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroVertices'], grafo['conexiones'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal = metodoSimuladorLocal(qp, shots, reps)
##        resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal)
##        estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultAnnealerOptimal)
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal)

        # Actualizar resultados
        porcentajeSolucionOptimaQAOALocal += estadisticasQAOALocal[0]
        porcentajeSolucionCumpleRestriccionesQAOALocal += estadisticasQAOALocal[1]
        energiaMediaQAOALocal += estadisticasQAOALocal[2]
        energiaMediaOptimaQAOALocal += estadisticasQAOALocal[3]

##        porcentajeSolucionOptimaQAOAReal += estadisticasQAOAReal[0]
##        porcentajeSolucionCumpleRestriccionesQAOAReal += estadisticasQAOAReal[1]
##        energiaMediaQAOAReal += estadisticasQAOAReal[2]
##        energiaMediaOptimaQAOAReal += estadisticasQAOAReal[3]

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
##    porcentajeSolucionOptimaQAOAReal /= len(grafosAleatorios) * 0.01
##    porcentajeSolucionCumpleRestriccionesQAOAReal /= len(grafosAleatorios) * 0.01
##    energiaMediaQAOAReal /= len(grafosAleatorios)
##    energiaMediaOptimaQAOAReal /= len(grafosAleatorios)

    # Annealer
    porcentajeSolucionOptimaAnnealer /= len(grafosAleatorios) * 0.01
    porcentajeSolucionCumpleRestriccionesAnnealer /= len(grafosAleatorios) * 0.01
    energiaMediaAnnealer /= len(grafosAleatorios)
    energiaMediaOptimaAnnealer /= len(grafosAleatorios)

    print("")
    ## Imprimir resultados
    imprimirResultadosExperimento('QAOA local: ', porcentajeSolucionOptimaQAOALocal, porcentajeSolucionCumpleRestriccionesQAOALocal, energiaMediaQAOALocal, energiaMediaOptimaQAOALocal)
##    imprimirResultadosExperimento('QAOA Real: ', porcentajeSolucionOptimaQAOAReal, porcentajeSolucionCumpleRestriccionesQAOAReal, energiaMediaQAOAReal, energiaMediaOptimaQAOAReal)
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

def generarGrafoAleatorioTSP(numeroVertices, numInstancias, pesoMaximoConexion):
    instancias = []

    for _ in range(numInstancias):
        # Generar todas las posibles conexiones entre los vértices
        conexiones = [(i, j, random.randint(1, pesoMaximoConexion)) for i in range(numeroVertices) for j in range(i + 1, numeroVertices)]

        # Generar un conjunto de conexiones que forme un camino que visite todos los nodos
        nodos_visitados = set()
        camino = []
        nodo_actual = random.randint(0, numeroVertices - 1)
        nodos_visitados.add(nodo_actual)

        while len(nodos_visitados) < numeroVertices:
            nodos_no_visitados = [nodo for nodo in range(numeroVertices) if nodo not in nodos_visitados]
            siguiente_nodo = random.choice(nodos_no_visitados)
            peso = random.randint(1, pesoMaximoConexion)
            camino.append((nodo_actual, siguiente_nodo, peso))
            nodos_visitados.add(siguiente_nodo)
            nodo_actual = siguiente_nodo

        # Combinar las conexiones seleccionadas con el camino generado
        conexionesSeleccionadas = random.sample(conexiones, numInstancias - 1)
        conexionesSeleccionadas.extend(camino)

        # Crear el diccionario de la instancia
        instancia = {
            'numeroVertices': numeroVertices,
            'conexiones': conexionesSeleccionadas
        }

        instancias.append(instancia)

    return instancias

def cumpleRestriccionesTSPAnnealer(result):

    n_nodos = int(len(result.first.sample)**(1/2))

    # Restricción 1: cada vértice se visita solamente una vez
    for parts in range(0, len(result.first.sample)-1, n_nodos):
        sum = 0
        for i in range(parts, parts + n_nodos):
            if result.first[0][i] == 1:
                sum+=1
        if sum > 1:
            return False

    # Restricción 2: solo se puede visitar una ciudad a la vez
    for i in range(0, n_nodos):
        sum = 0
        for j in range(0, n_nodos, 1):
            if result.first[0][i+(n_nodos*j)] == 1:
                sum += 1
        if sum > 1:
            return False

    return True

def obtenerEstadisticasAnnealer(result, optimalResult):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    print("\nAnnealer: ¿Se ha obtenido la solución óptima?", solucion_optima==solucion_obtenida)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesTSPAnnealer(result)
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


def obtenerEstadisticasQAOA(result, optimalResult):

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
    cumple_restricciones = result.status.name == 'SUCCESS'
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

experimento1(3, 5, 1, 20)