const GrovePi = require('grovepi').GrovePi
const Board = GrovePi.board
const AirQualityAnalogSensor = GrovePi.sensors.AirQualityAnalog

function start(onChange = console.log) {
  const board = new Board({
    debug: true,
    onError: function(err) {
      console.log('Something went wrong:', err)
    },
    onInit: function(res) {
      if (res) {
        console.log('GrovePi Version :: ' + board.version())
  
        const co2Sensor = new AirQualityAnalogSensor(0)
        co2Sensor.watchDelay = 1000
        console.log('co2Sensor (start watch)')
        
        co2Sensor.on('change', onChange)
        co2Sensor.watch()
      }
    }
  })
  
  board.init()

  return board.close
}

module.exports = { start }
