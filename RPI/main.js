const monitor = require("./monitor");
const db = require("./db");
const getSensorId = require("./lib/getSensorId")

const table = "csproject_co2_reading";

(async () => {
  const { store } = await db.init();
  const session_id = createSessionId();
  const sensor_id = await getSensorId();

  monitor.start(async (value) => {
    // console.log("ppm:", value);
    const row = await store(table, { sensor_id, session_id, value });
    console.clear();
    console.log(`reading stored: ${row.value} ppm`);
  });
})();

function createSessionId() {
  return new Date().getTime();
}
