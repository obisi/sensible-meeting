const test = require('ava');

const calculatePPM = require("./calculatePPM")

test('calculates PPM from volts', (t) => {
  t.is(calculatePPM(2.2353515625), 723);
  t.is(calculatePPM(2.2294921875), 738);
  t.is(calculatePPM(2.205078125), 806);
})
