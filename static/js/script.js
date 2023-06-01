var resultDiv = document.getElementById("cajaResultado");
var executeFormMaxCutLocal = document.getElementById("execute-MaxCutLocal");
var executeFormMaxCutReal = document.getElementById("execute-MaxCutReal");

var numeroNodos = 0;
var numeroRep = 0;
var arrayConexiones = [];
var arrayConexionesString = "";


$(document).ready(function() {
    $("#comoResolver").click(function() {
        resultDiv.innerHTML = "";

        var solver = document.getElementById("solver").value;
        switch (solver) { // Se puede optimizar mucho si en el nombre del solver se incluye la URL del script
            case "simuladorLocal":
                ejecutarScriptPython("/executeMaxCutLocal");
                break;
            case "simuladorRemoto":
                ejecutarScriptPython("/executeMaxCutRemoto");
                break;
            case "ordenadorReal":
                ejecutarScriptPython("/executeMaxCutReal");
                break;
            case "annealer":
                ejecutarScriptPython("/executeMaxCutAnnealer");
                break;
            case "annealerSimulatedAnnealingSolver":
                ejecutarScriptPython("/executeMaxCutAnnealerSimulatedAnnealingSolver");
                break;
            case "annealerTabuSolver":
                ejecutarScriptPython("/executeMacCutAnnealerTabuSolver");
                break;
            case "annealerSteepestDescentSolver":
                ejecutarScriptPython("/executeMaxCutSteepestDescentSolver");
                break;
        }
    });
});

function ejecutarScriptPython(scriptUrl) {

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
        "repeticiones": numeroRep
    }

    $.ajax({
        type: "POST",
        url: scriptUrl,
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
    var txtNumNodosMaxCut = document.getElementById("txtNumNodosMaxCut");
    var txtNumRepMaxCut = document.getElementById("txtNumRepMaxCut");
    var txtConexionesMaxCut = document.getElementById("txtConexMaxCut");

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
    // ESTO PARA CUANDO TENGA EL SCRIPT DE PYTHON QUE GENERE LA IMAGEN
    /*

    $.ajax({
        type: "POST",
        url: TODO URL DEL SCRIPT QUE GENERA LA IMAGEN
        data: JSON.stringify(parametros),
        contentType: 'application/json',
        success: function(response) {

            var contenedorGrafico = document.getElementById("graficoMaxCut");
            var image = document.createElement("img");
            image.src = "ruta_de_la_imagen.jpg";
            image.alt = "Texto alternativo de la imagen";
            container.appendChild(image);

        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });
     */
}

function seleccionarNumeroNodosMaxCut() {
    var texto = document.getElementById("numeroNodosMaxCut").value;
    numeroNodos = texto;

    actualizarDatosProblema();

    limpiarTexto();
}

function seleccionarNumeroRepsMaxCut() {
    var texto = document.getElementById("numeroRepMaxCut").value;
    numeroRep = texto;

    document.getElementById("numeroRepMaxCut").value = "";

    actualizarDatosProblema();
}

function agregarConexionMaxCut() {

    // Pillar nodo 1
    var nodo1 = document.getElementById("conexionMaxCutNodo1").value;

    // Pillar nodo 2
    var nodo2 = document.getElementById("conexionMaxCutNodo2").value;

    // Pillar valor conexión
    var valorConexion = document.getElementById("conexionMaxCutValor").value;

    // Construir objeto conexión
    var conexion = new Conexion(nodo1, nodo2, valorConexion);

    // Guardar conexión en array
    arrayConexiones.push(conexion);

    actualizarDatosProblema();

    /// VIEJO
    limpiarTextoConexion();
}

function limpiarTexto() {
    document.getElementById("numeroNodosMaxCut").value = "";
}

function limpiarTextoConexion() {
    document.getElementById("conexionMaxCutNodo1").value = "";
    document.getElementById("conexionMaxCutNodo2").value = "";
    document.getElementById("conexionMaxCutValor").value = "";
}

function cargarArchivoProblema(){
    var archivo = document.getElementById("archivoTexto").files[0];
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

function limpiarNumNodosMaxCut(){
    numeroNodos = 0;
    actualizarDatosProblema();
}

function limpiarNumRepsMaxCut(){
    numeroRep = 0;
    actualizarDatosProblema();
}

function limpiarConexionesMaxCut(){
    arrayConexiones = [];
    arrayConexionesString = "";
    actualizarDatosProblema();
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