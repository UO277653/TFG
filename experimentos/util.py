import random

def generarGrafosAleatoriosMaxCut():

    vertices = [5,6,7,8,9,10,11,12,13,14,15]

    for vertice in vertices:

        numeroVertices = vertice
        numInstancias = 20
        nombreArchivo = "grafosMaxCut.txt"

        instancias = []

        for _ in range(numInstancias):
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

def escribirDatosGrafo(problema, nNodos, metodo, porcentajeSolOptima, porcentajeSolValida, energia):

    with open("ultimosDatosGrafos.txt", 'a') as archivo:
        archivo.write(str(problema) + "," + str(nNodos) + "," + str(metodo) + "," + str(porcentajeSolOptima) + "," + str(porcentajeSolValida) + "," + str(energia) + "\n")

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

# generarGrafosAleatoriosMaxCut() # Descomentar para generar grafos

# # Ejemplo de uso
# instancias = leerInstancias("grafosMaxCut.txt")
# for instancia in instancias:
#     print(instancia)