import random
import time
import dimod
import numpy as np
from qiskit.utils import QuantumInstance
from qiskit_optimization.translators import \
    from_docplex_mp
from qiskit_optimization.converters import \
    QuadraticProgramToQubo
from qiskit_aer import Aer
from qiskit.algorithms import QAOA
from qiskit.algorithms.optimizers import COBYLA
from qiskit_optimization.algorithms import \
    MinimumEigenOptimizer, \
    OptimizationResultStatus
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit_optimization.runtime import QAOAClient
from dwave.system import DWaveSampler
from dwave.system import EmbeddingComposite
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit_optimization.runtime import QAOAClient


##
#
# GENERACION DE GRAFOS
#
##
def generarGrafosAleatoriosMaxCut():

    vertices = [5,6,7,8,9,10,11,12,13,14,15]

    for vertice in vertices:

        numeroVertices = vertice
        numInstancias = 20
        nombreArchivo = "grafosMaxCut.txt"

        instancias = []

        for i in range(numInstancias):
            # Generar todas las posibles conexiones entre los vértices
            conexiones = [(i, j) for i in range(numeroVertices) for j in range(i + 1, numeroVertices)]

            # Seleccionar aleatoriamente un subconjunto de conexiones
            numConexiones = random.randint(int(len(conexiones)/2), int(len(conexiones)*0.8))
            conexionesSeleccionadas = random.sample(conexiones, numConexiones)

            # Crear el diccionario de la instancia
            instancia = {
                'numeroVertices': numeroVertices,
                'conexiones': conexionesSeleccionadas
            }

            instancias.append(instancia)

        # Escribir las instancias en un archivo de texto
        with open(nombreArchivo, 'a') as archivo:
            for instancia in instancias:
                archivo.write(f"{instancia['numeroVertices']}-")
                for conexion in instancia['conexiones']:
                    archivo.write(f"{conexion[0]},{conexion[1]};")
                archivo.write("\n")

        print(f"Se han generado y guardado las instancias en el archivo {nombreArchivo}")

def generarGrafosAleatoriosTSP():

    vertices = [5,6,7,8,9,10,11,12,13,14,15]

    for vertice in vertices:

        numeroVertices = vertice
        numInstancias = 1 # 20
        nombreArchivo = "grafosTSP.txt"
        pesoMaximo = vertice

        instancias = []

        for i in range(numInstancias):

            conexiones = []

            for i in range(numeroVertices):
                for j in range(i+1, numeroVertices):
                    peso = random.randint(1, pesoMaximo)
                    conexiones.append((i,j,peso))

            # Seleccionar aleatoriamente un subconjunto de conexiones
            numConexiones = random.randint(int(len(conexiones)/2), int(len(conexiones)*0.8))
            conexionesSeleccionadas = random.sample(conexiones, numConexiones)

            # Crear el diccionario de la instancia
            instancia = {
                'numeroVertices': numeroVertices,
                'conexiones': conexionesSeleccionadas
            }

            instancias.append(instancia)

        # Escribir las instancias en un archivo de texto
        with open(nombreArchivo, 'a') as archivo:
            for instancia in instancias:
                archivo.write(f"{instancia['numeroVertices']}-")
                for conexion in instancia['conexiones']:
                    archivo.write(f"{conexion[0]},{conexion[1]},{conexion[2]};")
                archivo.write("\n")

        print(f"Se han generado y guardado las instancias en el archivo {nombreArchivo}")

# TIENE AL MENOS UN CAMINO POSIBLE PASANDO POR TODOS LOS NODOS
# Podria cambiarlo para que genere muchos y los guarde en un archivo .txt para conservarlos
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
        numConexiones = random.randint(int(len(conexiones)/2), int(len(conexiones)*0.8))
        conexionesSeleccionadas = random.sample(conexiones, numConexiones)
        conexionesSeleccionadas.extend(camino)

        # Crear el diccionario de la instancia
        instancia = {
            'numeroVertices': numeroVertices,
            'conexiones': conexionesSeleccionadas
        }

        instancias.append(instancia)

    # Escribir las instancias en un archivo de texto
    with open("grafosTSP.txt", 'a') as archivo:
        for instancia in instancias:
            archivo.write(f"{instancia['numeroVertices']}-")
            for conexion in instancia['conexiones']:
                archivo.write(f"{conexion[0]},{conexion[1]},{conexion[2]};")
            archivo.write("\n")

    print("Se han generado y guardado las instancias en el archivo grafosTSP.txt")

    return instancias

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

