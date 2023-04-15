var executeForm = document.getElementById("execute-form");
var resultDiv = document.getElementById("result");

executeForm.addEventListener("submit", function(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open('POST', executeForm.action);
    xhr.onload = function() {
        resultDiv.innerHTML = xhr.responseText;
    };
    xhr.send(new FormData(executeForm));
    
});
