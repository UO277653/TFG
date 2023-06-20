import random
import time
import dimod
import numpy as np

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
import time

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

    # Establecer las seeds
    seed = 277653
    np.random.seed(277653)

    quantum_instance = QuantumInstance(Aer.get_backend("aer_simulator"),shots = shots, seed_simulator=seed, seed_transpiler=seed)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance, reps=reps, initial_point=np.random.uniform(0, 2*np.pi, 2*reps)) # np.ones(2*reps)

    inicio = time.time()
    result = qaoa.compute_minimum_eigenvalue(H1)
    start = time.time()
    tiempoCalculo = (int((start - inicio)*1000))/shots

    datosResultados = {}

    # Probar todos los posibles expectationValue
    expectationValue = float('inf')
    for x in result.eigenstate:
        psi = Statevector.from_label(x)
        valorEstado = psi.expectation_value(H1)

        datosResultados[x] = [int((result.eigenstate[x])**2 * shots), valorEstado.real]
        if(expectationValue > valorEstado):
            expectationValue = psi.expectation_value(H1) # Guardar la menor energía obtenida

    print(datosResultados)

    return expectationValue.real, datosResultados, tiempoCalculo

def metodoSimuladorReal(num_nodos, conexiones):

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
    seed = 277653

    quantum_instance = QuantumInstance(backend, shots=shots, seed_simulator=seed, seed_transpiler=seed)

    qaoa = QAOA(optimizer=COBYLA(), quantum_instance=quantum_instance, reps=reps, initial_point=np.ones(2*reps))
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