def generarGrafoAleatorioGraphColor(numeroVertices, numInstancias):
    instancias = []

    with open("grafosGraphColor.txt", 'a') as archivo:

        for i in range(numInstancias):

            numeroNodos = numeroVertices
            numeroColores = random.randint(2,numeroNodos)
            edges = []

            # Generar conexiones aleatorias
            for i in range(numeroNodos):
                for j in range(i + 1, numeroNodos):
                    if random.random() < 0.7:
                        if((i,j) and (j,i) not in edges):
                            edges.append((i,j))
                            edges.append((j,i))

            # Crear el diccionario de la instancia
            instancia = {
                'numeroNodos': numeroNodos,
                'numeroColores': numeroColores,
                'edges': edges
            }

            aEscribir = str(instancia['numeroNodos']) + "-" + str(instancia['numeroColores']) + "-"

            for edge in edges:
                aEscribir += str(edge[0]) + "," + str(edge[1]) + ";"

            archivo.write(str(aEscribir + "\n"))

            instancias.append(instancia)

    return instancias

##
#
# LEER INSTANCIAS
#
##
def leerInstancias(nombreArchivo):
    instancias = []

    with open(nombreArchivo, 'r') as archivo:
        lineas = archivo.readlines()

        for linea in lineas:
            numeroVertices, conexiones = linea.strip().split('-')
            numeroVertices = int(numeroVertices)

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

def leerInstanciasTSP(nombreArchivo, numGrafosMin, numGrafosMax):
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
                num1, num2, weight = con.split(',')
                instancia['conexiones'].append((int(num1), int(num2), int(weight)))

            instancias.append(instancia)

    return instancias

def leerInstanciasKnapsack(nombreArchivo, numObjetosMin, numObjetosMax):
    instancias = []

    with open(nombreArchivo, 'r') as archivo:
        lineas = archivo.readlines()

        for linea in lineas:
            numeroVertices, valores, pesos, pesoMaximo = linea.strip().split(';')
            numeroVertices = int(numeroVertices)

            if(numeroVertices < numObjetosMin or numeroVertices > numObjetosMax):
                continue

            # Crear el diccionario de la instancia
            instancia = {
                'numeroVertices': numeroVertices,
                'valores': [],
                'pesos': [],
                'pesoMaximo': int(pesoMaximo)
            }

            valores = valores.split(',')

            for val in valores:
                instancia['valores'].append(int(val))

            pesos = pesos.split(',')

            for peso in pesos:
                instancia['pesos'].append(int(peso))

            instancias.append(instancia)

    return instancias

def leerInstanciasGraphColor(nombreArchivo, numGrafosMin, numGrafosMax):
    instancias = []

    with open(nombreArchivo, 'r') as archivo:
        lineas = archivo.readlines()

        for linea in lineas:
            numeroVertices, numeroColores, conexiones = linea.strip().split('-')
            numeroVertices = int(numeroVertices)

            if(numeroVertices < numGrafosMin or numeroVertices > numGrafosMax):
                continue

            # Crear el diccionario de la instancia
            instancia = {
                'numeroVertices': numeroVertices,
                'numeroColores': int(numeroColores),
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

##
#
# GESTION DE ARCHIVOS
#
##
def crearArchivoTxt(nombreArchivo, problema, nNodos, metodo, vectorSolOptima, cumpleRestricciones, vectorEnergiaSolObtenida, energiaSolOptima, tiempo):

    n = 0

    with open(nombreArchivo, 'a') as archivo:
        for sol in vectorSolOptima:
            aEscribir = str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(sol) + "," + str(cumpleRestricciones[n]) + "," + str(vectorEnergiaSolObtenida[n]) + "," + str(energiaSolOptima) + "," + str(tiempo) + "\n"
            archivo.write(str(aEscribir))
            n+=1

def limpiarArchivosExperimentos(archivo1, archivo2, archivo3):

    # Limpiar archivos en los que se van a exportar los datos
    with open(archivo1, 'w') as archivo:
        archivo.write("")

    with open(archivo2, 'w') as archivo:
        archivo.write("")

    with open(archivo3, 'w') as archivo:
        archivo.write("")

def escribirDatosGrafo(problema, nNodos, metodo, porcentajeSolOptima, porcentajeSolValida, energia):

    with open("ultimosDatosGrafos.txt", 'a') as archivo:
        archivo.write(str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(porcentajeSolOptima) + "," + str(porcentajeSolValida) + "," + str(energia) + "\n")


##
#
# FORMULACIONES
#
##
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

##
#
# METODOS DE RESOLUCION
#
##
def metodoSimuladorLocal(qp, shots, reps):

    # Establecer las seeds
    seed = 277653
    np.random.seed(277653)

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=shots, seed_simulator=seed, seed_transpiler=seed)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = reps, initial_point=np.random.uniform(0, 2*np.pi, 2*reps))
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    inicio = time.time()
    result = qaoa_optimizer.solve(qp)
    start = time.time()
    tiempoCalculo = (int((start - inicio)*1000))/shots

    datosResultados = {}

    valorMinimo = float('inf')
    index = 0
    for x in result.samples:

        datosResultados[index] = [round((x.probability) * shots), x.fval, x.x, x.status]
        index += 1

        if(valorMinimo > x.fval):
            valorMinimo = x.fval

    return valorMinimo, datosResultados, tiempoCalculo

