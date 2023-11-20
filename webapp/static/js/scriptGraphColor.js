var resultDiv = document.getElementById("cajaResultado");

numeroNodos = 0
numeroColores = 0
numeroRep = 0
arrayConexiones = []
metodo = ""

$(document).ready(function() {
    $("#comoResolver").click(function() {

        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

function ejecutarScriptPython() {

    document.getElementById("error_datosIncompletos_GraphColor").style.display = "none";

    if(arrayConexiones.length > 0) {
        arrayConexionesString = "";

        for (var i = 0; i < arrayConexiones.length - 1; i++) {
            arrayConexionesString += arrayConexiones[i] + ",";
        }

        arrayConexionesString += arrayConexiones[arrayConexiones.length - 1];
        arrayConexionesString = arrayConexionesString.trim();
    }

    if(numeroNodos > 0 && numeroColores > 0 && numeroRep > 0 && arrayConexionesString.length > 0) {

        resultDiv.appendChild(limpiarResultado());

        var parametros = {
            "numeroNodos": numeroNodos + "",
            "numeroColores": numeroColores + "",
            "numeroRep": numeroRep + "",
            "conexiones": arrayConexionesString,
            "metodo": metodo
        }

        $.ajax({
            type: "POST",
            url: "executeGraphColor",
            data: JSON.stringify(parametros),
            contentType: 'application/json',
            success: function (response) {
                var {
                    variablesP,
                    resultadoP,
                    valorFinalP
                } = obtenerResultados(response);

                resultDiv.appendChild(variablesP);
                resultDiv.appendChild(resultadoP);
                resultDiv.appendChild(valorFinalP);
            },
            error: function (xhr, status, error) {
                limpiarResultado()

                var errorP = document.createElement("p");
                errorP.textContent = "Se ha producido un error, por favor, revise los parámetros del problema";

                resultDiv.appendChild(errorP);
            }
        });

    } else {
        document.getElementById("error_datosIncompletos_GraphColor").style.display = "block";
    }

}

function seleccionarNumeroNodosGraphColor(){
    numeroNodos = document.getElementById("numeroNodosGraphColor").value;

    limpiarNumNodosGraphColor();
}

function limpiarNumNodosGraphColor(){
    document.getElementById("numeroNodosGraphColor").value = "";

    actualizarDatosProblema();
}

function seleccionarNumeroColores(){
    numeroColores = document.getElementById("numeroColores").value;

    limpiarNumColores();
}

function limpiarNumColores(){
    document.getElementById("numeroColores").value = "";

    actualizarDatosProblema();
}

function seleccionarNumeroRepsGraphColor(){
    numeroRep = document.getElementById("numeroRepGraphColor").value;

    limpiarNumRepsGraphColor();
}

function limpiarNumRepsGraphColor(){
    document.getElementById("numeroRepGraphColor").value = "";

    actualizarDatosProblema();
}

function agregarConexionGraphColor(){

    document.getElementById("error_componente_conexion").style.display = "none";

    // Obtener los valores de los campos de texto
    var nodo1 = document.getElementById("conexionNodo1").value;
    var nodo2 = document.getElementById("conexionNodo2").value;

    // Validar que se hayan ingresado ambos nodos
    if (nodo1 && nodo2) {

        // Crear la conexión en formato (a,b)
        var conexion = "(" + nodo1 + "," + nodo2 + ")";

        // Apilar la conexión en el array
        arrayConexiones.push(conexion);

        limpiarConexionesGraphColor();
    } else {
        document.getElementById("error_componente_conexion").style.display = "block";
    }
}

function limpiarConexionesGraphColor(){

    // Limpiar los campos de texto
    document.getElementById("conexionNodo1").value = "";
    document.getElementById("conexionNodo2").value = "";

    actualizarDatosProblema()
}

function actualizarDatosProblema(){

    limpiarErrores();
    limpiarResultado();

    var txtNumVertices = document.getElementById("txtNumVerticesGraphColor");
    var txtNumColores = document.getElementById("txtNumColoresGraphColor");
    var txtNumRep = document.getElementById("txtNumRepGraphColor");
    var txtConexiones = document.getElementById("txtConexGraphColor");

    txtNumVertices.textContent = numeroNodos;
    txtNumColores.textContent = numeroColores;
    txtNumRep.textContent = numeroRep;
    txtConexiones.textContent = arrayConexiones;
}

function cargarArchivoProblema(){
    var archivoInput = document.getElementById('archivoTexto');
    var archivo = archivoInput.files[0];
    var lector = new FileReader();

    lector.onload = function(e) {
        var contenido = e.target.result;
        procesarArchivoProblema(contenido);
    };

    lector.readAsText(archivo);
}

function procesarArchivoProblema(archivoTexto) {
    var lineas = archivoTexto.split("\n");

    pesoMaximo = parseInt(lineas[0]);

    var valoresString = lineas[1].split(",");
    arrayValores = valoresString.map(function(valor) {
        return parseInt(valor);
    });

    var pesosString = lineas[2].split(",");
    arrayPesos = pesosString.map(function(peso) {
        return parseInt(peso);
    });

    // Actualizar los datos del problema
    actualizarDatosProblema();
}

function cargarArchivoProblema(){
    var archivoInput = document.getElementById('archivoTexto');
    var archivo = archivoInput.files[0];
    var lector = new FileReader();

    lector.onload = function(e) {
        var contenido = e.target.result;
        procesarArchivoProblema(contenido);
    };

    lector.readAsText(archivo);
}

function procesarArchivoProblema(contenido){
    var lineas = contenido.split("\n");

    numeroNodos = parseInt(lineas[0]);
    numeroColores = parseInt(lineas[1]);
    numeroRep = parseInt(lineas[2]);

    // Dividir la cadena de conexiones por el delimitador ";"
    var conexionesSeparadas = lineas[3].split(";");

    // Convertir cada conexión en una tupla de números y agregarla a arrayConexiones
    arrayConexiones = [];
    for (var i = 0; i < conexionesSeparadas.length; i++) {
        var conexion = conexionesSeparadas[i];
        var nodos = conexion.split(",");
        var nodo1 = parseInt(nodos[0]);
        var nodo2 = parseInt(nodos[1]);
        arrayConexiones.push("(" + nodo1 + "," + nodo2 + ")");
    }

    // Actualizar los datos del problema
    actualizarDatosProblema();
}


function limpiarResultado() {

    // Limpiar el div de resultados
    var elementosP = resultDiv.getElementsByTagName("p");
    while (elementosP.length > 0) {
        resultDiv.removeChild(elementosP[0]);
    }

    var txtResolviendo = document.createElement("p");
    txtResolviendo.textContent = "Resolviendo...";
    return txtResolviendo;
}

function limpiarErrores(){
    document.getElementById("error_componente_conexion").style.display = "none";
    document.getElementById("error_datosIncompletos_GraphColor").style.display = "none";
}

function obtenerResultados(response) {
    // Quitar mensaje temporal resolviendo
    var elementosP = resultDiv.getElementsByTagName("p");
    while (elementosP.length > 0) {
        resultDiv.removeChild(elementosP[0]);
    }

    var info = response.split('/'); // Procesamos el output del programa .py
    var variables = info[0].split(';'); // Dividir las variables
    var resultado = info[1]; // Obtener el resultado
    var valorFinal = info[2]; // Obtener el valor final
    var variablesArray = []; // Array para guardar las variables y sus valores

    for (var i = 0; i < variables.length - 1; i++) {
        var variable = variables[i].split(',');
        var nombre = variable[0];
        var valor = variable[1];
        variablesArray.push(nombre + ": " + valor);
    }

    var variablesP = document.createElement("p");
    variablesP.textContent = "Valores de las variables: " + variablesArray.join(", ");
    var resultadoP = document.createElement("p");
    resultadoP.textContent = "Resultado ejecución: " + resultado;
    var valorFinalP = document.createElement("p");
    valorFinalP.textContent = "Valor de la función objetivo: " + valorFinal;
    return {variablesP, resultadoP, valorFinalP};
}

function borrarConexionesGraphColor(){

    arrayConexiones = [];
    arrayConexionesString = "";

    actualizarDatosProblema()
}

function  borrarNumeroNodosGraphColor(){

    numeroNodos = 0;
    actualizarDatosProblema()
}

function borrarNumeroColores(){

    numeroColores = 0;
    actualizarDatosProblema()
}

function borrarNumeroRepsGraphColor(){

    numeroRep = 0;
    actualizarDatosProblema()
}
