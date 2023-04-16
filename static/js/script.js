var executeForm = document.getElementById("execute-MaxCutLocal");
var resultDiv = document.getElementById("cajaResultado");
//var imgGrafico = document.createElement("img");
//img.src = "../img/graph.png";

executeForm.addEventListener("submit", function(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open('POST', executeForm.action);
    xhr.onload = function() {
        resultDiv.appendChild(document.createTextNode(xhr.responseText));
        //resultDiv.appendChild(imgGrafico);
    };
    xhr.send(new FormData(executeForm));
    
});
