import React from 'react'
import { useNavigate } from 'react-router-dom'

import './App.css'

export default function WelcomePage({ sensorId, setSensorId }) {
  const navigate = useNavigate()

  return (
    <div className="App">
      <header className="App-header">
        <div>
          <h1>Welcome to Sensible Meeting!</h1>
          <h4>Enter sensor id below to get started</h4>
          <input
            type="text"
            value={sensorId}
            onChange={(event) => setSensorId(event.target.value)}
          ></input>
          <br />
          <button onClick={() => navigate('/sensor-view')}>Connect</button>
        </div>
      </header>
    </div>
  )
}
