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

def experimento1(numObjetosMin, numObjetosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA.txt", "ultimosDatosAnnealer.txt", "ultimosDatosGrafos.txt")

    # Obtener grafos
    datosGrafos = {}
    n = 0
    grafos = []
    grafos.extend(leerInstanciasKnapsack("grafosKnapsack.txt", numObjetosMin, numObjetosMax))

    # Procesar grafos
    for grafo in grafos:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['valores'], grafo['pesos'], grafo['pesoMaximo'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, reps)
        ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], True, num_reads_annealer, "ultimosDatosAnnealer.txt", "Knapsack")
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, True, reps, "ultimosDatosSimulacionQAOA.txt", "Knapsack")
        ## estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultQAOAOptimal)

        datosGrafos[grafo['numeroVertices'], n] = {
            'estadisticasQAOALocal': estadisticasQAOALocal,
            'estadisticasAnnealer': estadisticasAnnealer
        }

        print(n)

        n += 1

    print("")

    for dato in datosGrafos:
        print(dato, " QAOA Local: ", datosGrafos[dato]['estadisticasQAOALocal'], " Annealer:", datosGrafos[dato]['estadisticasAnnealer'])

    print("")

def experimento2(numGrafosMin, numGrafosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA.txt", "ultimosDatosAnnealer.txt", "ultimosDatosGrafos.txt")

    # Obtener grafos
    datosGrafos = {}
    n = 0
    grafos = []
    grafos.extend(leerInstanciasKnapsack("grafosKnapsack.txt", numGrafosMin, numGrafosMax))

    # Procesar grafos
    for grafo in grafos:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['valores'], grafo['pesos'], grafo['pesoMaximo'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], num_reads_annealer, "ultimosDatosAnnealer.txt", "Knapsack", grafo['pesos'], grafo['pesoMaximo'])

        for rep in range (1, reps+1):
            resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, rep)
            ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])

            estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, rep, "ultimosDatosSimulacionQAOA.txt", "Knapsack", shots)
            ## estadisticasQAOAReal = obtenerEstadisticasQAOA(resultQAOAReal, resultQAOAOptimal)

        datosGrafos[grafo['numeroVertices'], n] = {
            'estadisticasQAOALocal': estadisticasQAOALocal,
            'estadisticasAnnealer': estadisticasAnnealer
        }

        print(n)

        n += 1


    print("")

    for dato in datosGrafos:
        print(dato, " QAOA Local: ", datosGrafos[dato]['estadisticasQAOALocal'], " Annealer:", datosGrafos[dato]['estadisticasAnnealer'])

    print("")

num_reads_annealer = 1
reps = 4
shots = 1024

experimento2(3, 5)