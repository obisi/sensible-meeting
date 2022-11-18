const getmac = require('getmac');

/**
 * Returns sensor id based on MAC address (with colons stripped).
 * If MAC address is `fe:51:77:24:c8:4e`, the return value will be `fe517724c84e`.
 * @returns 
 */
function getSensorId() {
  return getmac.default().replace(/:/g, '');
}

module.exports = getSensorId;