def metodoSimuladorRemoto(qp, shots, reps):

    # Establecer las seeds
    seed = 277653
    np.random.seed(277653)

    provider = IBMQ.load_account()
    quantum_instance = QuantumInstance(provider.get_backend('ibmq_qasm_simulator'), shots=shots, seed_simulator=seed, seed_transpiler=seed)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = reps, initial_point=np.random.uniform(0, 2*np.pi, 2*reps))
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    inicio = time.time()
    result = qaoa_optimizer.solve(qp)
    start = time.time()
    tiempoCalculo = (int((start - inicio)*1000))/shots

    datosResultados = {}

    valorMinimo = float('inf')
    index = 0
    for x in result.samples:

        datosResultados[index] = [round((x.probability) * shots), x.fval, x.x, x.status]
        index += 1

        if(valorMinimo > x.fval):
            valorMinimo = x.fval

    return valorMinimo, datosResultados, tiempoCalculo

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
    sampler = EmbeddingComposite(DWaveSampler(seed=277653))
    result = sampler.sample(bqm_binary, num_reads=num_reads)

    return result

def metodoExactoAnnealer(bqm_binary):

    sampler = dimod.ExactSolver()
    result = sampler.sample(bqm_binary)

    return result

##
#
# ESTADISTICAS Y RESULTADOS EXPERIMENTOS
#
##
def cumpleRestriccionesTSPAnnealer(result):

    n_nodos = int(len(result)**(1/2))

    # Restricción 1: cada vértice se visita solamente una vez
    for parts in range(0, len(result)-1, n_nodos):
        sum = 0
        for i in range(parts, parts + n_nodos):
            if result[i] == 1:
                sum+=1
        if sum > 1:
            return False

    # Restricción 2: solo se puede visitar una ciudad a la vez
    for i in range(0, n_nodos):
        sum = 0
        for j in range(0, n_nodos, 1):
            if result[i+(n_nodos*j)] == 1:
                sum += 1
        if sum > 1:
            return False

    return True

def cumpleRestriccionesKnapsackAnnealer(result, pesos, pesoMaximo):

    nodos = len(pesos)
    sum = 0

    # Restricción: no se puede superar el peso máximo
    for nodo in range(nodos):
        if(result[nodo] == 1):
            sum += pesos[nodo]

    if(sum > pesoMaximo):
        return False

    return True

def cumpleRestriccionesGraphColorAnnealer(result, conexiones, numeroColores):

    nodos = int(len(result)/numeroColores)

    colores = {}

    # Restricción 1: cada vértice recibe solamente un color
    for i in range(nodos):
        sum = 0
        for j in range(numeroColores):
            sum += result[j+((numeroColores)*i)]
            if(result[j+((numeroColores)*i)] != 0):
                colores[i] = j
        if sum > 1:
            return False

    # Restricción 2: vértices adyacentes no pueden tener el mismo color
    for i, j in conexiones:
        if(len(colores) < nodos or colores[i] == colores[j]):
            return False

    return True

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

