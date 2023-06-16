import random

import dimod
from dwave.system import DWaveSampler
from dwave.system import EmbeddingComposite
from qiskit import IBMQ
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit.opflow import PauliOp
from qiskit.quantum_info import Pauli
from qiskit.quantum_info import Statevector
from qiskit.utils import QuantumInstance
from qiskit_aer import Aer
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer
from qiskit_optimization.runtime import QAOAClient
from qiskit.providers.ibmq import least_busy

def metodoSimuladorLocal(num_nodos, conexiones, shots):

    # Creamos los términos de Pauli correspondientes a las conexiones
    pauli_terms = []
    for nodo1, nodo2 in conexiones:
        z_positions = [0] * num_nodos
        z_positions[(len(z_positions)-1)-nodo1] = 1
        z_positions[(len(z_positions)-1)-nodo2] = 1
        pauli_term = PauliOp(Pauli((z_positions, [0] * num_nodos)))
        pauli_terms.append(pauli_term)

    # Suma de los términos de Pauli
    H1 = sum(pauli_terms)

    quantum_instance = QuantumInstance(Aer.get_backend("aer_simulator"),shots = shots)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance)
    result = qaoa.compute_minimum_eigenvalue(H1)

    # Probar todos los posibles expectationValue
    expectationValue = 0
    for x in range(len(result.eigenstate)):
        psi = Statevector.from_int(x, dims = 2**num_nodos)
        if(expectationValue > psi.expectation_value(H1)):
            expectationValue = psi.expectation_value(H1) # Guardar la menor energía obtenida

    return expectationValue.real

def metodoSimuladorReal(num_nodos, conexiones, reps):

    # Creamos los términos de Pauli correspondientes a las conexiones
    pauli_terms = []
    for nodo1, nodo2 in conexiones:
        z_positions = [0] * num_nodos
        z_positions[(len(z_positions) - 1) - nodo1] = 1
        z_positions[(len(z_positions) - 1) - nodo2] = 1
        pauli_term = PauliOp(Pauli((z_positions, [0] * num_nodos)))
        pauli_terms.append(pauli_term)

    # Suma de los términos de Pauli
    H1 = sum(pauli_terms)

    # Cargar cuenta y obtener backend
    provider = IBMQ.load_account()
    backend = least_busy(provider.backends(filters=lambda x: x.configuration().n_qubits >= num_nodos and
                                                             not x.configuration().simulator and x.status().operational == True))
    print("Ejecutando en:", backend)

    # Configurar QuantumInstance con el backend seleccionado
    quantum_instance = QuantumInstance(backend, shots=shots)

    qaoa = QAOA(optimizer=COBYLA(), quantum_instance=quantum_instance)
    result = qaoa.compute_minimum_eigenvalue(H1)

    # Probar todos los posibles expectationValue
    expectationValue = 0
    for x in range(len(result.eigenstate)):
        psi = Statevector.from_int(x, dims=2**num_nodos)
        if expectationValue > psi.expectation_value(H1):
            expectationValue = psi.expectation_value(H1)  # Guardar la menor energía obtenida

    return expectationValue.real

def metodoAnnealer(conexiones, num_reads):

    J = {(nodo1, nodo2): 1 for nodo1, nodo2 in conexiones}
    h = {}
    problem = dimod.BinaryQuadraticModel(h, J, 0.0, dimod.SPIN)

    # Resolver el modelo dimod
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(problem, num_reads=num_reads)

    return result, problem

def metodoExactoAnnealer(problem):

    sampler = dimod.ExactSolver()
    result = sampler.sample(problem)

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
    #
    for num_vertices in range(numGrafosMin,numGrafosMax):
        num_instancias = numInstancias  # Número de instancias a generar para cada número de vértices
        instancias = generarGrafoAleatorio(num_vertices, num_instancias)
        grafosAleatorios.extend(instancias)

    for grafo in grafosAleatorios:

        # Resolver el problema
        resultAnnealer, problem = metodoAnnealer(grafo['conexiones'], num_reads_annealer)
        resultQAOALocal = metodoSimuladorLocal(grafo['numeroVertices'], grafo['conexiones'], shots)
##        resultQAOAReal = metodoSimuladorReal(grafo['numeroVertices'], grafo['conexiones'], reps)
        resultAnnealerOptimal = metodoExactoAnnealer(problem)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal)
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal)
##        estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultQAOAOptimal)

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

def cumpleRestriccionesMaxCut():

    # La restricción es que se usen valores binarios, para indicar que el vértice
    # se encuentra en un grupo o en otro
    return True

def obtenerEstadisticasAnnealer(result, optimalResult):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

##    print("\nAnnealer: ¿Se ha obtenido la solución óptima?", solucion_optima==solucion_obtenida)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesMaxCut()
##    print("Annealer: ¿La solución cumple las restricciones?", cumple_restricciones)

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = solucion_obtenida
##    print("Annealer: Energía de la solución obtenida:", energia_solucion_obtenida)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = solucion_optima
##    print("Annealer: Energía de la solución óptima:", energia_solucion_optima)

    # Crear un array con los valores
    resultados = [solucion_optima==solucion_obtenida, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Devolver el array de resultados
    return resultados


def obtenerEstadisticasQAOA(result, optimalResult):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy == result ## Comparar con el resultado optimo
##    print("\nQAOA: ¿Se ha obtenido la solución óptima?", solucion_optima)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesMaxCut()
##    print("QAOA: ¿La solución cumple las restricciones?", cumple_restricciones)

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = result
##    print("QAOA: Energía de la solución obtenida:", energia_solucion_obtenida)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = optimalResult.first.energy
##    print("QAOA: Energía de la solución óptima:", energia_solucion_optima)

    # Crear un array con los valores
    resultados = [solucion_optima, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Devolver el array de resultados
    return resultados


num_reads_annealer = 100
shots = 1024
reps = 1

experimento1(5,6,1)