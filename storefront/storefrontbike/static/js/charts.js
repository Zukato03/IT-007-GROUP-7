document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById('orderStatusChart').getContext('2d');
    const data = JSON.parse(document.getElementById('orderStatusData').textContent);

    const chart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.map(item => item.shipped_status),
            datasets: [{
                data: data.map(item => item.count),
                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
            }],
        },
    });
});
