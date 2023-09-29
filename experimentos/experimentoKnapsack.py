from util import *
from docplex.mp.model import Model

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

reps = 1
shots = 1024
num_reads = 100

experimento1(3, 5, 1, 20)