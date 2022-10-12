const monitor = require("./monitor");
const db = require("./db");

const table = "csproject_co2_reading";

(async () => {
  const { store } = await db.init();
  monitor.start(async (value) => {
    const row = await store(table, { value: Number.isNaN(value) ? 0 : value });

    console.clear();
    console.log("reading stored:", row);
  });
})();
