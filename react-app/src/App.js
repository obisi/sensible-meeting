import React, { useState } from 'react'
import { BrowserRouter as Router, Route } from 'react-router-dom'

import WelcomePage from './WelcomePage'
import SensorView from './SensorView'
import './App.css'

export default function App() {
  const [sensorId, setSensorId] = useState('')

  return (
    <div>
      <Router>
        <Route
          path="/"
          element={
            <WelcomePage sensorId={sensorId} setSensorId={setSensorId} />
          }
        />
        <Route
          path="/sensor-view"
          element={<SensorView sensorId={sensorId} />}
        />
      </Router>
    </div>
  )
}
