from util import *
from docplex.mp.model import Model

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

def cumpleRestriccionesTSPAnnealer(result): # TODO

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

def experimento1(numGrafosMin, numGrafosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA_TSP.txt", "ultimosDatosAnnealer_TSP.txt", "ultimosDatosGrafos_TSP.txt")

    # Obtener grafos
    datosGrafos = {}
    n = 0
    grafos = []
    grafos.extend(leerInstanciasTSP("grafosTSP.txt", numGrafosMin, numGrafosMax))

    # Procesar grafos
    for grafo in grafos:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroVertices'], grafo['conexiones'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, reps)
        ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], True, num_reads_annealer, "ultimosDatosAnnealer_TSP.txt", "TSP")
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, True, reps, "ultimosDatosSimulacionQAOA_TSP.txt", "TSP")
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

num_reads_annealer = 1 # 100
reps = 2 # 1,2,3,4
shots = 1024 # 1024

experimento1(5, 5)
print("acabe")