import React, { useState } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'react-chartjs-2'
import faker from 'faker'
import axios from 'axios'

const labels = ['January', 'February', 'March', 'April', 'May', 'June', 'July']

export default function SensorView({ sensorId }) {
  const [state, setState] = useState({
    datasets: [],
  })

  const handleStartSession = async () => {
    const response = await axios.post(
      'http://localhost:5000/api/v1/session/register',
      { sensor_id: '123', num_people: '1', location: 'asd' }
    )
    console.log('data: ', response.data)

    setState({
      labels,
      datasets: [
        {
          label: 'Measured',
          data: labels.map(() =>
            faker.datatype.number({ min: -1000, max: 1000 })
          ),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
        {
          label: 'Prediction',
          data: labels.map(() =>
            faker.datatype.number({ min: -1000, max: 1000 })
          ),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        },
      ],
    })
  }

  const handleStopSession = async () => {
    const response = await axios.post(
      'http://localhost:5000/api/v1/session/terminate',
      { session: '1234' }
    )
    console.log('data: ', response.data)

    setState({
      labels,
      datasets: [],
    })
  }

  ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
  )

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: 'CO2 level',
      },
    },
  }

  return (
    <div>
      <div className="flex-container">
        <h1 className="flex-item sensor-header">Sensor {sensorId}</h1>
        {state.datasets.length ? (
          <button className="start-btn" onClick={() => handleStopSession()}>
            Stop session
          </button>
        ) : (
          <button className="start-btn" onClick={() => handleStartSession()}>
            Start session
          </button>
        )}
        <Line options={options} data={state} />
      </div>
    </div>
  )
}
