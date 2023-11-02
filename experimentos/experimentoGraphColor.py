from util import *
from docplex.mp.model import Model

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



def experimento1(numGrafosMin, numGrafosMax):

    limpiarArchivosExperimentos("ultimosDatosSimulacionQAOA.txt", "ultimosDatosAnnealer.txt", "ultimosDatosGrafos.txt")

    # Obtener grafos
    datosGrafos = {}
    n = 0
    grafos = []
    grafos.extend(leerInstanciasGraphColor("grafosGraphColor.txt", numGrafosMin, numGrafosMax))

    # Procesar grafos
    for grafo in grafos:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroVertices'], grafo['numeroColores'], grafo['conexiones'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, reps)
        ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], True, num_reads_annealer, "ultimosDatosAnnealer.txt", "GraphColor")
        estadisticasQAOALocal = obtenerEstadisticasQAOA(resultQAOALocal, resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, True, reps, "ultimosDatosSimulacionQAOA.txt", "GraphColor")
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
    grafos.extend(leerInstanciasGraphColor("grafosGraphColor.txt", numGrafosMin, numGrafosMax))

    # Procesar grafos
    for grafo in grafos:

        # Formular el problema
        mdl = formularProblemaDocplex(grafo['numeroVertices'], grafo['numeroColores'], grafo['conexiones'])
        qp = formularProblemaQiskit(mdl)
        bqm_binary = formularProblemaDwave(qp)

        # Resolver el problema
        resultAnnealer = metodoAnnealer(bqm_binary, num_reads_annealer)
        resultAnnealerOptimal = metodoExactoAnnealer(bqm_binary)

        # Obtener estadísticas
        estadisticasAnnealer = obtenerEstadisticasAnnealer(resultAnnealer, resultAnnealerOptimal, grafo['numeroVertices'], num_reads_annealer, "ultimosDatosAnnealer.txt", "GraphColor", conexiones=grafo['conexiones'], numeroColores=grafo['numeroColores'])

        for rep in range (1, reps+1):
            #resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorLocal(qp, shots, rep)
            resultQAOALocal, datosResultadosQAOA, tiempoQAOA = metodoSimuladorRemoto(qp, shots, rep)
        ## resultQAOAReal = metodoSimuladorReal(qp,reps, grafo['numeroVertices'])

            #estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, rep, "ultimosDatosSimulacionQAOA.txt", "GraphColor", shots)
            estadisticasQAOALocal = obtenerEstadisticasQAOA(resultAnnealerOptimal, datosResultadosQAOA, grafo['numeroVertices'], tiempoQAOA, rep, "ultimosDatosSimulacionQAOA.txt", "GraphColor", shots, remoto=True)
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