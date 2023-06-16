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


def formularProblemaDocplex(valores, pesos, max_weight):

    ##
    ## DATOS DEL PROBLEMA
    ##

    # Define the object values, weights, and maximum weight
    values = [int(x) for x in valores]
    weights = [int(x) for x in pesos]
    max_weight = int(max_weight)
    num_objects = len(values)

    # Create the model
    mdl = Model(name='Knapsack')

    # Define the decision variables
    x = mdl.binary_var_list(num_objects)

    # Define the objective function
    objective = mdl.sum(-values[j] * x[j] for j in range(num_objects))
    mdl.minimize(objective)

    # Add the constraint for the maximum weight
    mdl.add_constraint(mdl.sum(weights[j] * x[j] for j in range(num_objects)) <= max_weight)

    # Solve the model
    mdl.solve()

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

    # Utilizar ordenador real
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
        instancias = generarGrafoAleatorioKnapsack(num_vertices, numInstancias, pesoMaximo)
        grafosAleatorios.extend(instancias)

    print(len(grafosAleatorios))

    for grafo in grafosAleatorios:

        print(f"Valores: ", grafo['valores'], "\nPesos: ", grafo['pesos'], "\nPeso máximo: ", grafo['pesoMaximo'])
        # Formular el problema
        mdl = formularProblemaDocplex(grafo['valores'], grafo['pesos'], grafo['pesoMaximo'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal = metodoSimuladorLocal(qp, shots, reps)
        # resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal)
        # estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultAnnealerOptimal)
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['pesos'], grafo['pesoMaximo'])

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

def generarGrafoAleatorioKnapsack(numeroVertices, numInstancias, pesoMaximoConexion):
    instancias = []

    for _ in range(numInstancias):
        # Generar todas las posibles conexiones entre los vértices
        valores = [(random.randint(1,pesoMaximoConexion)) for i in range(numeroVertices)]
        pesos = [(random.randint(1,pesoMaximoConexion)) for i in range(numeroVertices)]
        pesoMaximo = pesoMaximoConexion

        # Crear el diccionario de la instancia
        instancia = {
            'valores': valores,
            'pesos': pesos,
            'pesoMaximo': pesoMaximo
        }

        instancias.append(instancia)

    return instancias

def cumpleRestriccionesKnapsackAnnealer(result, pesos, pesoMaximo):

    nodos = len(pesos)

    # Restricción: no se puede superar el peso máximo
    for nodo in range(nodos):
        sum = 0
        if(result.first[0][nodo] == 1):
            sum += pesos[nodo]

    if(sum > pesoMaximo):
        return False

    return True

def obtenerEstadisticasAnnealer(result, optimalResult, pesos, pesoMaximo):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    print("\nAnnealer: ¿Se ha obtenido la solución óptima?", solucion_optima==solucion_obtenida)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestriccionesKnapsackAnnealer(result, pesos, pesoMaximo)
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