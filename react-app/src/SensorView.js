import React, { useEffect, useState } from 'react'
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

const labels = ['16.39', '16.40', '16.41', '16.42', '16.43', '16.44', '16.45']
const threshold = ''

export default function SensorView({ sensorId }) {
  const [state, setState] = useState({
    datasets: [],
  })
  const [sessionId, setSessionId] = useState('')
  const [intervalId, setIntervalId] = useState('')

  const setGraphState = () => {
    setState({
      labels,
      datasets: [
        {
          label: 'Measured',
          data: labels.map(() => faker.datatype.number({ min: 0, max: 1200 })),
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.5)',
        },
        {
          label: 'Prediction',
          data: labels.map(() => faker.datatype.number({ min: 0, max: 1200 })),
          borderColor: 'rgb(53, 162, 235)',
          backgroundColor: 'rgba(53, 162, 235, 0.5)',
        },
        {
          label: 'Threshold',
          data: labels.map(() => 1000),
          borderColor: 'rgb(255, 255, 0)',
          backgroundColor: 'rgba(255, 255, 0, 0.5)',
        },
      ],
    })
  }

  const handleStartSession = async () => {
    const response = await axios.post(
      'http://localhost:5000/api/v1/session/register',
      { sensor_id: '2', num_people: '1', location: 'Helsinki' }
    )
    console.log('register data: ', response.data)

    if (response.data.is_ok) {
      setSessionId(response.data.session_id)

      const intervalId = setInterval(() => {
        axios
          .get(
            `http://localhost:5000/api/v1/session/get_session?session_id=${response.data.session_id}`
          )
          .then((response) => {
            console.log('session data: ', response.data)
            setGraphState()
          })
      }, 1000)

      setIntervalId(intervalId)
    }
  }

  const handleStopSession = async () => {
    const response = await axios.post(
      'http://localhost:5000/api/v1/session/terminate',
      { session: sessionId }
    )
    console.log('terminate data: ', response.data)
    setSessionId('')
    clearInterval(intervalId)
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
