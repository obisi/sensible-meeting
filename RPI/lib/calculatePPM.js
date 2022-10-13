const DC_GAIN = 8.5;                  // The DC gain of amplifier
const ZERO_POINT_VOLTAGE = 2.4 / 8.5; // The output of the sensor in volts when the concentration of CO2 is 400PPM
const REACTION_VOLTAGE = 0.030;       // The voltage drop of the sensor when move the sensor from air into 1000ppm CO2

/**
 * Two points are taken from the curve.
 * with these two points, a line is formed which is
 * "approximately equivalent" to the original curve.
 * data format:{ x, y, slope}; point1: (lg400, 0.324), point2: (lg4000, 0.280)
 * slope = ( reaction voltage ) / (log400 –log1000)
 */
const CO2_CURVE = [2.602, ZERO_POINT_VOLTAGE, (REACTION_VOLTAGE / (2.602 - 3))];

function calculatePPM(volts) {
  if ((volts / DC_GAIN) >= ZERO_POINT_VOLTAGE) {
    return -1;
  } else {
    return Math.round(Math.pow(10, ((volts / DC_GAIN) - CO2_CURVE[1]) / CO2_CURVE[2] + CO2_CURVE[0]), 2);
  }
}

module.exports = calculatePPM
