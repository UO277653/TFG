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



def experimento1(numGrafosMin, numGrafosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA.txt", "ultimosDatosAnnealer.txt", "ultimosDatosGrafos.txt")

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
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], num_reads_annealer, "ultimosDatosAnnealer.txt", "TSP")
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, reps, "ultimosDatosSimulacionQAOA.txt", "TSP", shots)
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

# Ahorra gasto de DWave, no hace llamada para cada rep
def experimento2(numGrafosMin, numGrafosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA.txt", "ultimosDatosAnnealer.txt", "ultimosDatosGrafos.txt")

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
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], num_reads_annealer, "ultimosDatosAnnealer.txt", "TSP")

        for rep in range (1, reps+1):
            #resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, rep)
            resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorRemoto(qp, shots, rep)
        ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])

            #estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, rep, "ultimosDatosSimulacionQAOA.txt", "TSP", shots)
            estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, rep, "ultimosDatosSimulacionQAOA.txt", "TSP", shots, remoto=True)
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
reps = 1 # 1,2,3,4
shots = 1024 # 1024

experimento2(3, 3)