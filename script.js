fetch('http://127.0.0.1:5000/previsao', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ idade: idade, frequencia: frequencia })
  })
  .then(response => response.json())
  .then(data => {
    document.getElementById('status').innerText = 'Cancelamento: ' + data.cancelamento;
    document.getElementById('acuracia').innerText = 'Acurácia do Modelo: ' + (data.acuracia * 100).toFixed(2) + '%';
  });
  