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
    MinimumEigenOptimizer
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit_optimization.runtime import QAOAClient
from dwave.system import DWaveSampler
from dwave.system import EmbeddingComposite
from qiskit import IBMQ
from qiskit.providers.ibmq import least_busy
from qiskit_optimization.runtime import QAOAClient


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
        conexionesSeleccionadas = random.sample(conexiones, numInstancias - 1)
        conexionesSeleccionadas.extend(camino)

        # Crear el diccionario de la instancia
        instancia = {
            'numeroVertices': numeroVertices,
            'conexiones': conexionesSeleccionadas
        }

        instancias.append(instancia)

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



def crearArchivoTxt(nombreArchivo, problema, nNodos, metodo, vectorSolOptima, cumpleRestricciones, vectorEnergiaSolObtenida, energiaSolOptima, tiempo):

    n = 0

    with open(nombreArchivo, 'a') as archivo:
        for sol in vectorSolOptima:
            aEscribir = str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(sol) + "," + str(cumpleRestricciones) + "," + str(vectorEnergiaSolObtenida[n]) + "," + str(energiaSolOptima) + "," + str(tiempo) + "\n"
            archivo.write(str(aEscribir))
            n+=1

def limpiarArchivosExperimentos(archivo1, archivo2, archivo3):

    # Limpiar archivos en los que se van a exportar los datos
    with open(archivo1, 'w') as archivo:  # TODO mover esta parte a util con 3 argumentos
        archivo.write("")

    with open(archivo2, 'w') as archivo:
        archivo.write("")

    with open(archivo3, 'w') as archivo:
        archivo.write("")

def escribirDatosGrafo(problema, nNodos, metodo, porcentajeSolOptima, porcentajeSolValida, energia):

    with open("ultimosDatosGrafos.txt", 'a') as archivo:
        archivo.write(str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(porcentajeSolOptima) + "," + str(porcentajeSolValida) + "," + str(energia) + "\n")

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

    # Establecer las seeds
    seed = 277653
    np.random.seed(277653)

    quantum_instance = QuantumInstance(Aer.get_backend('aer_simulator'), shots=shots, seed_simulator=seed, seed_transpiler=seed)
    qaoa = QAOA(optimizer = COBYLA(), quantum_instance=quantum_instance , reps = reps) # , initial_point=np.random.uniform(0, 2*np.pi, 2*reps)
    qaoa_optimizer = MinimumEigenOptimizer(qaoa)
    inicio = time.time()
    result = qaoa_optimizer.solve(qp)
    start = time.time()
    tiempoCalculo = (int((start - inicio)*1000))/shots

    datosResultados = {}

    valorMinimo = float('inf')
    index = 0
    for x in result.samples:

        datosResultados[index] = [round((x.probability) * shots), x.fval]
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
    sampler = EmbeddingComposite(DWaveSampler())
    result = sampler.sample(bqm_binary, num_reads=num_reads)

    return result

def metodoExactoAnnealer(bqm_binary):

    sampler = dimod.ExactSolver()
    result = sampler.sample(bqm_binary)

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

def obtenerEstadisticasAnnealer(result, optimalResult, nNodos, cumpleRestricciones, num_reads_annealer, nombreArchivo, nombreProblema):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy
    solucion_obtenida = result.first.energy

    comparativaSoluciones = {}
    array_sol_optima = []
    n = 0

    porcentajeSolOptima = 0

    for res in result.data_vectors['energy']:
        comparativaSoluciones[res] = solucion_optima == res
        for i in range(0, result.data_vectors['num_occurrences'][n]):
            array_sol_optima.append(comparativaSoluciones[res])
            if comparativaSoluciones[res]:
                porcentajeSolOptima += 1
        n += 1

    porcentajeSolOptima /= float(num_reads_annealer)

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestricciones

    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    n = 0

    energia = 0

    for res in result.data_vectors['energy']:
        for i in range(0, result.data_vectors['num_occurrences'][n]):
            array_sol_obtenida.append(str(res))
            energia += res
        n += 1

    energia /= float(num_reads_annealer)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = solucion_optima

    # Crear un array con los valores
    resultados = [solucion_optima==solucion_obtenida, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    crearArchivoTxt(nombreArchivo, nombreProblema, nNodos, "Annealer", array_sol_optima, True, array_sol_obtenida, optimalResult.first.energy, 0)

    escribirDatosGrafo(nombreProblema, nNodos, "Annealer", porcentajeSolOptima, "100", energia) # TODO ese porcentajeSolValida...

    # Devolver el array de resultados
    return resultados

def obtenerEstadisticasQAOA(result, optimalResult, datosResultados, nNodos, tiempoQAOA, cumpleRestricciones, reps, nombreArchivo, nombreProblema):

    # Verificar si se ha obtenido la solución óptima
    solucion_optima = optimalResult.first.energy == result ## Comparar con el resultado optimo

    comparativaSoluciones = {}
    array_sol_optima = []

    porcentajeSolOptima = 0

    n = 0

    for solucion in datosResultados:
        comparativaSoluciones[solucion] = datosResultados[solucion][1] == optimalResult.first.energy
        for i in range(0, datosResultados[solucion][0]):
            array_sol_optima.append(comparativaSoluciones[solucion])
            n += 1
            if(comparativaSoluciones[solucion]):
                porcentajeSolOptima += 1

    porcentajeSolOptima /= n

    # Verificar si la solución cumple las restricciones
    cumple_restricciones = cumpleRestricciones


    # Obtener la energía de la solución obtenida
    energia_solucion_obtenida = 0
    array_sol_obtenida = []

    energia = 0

    for solucion in datosResultados:
        for i in range(0, datosResultados[solucion][0]):
            array_sol_obtenida.append(datosResultados[solucion][1])
            energia_solucion_obtenida += datosResultados[solucion][1]
            energia += datosResultados[solucion][1]

    energia /= n

    energia_solucion_obtenida /= len(datosResultados)

    # Obtener la energía de la solución óptima
    energia_solucion_optima = optimalResult.first.energy

    # Crear un array con los valores
    resultados = [solucion_optima, cumple_restricciones, energia_solucion_obtenida, energia_solucion_optima]

    # Crear archivo .txt con datos
    metodo = "Simulación QAOA (reps=" +  str(reps) + ")"
    crearArchivoTxt(nombreArchivo, nombreProblema, nNodos, metodo, array_sol_optima, True, array_sol_obtenida, optimalResult.first.energy, tiempoQAOA)

    escribirDatosGrafo(nombreProblema, nNodos, metodo, porcentajeSolOptima, "100", round(energia,2)) # TODO ese porcentajeSolValida

    # Devolver el array de resultados
    return resultados

# generarGrafosAleatoriosMaxCut() # Descomentar para generar grafos
# generarGrafosAleatoriosTSP()

# # Ejemplo de uso
# instancias = leerInstancias("grafosMaxCut.txt")
# for instancia in instancias:
#     print(instancia)