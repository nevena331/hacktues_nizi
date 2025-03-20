document.addEventListener("DOMContentLoaded", function () {
    const summaryBtn = document.getElementById("summary-btn");
    const ctx = document.getElementById("summaryChart").getContext("2d");
    const summaryTable = document.getElementById("summaryTable");
    const tableBody = document.getElementById("summaryTableBody");

    let chartInstance = null;

    summaryBtn.addEventListener("click", function () {
        const income = 5400;
        const expenses = 3200;
        const balance = income - expenses;

        if (chartInstance) {
            chartInstance.destroy();
        }
       
        chartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: ["Income", "Expenses"],
                datasets: [
                    {
                        data: [income, expenses],
                        backgroundColor: ["#28a745", "#dc3545"],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });

        tableBody.innerHTML = `
            <tr>
                <td>$${income.toLocaleString()}</td>
                <td>$${expenses.toLocaleString()}</td>
                <td class="${balance >= 0 ? 'text-success' : 'text-danger'}">$${balance.toLocaleString()}</td>
            </tr>
        `;

        summaryTable.style.display = "table";
    });
});