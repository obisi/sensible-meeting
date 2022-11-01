'use strict'

const connectButton = document.querySelector('.connect-btn')
connectButton.addEventListener('click', () => {
  const sensorId = document.querySelector('.sensor-id').value
  localStorage.setItem('sensorId', sensorId)
  window.location.href = 'sensor.html'
})
