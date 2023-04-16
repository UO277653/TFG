var executeForm = document.getElementById("execute-MaxCutLocal");
var resultDiv = document.getElementById("cajaResultado");

executeForm.addEventListener("submit", function(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open('POST', executeForm.action);
    xhr.onload = function() {
        resultDiv.appendChild(document.createTextNode(xhr.responseText));
    };
    xhr.send(new FormData(executeForm));
    
});
