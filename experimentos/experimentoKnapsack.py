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

def experimento1(numObjetosMin, numObjetosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA_Knapsack.txt", "ultimosDatosAnnealer_Knapsack.txt", "ultimosDatosGrafos_Knapsack.txt")

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
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], True, num_reads_annealer, "ultimosDatosAnnealer_Knapsack.txt", "Knapsack")
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, True, reps, "ultimosDatosSimulacionQAOA_Knapsack.txt", "Knapsack")
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

reps = 1
shots = 100
num_reads_annealer = 1

experimento1(3, 3)