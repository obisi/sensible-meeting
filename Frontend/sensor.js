'use strict'

const sensorId = localStorage.getItem('sensorId')
document.getElementsByClassName('sensor-header')[0].innerHTML = sensorId

// TODO: fetch data from backend, current chart is a placeholder

const labels = ['January', 'February', 'March', 'April', 'May', 'June']

const data = {
  labels: labels,
  datasets: [
    {
      label: 'My First dataset',
      backgroundColor: 'rgb(255, 99, 132)',
      borderColor: 'rgb(255, 99, 132)',
      data: [0, 10, 5, 2, 20, 30, 45],
    },
  ],
}

const config = {
  type: 'line',
  data: data,
  options: {},
}

const myChart = new Chart(document.getElementById('chart'), config)
document.getElementById('chart').style.display = 'none'

const startSessionButton = document.querySelector('.start-btn')
startSessionButton.addEventListener('click', () => {
  document.getElementById('chart').style.display = 'block'
})
