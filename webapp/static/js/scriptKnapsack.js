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

        resultDiv.appendChild(limpiarResultado());
        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

function ejecutarScriptPython() {

    var parametros = {
        "pesoMaximo": pesoMaximo + "",
        "arrayValores": arrayValores.join(","),
        "arrayPesos": arrayPesos.join(","),
        "metodo": metodo
    }

    $.ajax({
        type: "POST",
        url: "executeKnapsack",
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