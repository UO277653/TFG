var resultDiv = document.getElementById("cajaResultado");

pesoMaximo = 0
arrayValores = []
arrayPesos = []
metodo = ""

function seleccionarPesoMaximoKnapsack(){
    pesoMaximo = document.getElementById("pesoMaximo").value;
    limpiarPesoMaximoKnapsack();
}

function limpiarPesoMaximoKnapsack(){
    document.getElementById("pesoMaximo").value = "";

    actualizarDatosProblema();
}

function agregarObjetoKnapsack(){
    var txtValorObjeto = document.getElementById("valorObjeto").value;
    var txtPesoObjeto = document.getElementById("pesoObjeto").value;

    if(txtValorObjeto != "" && txtPesoObjeto != ""){
        arrayValores.push(txtValorObjeto);
        arrayPesos.push(txtPesoObjeto);
    }

    limpiarObjetoKnapsack();
}

function limpiarObjetoKnapsack(){
    var txtValorObjeto = document.getElementById("valorObjeto");
    var txtPesoObjeto = document.getElementById("pesoObjeto");

    txtValorObjeto.value = "";
    txtPesoObjeto.value = "";

    actualizarDatosProblema();
}

function actualizarDatosProblema(){

    var txtNumObjetos = document.getElementById("txtNumObjetos");
    var txtValores = document.getElementById("txtValores");
    var txtPesos = document.getElementById("txtPesos");
    var txtPesoMaximo = document.getElementById("txtPesoMaximo");

    txtNumObjetos.textContent = arrayValores.length;
    txtValores.textContent = arrayValores;
    txtPesos.textContent = arrayPesos;
    txtPesoMaximo.textContent = pesoMaximo;
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

$(document).ready(function() {
    $("#comoResolver").click(function() {
        resultDiv.innerHTML = "";
        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

function ejecutarScriptPython() {

    var parametros = {
        "pesoMaximo": pesoMaximo + "",
        "arrayValores": arrayValores.join(","), // TODO es necesario que los pase a string los array?
        "arrayPesos": arrayPesos.join(","),
        "metodo": metodo
    }

    $.ajax({
        type: "POST",
        url: "executeKnapsack",
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


