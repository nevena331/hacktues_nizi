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
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const summaryBtn = document.getElementById("summary-btn");
    const ctxIncome = document.getElementById("incomeChart").getContext("2d");
    const incomeChartContainer = document.getElementById("incomeChartContainer");

    let incomeChartInstance = null;

    summaryBtn.addEventListener("click", function () {
        const labels = ["Day 5", "Day 10", "Day 15", "Day 20", "Day 25", "Day 30"];
        const datapoints = [3100, 2600, 3000, -500, 2000, -1000]; 

        if (incomeChartInstance) {
            incomeChartInstance.destroy();
        }

        const data = {
            labels: labels,
            datasets: [{
                label: 'Income',
                data: datapoints,
                borderColor: 'rgba(75, 192, 192, 1)', 
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 2,
                pointRadius: 6,
                pointBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 8,
                pointHoverBackgroundColor: 'rgba(255, 99, 132, 1)',
                pointHoverBorderColor: '#fff',
                cubicInterpolationMode: 'monotone',
                tension: 0.4,
                segment: {
                    borderColor: ctx => {
                        const index = ctx.p1DataIndex; 
                        return datapoints[index] < 0 ? 'rgba(255, 0, 0, 1)' : 'rgba(75, 192, 192, 1)';
                    }
                }
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Income in the past month'
                    },
                },
                interaction: {
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Value'
                        },
                        suggestedMin: -1000,
                        suggestedMax: 5000
                    }
                },
                maintainAspectRatio: false,
            },
        };

        incomeChartInstance = new Chart(ctxIncome, config);
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const summaryBtn = document.getElementById("summary-btn");
    const ctxIncomeLast5Months = document.getElementById("incomeLast5MonthsChart").getContext("2d");
    let incomeLast5MonthsChartInstance = null;

    summaryBtn.addEventListener("click", function () {
        const labels = ["February", "March", "April", "May", "June"]; 
        const incomeData = [4000, 3500, 3500, 3000, 4500]; 

        if (incomeLast5MonthsChartInstance) {
            incomeLast5MonthsChartInstance.destroy();
        }

        const data = {
            labels: labels,
            datasets: [{
                label: 'Income (Last 5 Months)',
                data: incomeData,
                borderColor: 'rgba(34, 197, 94, 1)', 
                backgroundColor: 'rgba(34, 197, 94, 0.2)',
                borderWidth: 2,
                pointRadius: 6,
                pointBackgroundColor: 'rgba(34, 197, 94, 1)',
                pointBorderColor: '#fff',
                pointHoverRadius: 8,
                pointHoverBackgroundColor: 'rgba(34, 197, 94, 1)',
                pointHoverBorderColor: '#fff',
                cubicInterpolationMode: 'monotone',
                tension: 0.4
            }]
        };

        const config = {
            type: 'line',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Income Over the Last 5 Months'
                    },
                },
                interaction: {
                    intersect: false,
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Income ($)'
                        },
                        suggestedMin: 0,
                        suggestedMax: 5000
                    }
                },
                maintainAspectRatio: false,
            },
        };

        incomeLast5MonthsChartInstance = new Chart(ctxIncomeLast5Months, config);
    });
});