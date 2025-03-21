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

function uploadReceipt() {
    const fileInput = document.getElementById("receipt-image");
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const table = document.getElementById("transaction-table");
            const lastRow = table.rows[table.rows.length - 1];
            const cell = lastRow.cells[4];
            cell.innerHTML = `<img src="${e.target.result}" alt="Receipt" width="50">`;
        };
        reader.readAsDataURL(file);
    }
}