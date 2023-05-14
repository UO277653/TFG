var resultDiv = document.getElementById("cajaResultado");
var executeFormMaxCutLocal = document.getElementById("execute-MaxCutLocal");
var executeFormMaxCutReal = document.getElementById("execute-MaxCutReal");

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

    //var xhr = new XMLHttpRequest();
    //xhr.open('POST', executeFormMaxCutReal.action); // ME QUEDÉ AQUÍ, CAMBIAR URL A LA QUE CORRESPONDA


    $.ajax({
        type: "POST",
        url: scriptUrl,
        //data: {script_name: scriptName},
        success: function(response) {
            console.log(response);
            resultDiv.appendChild(document.createTextNode(response));
        },
        error: function(xhr, status, error) {
            console.error(status + ": " + error);
        }
    });

}


/**
executeFormMaxCutLocal.addEventListener("submit", function(event) {
    event.preventDefault();
    resultDiv.innerHTML = "";
    var xhr = new XMLHttpRequest();
    xhr.open('POST', executeFormMaxCutLocal.action);
    xhr.onload = function() {

        resultDiv.appendChild(document.createTextNode(xhr.responseText));

        const imgGrafico = document.createElement("img");
        imgGrafico.src = "../static/img/graph.png";
        resultDiv.appendChild(imgGrafico);

    };
    xhr.send(new FormData(executeFormMaxCutLocal));

});

executeFormMaxCutReal.addEventListener("submit", function(event) {
    event.preventDefault();
    resultDiv.innerHTML = "";
    var xhr = new XMLHttpRequest();
    xhr.open('POST', executeFormMaxCutReal.action);
    xhr.onload = function() {

        resultDiv.appendChild(document.createTextNode(xhr.responseText));

        const imgGrafico = document.createElement("img");
        imgGrafico.src = "../static/img/graph.png";
        resultDiv.appendChild(imgGrafico);

    };
    xhr.send(new FormData(executeFormMaxCutReal));

});

 **/
