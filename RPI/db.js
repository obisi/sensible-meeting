require('dotenv').config()
const { Client } = require('pg')
const client = new Client()

async function init() {
  await client.connect()

  return {
    store: async (table, payload) => {
      const fields = Object.keys(payload).join(",")
      const valuePlaceholder = Object.keys(payload).map((_, i) => `$${i+1}`).join(",")
      const values = Object.values(payload)
      const text = `INSERT INTO ${table} (${fields}) VALUES (${valuePlaceholder}) RETURNING *`
      try {
        const res = await client.query(text, values)
        return res.rows[0]
      } catch (err) {
        console.log(err.stack)
        return null
      }
    },
    close: client.end
  }
}

module.exports = { init }