def obtenerEstadisticasAnnealer(result, optimalResult, nNodos):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    comparativaSoluciones = {}
    array_sol_optima = []
    n = 0

    for res in result.data_vectors['energy']:
        comparativaSoluciones[res] = solucion_optima == res ## TODO tengo que usar el vector, no la energia, que lo cambie en el for
        for i in range(0, result.data_vectors['num_occurrences'][n]):
            array_sol_optima.append(comparativaSoluciones[res])
        n += 1

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesMaxCut()

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    n = 0

    for res in result.data_vectors['energy']:
        for i in range(0, result.data_vectors['num_occurrences'][n]):
            array_sol_obtenida.append(str(res))
        n += 1

    # Obtener la energía de la solución óptima
    energia_solucion_optima = solucion_optima

    # Crear un array con los valores
    resultados = [solucion_optima==solucion_obtenida, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    metodo = "Annealer"
    crearArchivoTxt("ultimosDatosAnnealer.txt", "Max-Cut", nNodos, metodo, array_sol_optima, True, array_sol_obtenida, optimalResult.first.energy, 0)

    # Devolver el array de resultados
    return resultados

def obtenerEstadisticasQAOA(result, optimalResult, datosResultados, nNodos, tiempoQAOA):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy == result ## Comparar con el resultado optimo

    comparativaSoluciones = {}
    array_sol_optima = []

    for solucion in datosResultados:
        comparativaSoluciones[solucion] = datosResultados[solucion][1] == optimalResult.first.energy
        for i in range(0, datosResultados[solucion][0]):
            array_sol_optima.append(comparativaSoluciones[solucion])

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesMaxCut()


    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    for solucion in datosResultados:
        for i in range(0, datosResultados[solucion][0]):
            array_sol_obtenida.append(datosResultados[solucion][1])
            energia_solucion_obtenida += datosResultados[solucion][1]

    energia_solucion_obtenida /= len(datosResultados)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = optimalResult.first.energy

    # Crear un array con los valores
    resultados = [solucion_optima, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    metodo = "Simulación QAOA (reps=" +  str(reps) + ")"
    crearArchivoTxt("ultimosDatosSimulacionQAOA.txt", "Max-Cut", nNodos, metodo, array_sol_optima, True, array_sol_obtenida, optimalResult.first.energy, tiempoQAOA)


    # Devolver el array de resultados
    return resultados

def crearArchivoTxt(nombreArchivo, problema, nNodos, metodo, vectorSolOptima, cumpleRestricciones, vectorEnergiaSolObtenida, energiaSolOptima, tiempo):

    n = 0

    with open(nombreArchivo, 'a') as archivo:
        for sol in vectorSolOptima:
            aEscribir = str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(sol) + "," + str(cumpleRestricciones) + "," + str(vectorEnergiaSolObtenida[n]) + "," + str(energiaSolOptima) + "," + str(tiempo) + "\n"
            archivo.write(str(aEscribir))
            n+=1

def leerInstancias(nombreArchivo, numGrafosMin, numGrafosMax):
    instancias = []

    with open(nombreArchivo, 'r') as archivo:
        lineas = archivo.readlines()

        for linea in lineas:
            numeroVertices, conexiones = linea.strip().split('-')
            numeroVertices = int(numeroVertices)

            if(numeroVertices < numGrafosMin or numeroVertices > numGrafosMax):
                continue

            # Crear el diccionario de la instancia
            instancia = {
                'numeroVertices': numeroVertices,
                'conexiones': []
            }

            conexiones = conexiones.split(';')
            conexiones = conexiones[:-1]

            # Leer las conexiones de la instancia
            for con in conexiones:
                num1, num2 = con.split(',')
                instancia['conexiones'].append((int(num1), int(num2)))

            instancias.append(instancia)

    return instancias

def experimento1(numGrafosMin, numGrafosMax, numInstancias):

    # Limpiar archivos en los que se van a exportar los datos
    with open("ultimosDatosSimulacionQAOA.txt", 'w') as archivo:
        archivo.write("")

    with open("ultimosDatosAnnealer.txt", 'w') as archivo:
        archivo.write("")

    # Variables para ir guardando resultados
    porcentajeSolucionOptimaQAOALocal, porcentajeSolucionOptimaQAOAReal, porcentajeSolucionOptimaAnnealer = 0, 0, 0
    porcentajeSolucionCumpleRestriccionesQAOALocal, porcentajeSolucionCumpleRestriccionesQAOAReal, porcentajeSolucionCumpleRestriccionesAnnealer  = 0, 0, 0
    energiaMediaQAOALocal, energiaMediaQAOAReal, energiaMediaAnnealer = 0, 0, 0
    energiaMediaOptimaQAOALocal, energiaMediaOptimaQAOAReal, energiaMediaOptimaAnnealer = 0, 0, 0

    # Generar grafos aleatorios
    datosGrafos = {}
    n = 0
    grafosAleatorios = []

    grafosAleatorios.extend(leerInstancias("grafosMaxCut.txt", numGrafosMin, numGrafosMax))

    for grafo in grafosAleatorios:

        # Resolver el problema
        resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(grafo['numeroVertices'], grafo['conexiones'], shots)
        ##        resultQAOAReal = metodoSimuladorReal(grafo['numeroVertices'], grafo['conexiones'])
        resultAnnealer, problem = metodoAnnealer(grafo['conexiones'], num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(problem)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'])
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA)
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

        datosGrafos[grafo['numeroVertices'], n] = {
            'estadisticasQAOALocal': estadisticasQAOALocal,
            'estadisticasAnnealer': estadisticasAnnealer
        }

        n += 1

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

    for dato in datosGrafos:
        print(dato, " QAOA Local: ", datosGrafos[dato]['estadisticasQAOALocal'], " Annealer:", datosGrafos[dato]['estadisticasAnnealer'])

    print("")
    ## Imprimir resultados
    imprimirResultadosExperimento('QAOA local: ', porcentajeSolucionOptimaQAOALocal, porcentajeSolucionCumpleRestriccionesQAOALocal, energiaMediaQAOALocal, energiaMediaOptimaQAOALocal)
    ##    imprimirResultadosExperimento('QAOA Real: ', porcentajeSolucionOptimaQAOAReal, porcentajeSolucionCumpleRestriccionesQAOAReal, energiaMediaQAOAReal, energiaMediaOptimaQAOAReal)
    imprimirResultadosExperimento('Annealer: ', porcentajeSolucionOptimaAnnealer, porcentajeSolucionCumpleRestriccionesAnnealer, energiaMediaAnnealer, energiaMediaOptimaAnnealer)

num_reads_annealer = 100
shots = 1024
reps = 4

experimento1(5,10,3)