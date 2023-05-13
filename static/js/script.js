var resultDiv = document.getElementById("cajaResultado");
var executeFormMaxCutLocal = document.getElementById("execute-MaxCutLocal");
var executeFormMaxCutReal = document.getElementById("execute-MaxCutReal");

$(document).ready(function() {
    $("#comoResolver").click(function() {
        resultDiv.innerHTML = "";

        var solver = document.getElementById("solver").value;
        switch (solver) {
            case "simuladorLocal":
                resultDiv.innerHTML = "1";
                break;
            case "simuladorRemoto":
                resultDiv.innerHTML = "2";
                break;
            case "ordenadorReal":
                resultDiv.innerHTML = "3";
                break;
            case "annealer":
                resultDiv.innerHTML = "4";
                break;
            case "annealerSimulatedAnnealingSolver":
                resultDiv.innerHTML = "5";
                break;
            case "annealerTabuSolver":
                resultDiv.innerHTML = "6";
                break;
            case "annealerSteepestDescentSolver":
                resultDiv.innerHTML = "7";
                break;
        }
    });
});

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
