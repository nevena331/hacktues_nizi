function toggleForm() {
    var loginBox = document.getElementById("login-box");
    var registerBox = document.getElementById("register-box");
    
    if (loginBox.style.display === "none") {
        loginBox.style.display = "block";
        registerBox.style.display = "none";
    } else {
        loginBox.style.display = "none";
        registerBox.style.display = "block";
    }
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("login-box").style.display = "block";
});