def obtenerEstadisticasAnnealer(result, optimalResult, nNodos, num_reads_annealer, nombreArchivo, nombreProblema, pesos = [], pesoMaximo = 0, conexiones = [], numeroColores = 0):

    # Verificar si se ha obtenido la solución óptima
    comparativaSoluciones = {}
    array_sol_optima = []
    porcentajeSolOptima = 0
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    # Para guardar cuantas veces se ha encontrado una solucion valida
    array_sol_valida = []
    porcentajeSolValida = 0

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    n = 0

    for res in result.record:

        comparativaSoluciones[n] = solucion_optima == res['energy']

        for i in range(0, result.data_vectors['num_occurrences'][n]):
            array_sol_optima.append(comparativaSoluciones[n])

            if comparativaSoluciones[n]:
                porcentajeSolOptima += 1

            array_sol_obtenida.append(str(res['energy']))
            energia_solucion_obtenida += float(res['energy'])

            if(nombreProblema == 'TSP'): # TODO que sea automatico, mejorar
                array_sol_valida.append(cumpleRestriccionesTSPAnnealer(res[0]))
                if(cumpleRestriccionesTSPAnnealer(res[0])):
                    porcentajeSolValida += 1
            elif(nombreProblema == 'Knapsack'):
                array_sol_valida.append(cumpleRestriccionesKnapsackAnnealer(res[0], pesos, pesoMaximo))
                if(cumpleRestriccionesKnapsackAnnealer(res[0], pesos, pesoMaximo)):
                    porcentajeSolValida += 1
            elif(nombreProblema == 'GraphColor'):
                array_sol_valida.append(cumpleRestriccionesGraphColorAnnealer(res[0], conexiones, numeroColores))
                if(cumpleRestriccionesGraphColorAnnealer(res[0], conexiones, numeroColores) or comparativaSoluciones[n]):
                    porcentajeSolValida += 1
            else:
                print("Error: problema no valido")

        n += 1

    porcentajeSolOptima /= float(num_reads_annealer)
    porcentajeSolValida /= float(num_reads_annealer)
    energia_solucion_obtenida /= float(num_reads_annealer)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = solucion_optima

    # Crear un array con los valores
    resultados = [solucion_optima==solucion_obtenida, porcentajeSolValida, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    crearArchivoTxt(nombreArchivo, nombreProblema, nNodos, "Annealer", array_sol_optima, array_sol_valida, array_sol_obtenida, optimalResult.first.energy, 0)

    escribirDatosGrafo(nombreProblema, nNodos, "Annealer", porcentajeSolOptima, porcentajeSolValida, round(energia_solucion_obtenida,2))

    # Devolver el array de resultados
    return resultados

def obtenerEstadisticasQAOA(optimalResult, datosResultados, nNodos, tiempoQAOA, reps, nombreArchivo, nombreProblema, shots, remoto = False):

    # Para guardar cuantas veces se ha encontrado la solucion optima
    comparativaSoluciones = {} # Para guardar si una solucion es la optima o no
    array_sol_optima = []
    porcentajeSolOptima = 0
    energia_solucion_optima = optimalResult.first.energy # Obtener la energía de la solución óptima

    # Para guardar cuantas veces se ha encontrado una solucion valida
    array_sol_valida = []
    porcentajeSolValida = 0

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    energias = {}
    energiaMinimaObtenida = float('inf')

    n = 0

    # Para cada solucion obtenida con el QAOA
    for solucion in datosResultados:

        # Comprobar energia minima obtenida comparandola con annealer, para ver si se ha encontrado la optima
        for i in optimalResult.record:

            # Resuelve problema discrepancia Knapsack
            longitudParaAgregar = len(i[0]) - len(datosResultados[solucion][2].tolist())
            aComparar = datosResultados[solucion][2].tolist()

            if(longitudParaAgregar != 0):
                aComparar = datosResultados[solucion][2].tolist() + [0] * longitudParaAgregar

            if (i[0] == aComparar).all(): # Filtrar
                energias[solucion] = i[1]
                if(energiaMinimaObtenida > i[1]):
                    energiaMinimaObtenida = i[1]

        # Comprobar si es una solucion optima
        comparativaSoluciones[solucion] = energias[solucion] == energia_solucion_optima
        for i in range(0, datosResultados[solucion][0]):
            array_sol_optima.append(comparativaSoluciones[solucion])
            n += 1
            if(comparativaSoluciones[solucion]):
                porcentajeSolOptima += 1

            # Comprobar si la solucion cumple las restricciones
            array_sol_valida.append(datosResultados[solucion][3] == OptimizationResultStatus.SUCCESS)
            if(datosResultados[solucion][3] == OptimizationResultStatus.SUCCESS):
                porcentajeSolValida += 1

            # Sumar energias obtenidas
            array_sol_obtenida.append(energias[solucion])
            energia_solucion_obtenida += energias[solucion]

    porcentajeSolOptima /= shots
    porcentajeSolValida /= shots
    energia_solucion_obtenida /= shots

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = energia_solucion_optima == energiaMinimaObtenida

    # Crear un array con los valores
    resultados = [solucion_optima, porcentajeSolValida, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    metodo = "Simulación QAOA (reps=" +  str(reps) + ")" if not remoto else "Simulación QAOA remota (reps=" +  str(reps) + ")"
    crearArchivoTxt(nombreArchivo, nombreProblema, nNodos, metodo, array_sol_optima, array_sol_valida, array_sol_obtenida, energia_solucion_optima, tiempoQAOA)

    escribirDatosGrafo(nombreProblema, nNodos, metodo, porcentajeSolOptima, porcentajeSolValida, round(energia_solucion_obtenida,2))

    # Devolver el array de resultados
    return resultados

# generarGrafosAleatoriosMaxCut() # Descomentar para generar grafos
# generarGrafosAleatoriosTSP()
# generarGrafoAleatorioTSP(5, 5, 10)
# generarGrafoAleatorioGraphColor(4, 10)

# # Ejemplo de uso
# instancias = leerInstancias("grafosMaxCut.txt")
# for instancia in instancias:
#     print(instancia)