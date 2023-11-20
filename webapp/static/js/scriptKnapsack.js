var resultDiv = document.getElementById("cajaResultado");

pesoMaximo = 0
arrayValores = []
arrayPesos = []
metodo = ""
var numeroRep = 0;

$(document).ready(function() {
    $("#comoResolver").click(function() {

        metodo = document.getElementById("solver").value;
        ejecutarScriptPython();
    });
});

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

    document.getElementById("error_componente_objeto").style.display = "none";

    if(txtValorObjeto != "" && txtPesoObjeto != ""){
        arrayValores.push(txtValorObjeto);
        arrayPesos.push(txtPesoObjeto);
        limpiarObjetoKnapsack();
    } else {
        document.getElementById("error_componente_objeto").style.display = "block";
    }

}

function limpiarObjetoKnapsack(){
    var txtValorObjeto = document.getElementById("valorObjeto");
    var txtPesoObjeto = document.getElementById("pesoObjeto");

    txtValorObjeto.value = "";
    txtPesoObjeto.value = "";

    actualizarDatosProblema();
}

function actualizarDatosProblema(){

    limpiarErrores();
    limpiarResultado();

    var txtNumObjetos = document.getElementById("txtNumObjetos");
    var txtValores = document.getElementById("txtValores");
    var txtPesos = document.getElementById("txtPesos");
    var txtPesoMaximo = document.getElementById("txtPesoMaximo");
    var txtNumRepKnapsack = document.getElementById("txtNumRepKnapsack");

    if(txtNumRepKnapsack != null) {
        txtNumRepKnapsack.textContent = numeroRep;
    }

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

    numeroRep = parseInt(lineas[0]);

    pesoMaximo = parseInt(lineas[1]);

    var valoresString = lineas[2].split(",");
    arrayValores = valoresString.map(function(valor) {
        return parseInt(valor);
    });

    var pesosString = lineas[3].split(",");
    arrayPesos = pesosString.map(function(peso) {
        return parseInt(peso);
    });

    // Actualizar los datos del problema
    actualizarDatosProblema();
}

function limpiarNumRepsKnapsack(){
    numeroRep = 0;
    actualizarDatosProblema();
}

function ejecutarScriptPython() {

    document.getElementById("error_datosIncompletos_Knapsack").style.display = "none";

    if(pesoMaximo > 0 && arrayValores.length > 0 && arrayPesos.length > 0 && numeroRep > 0) {

        resultDiv.appendChild(limpiarResultado());

        var parametros = {
            "pesoMaximo": pesoMaximo + "",
            "arrayValores": arrayValores.join(","),
            "arrayPesos": arrayPesos.join(","),
            "metodo": metodo,
            "repeticiones": numeroRep + ""
        }

        $.ajax({
            type: "POST",
            url: "executeKnapsack",
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
        document.getElementById("error_datosIncompletos_Knapsack").style.display = "block";
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

function limpiarErrores(){
    document.getElementById("error_componente_objeto").style.display = "none";
    document.getElementById("error_datosIncompletos_Knapsack").style.display = "none";
}

function seleccionarNumeroRepsKnapsack() {
    var texto = document.getElementById("numeroRepKnapsack").value;
    numeroRep = texto;

    document.getElementById("numeroRepKnapsack").value = "";

    actualizarDatosProblema();
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