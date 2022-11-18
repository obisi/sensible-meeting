import React, { useState } from 'react'
import { Routes, Route } from 'react-router-dom'

import WelcomePage from './WelcomePage'
import SensorView from './SensorView'
import './App.css'

export default function App() {
  const [sensorId, setSensorId] = useState('')

  return (
    <div>
      <Routes>
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
      </Routes>
    </div>
  )
}
