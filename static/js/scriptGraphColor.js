var resultDiv = document.getElementById("cajaResultado");

numeroNodos = 0
numeroColores = 0
numeroRep = 0
arrayConexiones = []
metodo = ""

$(document).ready(function() {
    $("#comoResolver").click(function() {
        resultDiv.innerHTML = "";
        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

function ejecutarScriptPython() {

    if(arrayConexiones.length > 0) {
        arrayConexionesString = "";

        for (var i = 0; i < arrayConexiones.length - 1; i++) {
            arrayConexionesString += arrayConexiones[i] + ",";
        }

        arrayConexionesString += arrayConexiones[arrayConexiones.length - 1];
        arrayConexionesString = arrayConexionesString.trim();
    }

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
        success: function(response) {
            console.log(response);
            resultDiv.appendChild(document.createTextNode(response));
        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });

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
    }
}

function limpiarConexionesGraphColor(){

    // Limpiar los campos de texto
    document.getElementById("conexionNodo1").value = "";
    document.getElementById("conexionNodo2").value = "";

    actualizarDatosProblema()
}

function actualizarDatosProblema(){

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
        arrayConexiones.push("(" + nodo1 + "," + nodo2 + ") ");
    }

    // Actualizar los datos del problema
    actualizarDatosProblema();
}

