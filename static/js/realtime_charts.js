function updateConsumptionChart(customerId, chartInstance) {
  fetch('/api/consumption/?customer_id=' + customerId)
    .then(function(r) { return r.json(); })
    .then(function(data) {
      if (chartInstance && data.labels && data.values) {
        chartInstance.data.labels = data.labels;
        chartInstance.data.datasets[0].data = data.values;
        chartInstance.update('none');
      }
    })
    .catch(function() {});
}

document.addEventListener('DOMContentLoaded', function() {
  var chartEl = document.getElementById('consumptionChart');
  if (!chartEl) return;
  var customerId = chartEl.getAttribute('data-customer-id');
  if (!customerId) return;

  var ctx = chartEl.getContext('2d');
  var chart = new Chart(ctx, {
    type: 'bar',
    data: { labels: [], datasets: [{
      label: 'Consumo (Kz)',
      data: [],
      backgroundColor: 'rgba(227, 6, 19, 0.6)',
      borderColor: '#E30613',
      borderWidth: 2,
      borderRadius: 6,
    }]},
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, ticks: { callback: function(v) { return v + 'Kz'; } } }
      }
    }
  });

  updateConsumptionChart(customerId, chart);
  setInterval(function() { updateConsumptionChart(customerId, chart); }, 30000);
});
