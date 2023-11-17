var resultDiv = document.getElementById("cajaResultado");

numeroNodos = 0
numeroRep = 0
arrayConexiones = []
arrayConexionesString = ""
metodo = ""

$(document).ready(function() {
    $("#comoResolver").click(function() {
        resultDiv.appendChild(limpiarResultado());
        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

function ejecutarScriptPython() {

    if(arrayConexiones.length > 0) {
        arrayConexionesString = "";

        for (var i = 0; i < arrayConexiones.length - 1; i++) {
            arrayConexionesString += arrayConexiones[i] + ";";
        }

        arrayConexionesString += arrayConexiones[arrayConexiones.length - 1];

        console.log(arrayConexionesString);
    } else {
        console.log(arrayConexionesString);
    }

    var parametros = {
        "nodos": numeroNodos,
        "conexiones": arrayConexionesString,
        "repeticiones": numeroRep,
        "metodo": metodo
    }

    $.ajax({
        type: "POST",
        url: "executeTSP",
        data: JSON.stringify(parametros),
        contentType: 'application/json',
        success: function(response) {
            var {
                variablesP,
                resultadoP,
                valorFinalP
            } = obtenerResultados(response);

            resultDiv.appendChild(variablesP);
            resultDiv.appendChild(resultadoP);
            resultDiv.appendChild(valorFinalP);
        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });

}


function actualizarDatosProblema(){
    var txtNumNodosMaxCut = document.getElementById("txtNumNodosTSP");
    var txtNumRepMaxCut = document.getElementById("txtNumRepTSP");
    var txtConexionesMaxCut = document.getElementById("txtConexTSP");

    if(txtNumNodosMaxCut != null) {
        txtNumNodosMaxCut.textContent = numeroNodos;
    }
    if(txtNumRepMaxCut != null) {
        txtNumRepMaxCut.textContent = numeroRep;
    }
    if(txtConexionesMaxCut != null) {
        var arrayConexionesStringBonita = "";

        for (var i = 0; i < arrayConexiones.length; i++) {
            arrayConexionesStringBonita += arrayConexiones[i].toStringPretty() + "<br>";
        }

        txtConexionesMaxCut.innerHTML = arrayConexionesStringBonita;
    }
}

function seleccionarNumeroNodosTSP() {
    var texto = document.getElementById("numeroNodosTSP").value;
    numeroNodos = texto;

    actualizarDatosProblema();

    limpiarTexto();
}

function seleccionarNumeroRepsTSP() {
    var texto = document.getElementById("numeroRepTSP").value;
    numeroRep = texto;

    document.getElementById("numeroRepTSP").value = "";

    actualizarDatosProblema();
}

function limpiarNumNodosTSP(){
    numeroNodos = 0;
    actualizarDatosProblema();
}

function limpiarNumRepsTSP(){
    numeroRep = 0;
    actualizarDatosProblema();
}

function limpiarConexionesTSP(){
    arrayConexiones = [];
    arrayConexionesString = "";
    actualizarDatosProblema();
}

function agregarConexionTSP() {

    // Seleccionar nodo 1
    var nodo1 = document.getElementById("conexionTSPNodo1").value;

    // Seleccionar nodo 2
    var nodo2 = document.getElementById("conexionTSPNodo2").value;

    // Seleccionar valor conexión
    var valorConexion = document.getElementById("conexionTSPValor").value;

    // Construir objeto conexión
    var conexion = new Conexion(nodo1, nodo2, valorConexion);

    // Guardar conexión en array
    arrayConexiones.push(conexion);

    actualizarDatosProblema();

    limpiarTextoConexion();
}

function cargarArchivoProblema(){
    var archivo = document.getElementById("archivoTextoTSP").files[0];
    var lector = new FileReader();

    arrayConexionesString = "";

    lector.onload = function(evento) {
        var contenido = evento.target.result;
        var lineas = contenido.split('\n');
        var parametro1 = lineas[0].trim();
        var parametro2 = lineas[1].trim();
        var parametro3 = lineas[2].trim();

        //
        numeroNodos = parametro1;
        numeroRep = parametro2;
        arrayConexionesString = parametro3;
        //

        const conexiones = [];
        const partes = arrayConexionesString.split(";");

        for (let i = 0; i < partes.length; i++) {
            const valores = partes[i].split(",");
            const conexion = new Conexion(parseInt(valores[0]), parseInt(valores[1]), parseInt(valores[2]));
            conexiones.push(conexion);
        }

        arrayConexiones = conexiones;

        actualizarDatosProblema();
    };

    lector.readAsText(archivo);
}

class Conexion {
    constructor(nodo1, nodo2, valor) {
        this.nodo1 = nodo1;
        this.nodo2 = nodo2;
        this.valor = valor;
    }

    toString() {
        return this.nodo1 + "," + this.nodo2 + "," + this.valor;
    }

    toStringPretty(){
        return this.nodo1 + " - " + this.nodo2 + " (" + this.valor + ")";
    }
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