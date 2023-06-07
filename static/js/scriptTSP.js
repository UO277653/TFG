var resultDiv = document.getElementById("cajaResultado");

numeroNodos = 0
numeroRep = 0
arrayConexiones = []
arrayConexionesString = ""
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
        data: JSON.stringify(parametros), // JSON.stringify(arrayConexiones)
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

    // Si los 3 no son null, entonces se puede generar la imagen
    // ESTO PARA CUANDO TENGA EL SCRIPT DE PYTHON QUE GENERE LA IMAGEN mirar script.js
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

    // Pillar nodo 1
    var nodo1 = document.getElementById("conexionTSPNodo1").value;

    // Pillar nodo 2
    var nodo2 = document.getElementById("conexionTSPNodo2").value;

    // Pillar valor conexión
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

    arrayConexionesString = ""; // TODO TENGO QUE HACER ALGO PARA BORRARLA SI LA CARGO DE LA OTRA FORMA

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

        console.log("Parámetro 1: " + parametro1);
        console.log("Parámetro 2: " + parametro2);
        console.log("Parámetro 3: " + parametro3);

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
        //return "Nodo 1: " + this.nodo1 + ", Nodo 2: " + this.nodo2 + ", Valor: " + this.valor;
        return this.nodo1 + " - " + this.nodo2 + " (" + this.valor + ")";
    }
}