import React from 'react'
import { render } from 'react-dom'
import './index.css'
//import App from './App'
import SensorView from './SensorView'

render(
  <React.StrictMode>
    <SensorView />
  </React.StrictMode>,
  document.getElementById('root')
)
