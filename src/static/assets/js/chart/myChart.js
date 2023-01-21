const ctx = document.getElementById('myChart');
const myChart = new Chart(ctx, {
    type: 'line',
    data: {
        labels: JSON.parse((document.querySelector('#labels').value).replace(/'/g, '"')),
        datasets: [{
            data: JSON.parse(document.querySelector('#data').value),
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false,
            },
            title: {
                display: false,
            }
        },
        scales: {
            y: {
                ticks: {
                    callback: function(value) {
                        return value + "€";
                    }
                }
            }
        }
    },
});
