document.addEventListener("DOMContentLoaded", function () {
    const summaryBtn = document.getElementById("summary-btn");
    const ctx = document.getElementById("summaryChart").getContext("2d");
    const summaryTable = document.getElementById("summaryTable");
    const tableBody = document.getElementById("summaryTableBody");

    let chartInstance = null;

    summaryBtn.addEventListener("click", function () {
        const expenseCategories = ["Food & Beverage", "Transportation", "Groceries", "Healthcare", "Utilities", "Other"];
        const expenseValues = [800, 600, 700, 500, 400, 200]; 

        const totalExpenses = expenseValues.reduce((acc, val) => acc + val, 0);

        if (chartInstance) {
            chartInstance.destroy();
        }

        chartInstance = new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: expenseCategories,
                datasets:[
                    {
                        data: expenseValues,
                        backgroundColor: ["#dc3545", "#fd7e14", "#ffc107", "#17a2b8", "#6610f2", "#6c757d"],
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });

        let tableHTML = `
            <tr>
                <td>
                    <ul>
                        ${expenseCategories.map((category, index) => `<li>${category}: $${expenseValues[index].toLocaleString()}</li>`).join("")}
                    </ul>
                </td>
                <td class="text-danger">$${totalExpenses.toLocaleString()}</td>
            </tr>
        `;

        tableBody.innerHTML = tableHTML;
        summaryTable.style.display = "table";
    });
});