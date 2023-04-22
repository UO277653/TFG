var resultDiv = document.getElementById("cajaResultado");
var executeFormMaxCutLocal = document.getElementById("execute-MaxCutLocal");
var executeFormMaxCutReal = document.getElementById("execute-MaxCutReal");


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
