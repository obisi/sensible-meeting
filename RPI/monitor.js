const GrovePi = require('grovepi').GrovePi
const Board = GrovePi.board
const AnalogSensor = GrovePi.sensors.base.Analog

const calculatePPM = require("./lib/calculatePPM");

const READ_SAMPLE_INTERVAL = 50;      // How many samples to take in normal operation
const READ_SAMPLE_TIMES = 5;          // The time interval (in ms) between each samples in normal operation

const PIN_NO = 0;

function start(onChange = console.log, msInterval = 1000) {
  const board = new Board({
    debug: true,
    onError: function (err) {
      console.log('Something went wrong:', err)
    },
    onInit: function (res) {
      if (res) {
        console.log('GrovePi Version :: ' + board.version())

        const co2Sensor = new AnalogSensor(PIN_NO);
        co2Sensor.watchDelay = READ_SAMPLE_INTERVAL;
        console.log('co2Sensor (start watch)')

        let countOnChange = 0;

        let volt = 0;
        let countInterval = 0;
        let ppm = 0;
        co2Sensor.on('change', async (value) => {
          // Calculate PPM
          volt += value;
          if (countInterval == READ_SAMPLE_TIMES) {
            volt = (volt / READ_SAMPLE_TIMES) * 5 / 1024;
            ppm = calculatePPM(volt);

            volt = 0;
            countInterval = 0;
          } else {
            countInterval++;
          }

          // Delay sending the latest PPM to `onChange` handler until `msInterval` is reached
          if (countOnChange * READ_SAMPLE_INTERVAL == msInterval) {
            onChange(Number.isNaN(ppm) ? 0 : parseInt(ppm));
            countOnChange = 0;
          } else {
            countOnChange++;
          }
        });

        co2Sensor.watch()
      }
    }
  })

  board.init()

  return board.close
}

module.exports = { start }
