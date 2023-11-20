function consultarSesionQiskit(){

    $.ajax({
        type: "GET",
        url: "sesionQiskit",
        contentType: 'application/json',
        success: function(response) {

            document.getElementById("txtSesionQiskit").textContent = response;

        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });
}

function consultarSesionDWave(){

    $.ajax({
        type: "GET",
        url: "sesionDWave",
        contentType: 'application/json',
        success: function(response) {

            document.getElementById("txtSesionDWave").textContent = response;

        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });
}

function cargarSesionQiskit(){

    var parametros = {
        "token": document.getElementById("tokenQiskit").value
    }

    $.ajax({
        type: "POST",
        url: "configQiskit",
        data: JSON.stringify(parametros),
        contentType: 'application/json',
        success: function(response) {

            document.getElementById("tokenQiskit").value = "";
        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });
}

function cargarSesionDWave(){

    var parametros = {
        "token": document.getElementById("tokenDwave").value
    }

    $.ajax({
        type: "POST",
        url: "configDWave",
        data: JSON.stringify(parametros),
        contentType: 'application/json',
        success: function(response) {

            document.getElementById("tokenDwave").value = "";
        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });

}

function validarNumero(input) {

    // Numero actual
    var valorNumerico = input.value.replace(/[^0-9]/g, '');

    // Actualizar el valor numérico sin caracteres no numéricos
    input.value = valorNumerico;
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