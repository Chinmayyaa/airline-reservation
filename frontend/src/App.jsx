import { useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

function App() {
  const [flightId, setFlightId] = useState('')
  const [seatNumber, setSeatNumber] = useState('')

  const [passengerName, setPassengerName] = useState('')
  const [passengerEmail, setPassengerEmail] = useState('')
  const [passengerPhone, setPassengerPhone] = useState('')

  const [lock, setLock] = useState(null)
  const [pnr, setPnr] = useState('')
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(false)

  const lockSeat = async () => {
    setMessage('')
    setPnr('')

    if (!flightId || !seatNumber) {
      setMessage('Please enter flight ID and seat number.')
      return
    }

    try {
      setLoading(true)

      const response = await fetch(`${API_URL}/api/seats/lock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: flightId,
          seat_number: seatNumber,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.detail || 'Seat is not available.')
        return
      }

      setLock(data)
      setMessage('Seat locked successfully!')
    } catch (error) {
      setMessage('Could not connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  const bookTicket = async () => {
    setMessage('')

    if (!lock) {
      setMessage('Please lock a seat first.')
      return
    }

    if (!passengerName || !passengerEmail || !passengerPhone) {
      setMessage('Please enter all passenger details.')
      return
    }

    try {
      setLoading(true)

      const response = await fetch(`${API_URL}/api/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flight_id: flightId,
          passenger_name: passengerName,
          passenger_email: passengerEmail,
          passenger_phone: passengerPhone,
          seat_number: seatNumber,
          lock_id: lock.lock_id,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        setMessage(data.detail || 'Booking failed.')
        return
      }

      setPnr(data.pnr)
      setMessage('Booking confirmed successfully!')
      setLock(null)
    } catch (error) {
      setMessage('Could not connect to the backend.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="booking-page">
      <div className="booking-card">
        <h1>Airline Reservation</h1>
        <p className="subtitle">Book your flight and reserve your seat</p>

        <div className="form-section">
          <h2>Flight & Seat</h2>

          <input
            type="text"
            placeholder="Flight ID (e.g. AI101)"
            value={flightId}
            onChange={(e) => setFlightId(e.target.value)}
          />

          <input
            type="text"
            placeholder="Seat Number (e.g. 12A)"
            value={seatNumber}
            onChange={(e) => setSeatNumber(e.target.value)}
          />

          <button onClick={lockSeat} disabled={loading || !!lock}>
            {lock ? 'Seat Locked' : 'Lock Seat'}
          </button>
        </div>

        {lock && (
          <div className="lock-box">
            <strong>Seat {lock.seat_number} is locked</strong>
            <p>Lock expires at: {new Date(lock.expires_at).toLocaleString()}</p>
          </div>
        )}

        <div className="form-section">
          <h2>Passenger Details</h2>

          <input
            type="text"
            placeholder="Full Name"
            value={passengerName}
            onChange={(e) => setPassengerName(e.target.value)}
          />

          <input
            type="email"
            placeholder="Email"
            value={passengerEmail}
            onChange={(e) => setPassengerEmail(e.target.value)}
          />

          <input
            type="tel"
            placeholder="Phone Number"
            value={passengerPhone}
            onChange={(e) => setPassengerPhone(e.target.value)}
          />

          <button
            onClick={bookTicket}
            disabled={loading || !lock}
          >
            Confirm Booking
          </button>
        </div>

        {message && <div className="message">{message}</div>}

        {pnr && (
          <div className="pnr-box">
            <p>Your booking is confirmed!</p>
            <h2>PNR: {pnr}</h2>
          </div>
        )}
      </div>
    </div>
  )
}

export default App