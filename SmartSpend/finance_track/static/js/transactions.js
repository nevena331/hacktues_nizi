document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("transaction-form").addEventListener("submit", function (event) {
        event.preventDefault();
        addTransaction();
    });

    document.getElementById("receipt-image").addEventListener("change", function () {
        uploadReceipt();
    });
});

function toggleForm() {
    const form = document.getElementById("transaction-form");
    form.style.display = form.style.display === "none" ? "block" : "none";
}

function toggleFileUpload() {
    const fileForm = document.getElementById("file-upload-form");
    fileForm.style.display = fileForm.style.display === "none" ? "block" : "none";
}

function addTransaction() {
    const date = document.getElementById("date").value;
    const description = document.getElementById("description").value;
    const amount = document.getElementById("amount").value;
    const type = document.getElementById("type").value;

    if (!date || !description || !amount) {
        alert("Please fill in all fields.");
        return;
    }

    const table = document.getElementById("transaction-table");
    const row = table.insertRow();
    row.innerHTML = `
        <td>${date}</td>
        <td>${description}</td>
        <td>$${amount}</td>
        <td class="${type === 'Income' ? 'text-success' : 'text-danger'}">${type}</td>
        <td></td>
    `;

    document.getElementById("transaction-form").reset();
    toggleForm();
}

document.getElementById("receipt-image").addEventListener("change", function () {
    const file = this.files[0];

    if (!file) {
        alert("Please select an image.");
        return;
    }

    const reader = new FileReader();
    reader.onloadend = function () {
        const base64String = reader.result.split(",")[1]; // Extract Base64 data
        sendToBackend(base64String);
    };
    reader.readAsDataURL(file);
});

function sendToBackend(base64String) {
    fetch("/upload-receipt/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ image: base64String })
    })
    .then(response => response.json())
    .then(data => alert("Receipt uploaded successfully!"))
    .catch(error => console.error("Error:", error));
}