document.addEventListener("DOMContentLoaded", function() {
    var ctx = document.getElementById('financeChart').getContext('2d');
    var financeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Expenses',
                data: [3000, 3200, 2800, 3500, 3100],
                backgroundColor: 'rgba(255, 99, 132, 0.5)'
            }]
        },
    });
});