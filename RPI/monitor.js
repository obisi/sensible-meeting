const GrovePi = require('grovepi').GrovePi
const Board = GrovePi.board
const AnalogSensor = GrovePi.sensors.base.Analog

const DC_GAIN = 8.5;                // The DC gain of amplifier
const READ_SAMPLE_INTERVAL = 50;    // How many samples to take in normal operation
const READ_SAMPLE_TIMES = 5;        // The time interval (in ms) between each samples in normal operation
const ZERO_POINT_VOLTAGE = 2 / 8.5; // The output of the sensor in volts when the concentration of CO2 is 400PPM
const REACTION_VOLTAGE = 0.030;     // The voltage drop of the sensor when move the sensor from air into 1000ppm CO2

/**
 * Two points are taken from the curve.
 * with these two points, a line is formed which is
 * "approximately equivalent" to the original curve.
 * data format:{ x, y, slope}; point1: (lg400, 0.324), point2: (lg4000, 0.280)
 * slope = ( reaction voltage ) / (log400 –log1000)
 */
const CO2_CURVE = [2.602, ZERO_POINT_VOLTAGE, (REACTION_VOLTAGE / (2.602 - 3))];

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

function calculatePPM(volts) {
  return Math.round(Math.pow(10, ((volts / DC_GAIN) - CO2_CURVE[1]) / CO2_CURVE[2] + CO2_CURVE[0]), 2);
}

module.exports = { start }
