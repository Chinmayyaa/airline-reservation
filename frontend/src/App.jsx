import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  // -------------------------
  // Flight search
  // -------------------------
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");

  const [flights, setFlights] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);

  // -------------------------
  // Seat management
  // -------------------------
  const [seats, setSeats] = useState([]);
  const [selectedSeat, setSelectedSeat] = useState(null);

  // -------------------------
  // Booking
  // -------------------------
  const [passengerName, setPassengerName] = useState("");
  const [passengerEmail, setPassengerEmail] = useState("");
  const [passengerPhone, setPassengerPhone] = useState("");

  const [lock, setLock] = useState(null);
  const [pnr, setPnr] = useState("");

  // -------------------------
  // UI states
  // -------------------------
  const [loadingFlights, setLoadingFlights] = useState(false);
  const [loadingSeats, setLoadingSeats] = useState(false);
  const [loadingBooking, setLoadingBooking] = useState(false);

  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // -------------------------
  // SEARCH FLIGHTS
  // -------------------------
  const searchFlights = async () => {
    setErrorMessage("");
    setSuccessMessage("");
    setFlights([]);
    setSelectedFlight(null);
    setSeats([]);
    setSelectedSeat(null);
    setLock(null);
    setPnr("");

    if (!source.trim() || !destination.trim() || !date) {
      setErrorMessage("Please enter source, destination and date.");
      return;
    }

    if (source.trim().toLowerCase() === destination.trim().toLowerCase()) {
      setErrorMessage("Source and destination cannot be the same.");
      return;
    }

    try {
      setLoadingFlights(true);

      const url =
        `${API_URL}/api/flights/search` +
        `?source=${encodeURIComponent(source.trim())}` +
        `&destination=${encodeURIComponent(destination.trim())}` +
        `&date=${encodeURIComponent(date)}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error("Failed to search flights");
      }

      const data = await response.json();

      setFlights(data.flights || []);

      if (!data.flights || data.flights.length === 0) {
        setErrorMessage(
          "No flights found for the selected route and date."
        );
      } else {
        setSuccessMessage(`${data.flights.length} flight(s) found.`);
      }
    } catch (error) {
      console.error("Flight search error:", error);
      setFlights([]);
      setErrorMessage("Unable to connect to the flight service.");
    } finally {
      setLoadingFlights(false);
    }
  };

  // -------------------------
  // LOAD SEATS
  // -------------------------
  const loadSeats = async (flightId) => {
    try {
      setLoadingSeats(true);
      setErrorMessage("");
      setSuccessMessage("");
      setSelectedSeat(null);
      setLock(null);

      const response = await fetch(
        `${API_URL}/api/flights/${flightId}/seats`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(
          errorData?.detail || "Failed to load seats"
        );
      }

      const data = await response.json();
      setSeats(data.seats || []);
    } catch (error) {
      console.error("Seat loading error:", error);
      setSeats([]);
      setSelectedSeat(null);
      setErrorMessage(
        error.message || "Unable to load seat information."
      );
    } finally {
      setLoadingSeats(false);
    }
  };

  // -------------------------
  // SELECT FLIGHT
  // -------------------------
  const selectFlight = async (flight) => {
    setSelectedFlight(flight);
    setPnr("");
    setLock(null);
    setSelectedSeat(null);
    setErrorMessage("");
    setSuccessMessage("");

    await loadSeats(flight.flightId);
  };

  // -------------------------
  // SELECT ONE SEAT
  // -------------------------
  const selectSeat = (seat) => {
    setErrorMessage("");
    setSuccessMessage("");

    if (seat.status !== "AVAILABLE") {
      return;
    }

    if (selectedSeat?.seatId === seat.seatId) {
      setSelectedSeat(null);
    } else {
      setSelectedSeat(seat);
      setLock(null);
    }
  };

  // -------------------------
  // LOCK SELECTED SEAT
  // -------------------------
  const lockSelectedSeat = async () => {
    if (!selectedFlight || !selectedSeat) {
      setErrorMessage("Please select a seat first.");
      return;
    }

    setErrorMessage("");
    setSuccessMessage("");
    setPnr("");

    try {
      setLoadingBooking(true);

      const response = await fetch(`${API_URL}/api/seats/lock`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          flight_id: selectedFlight.flightId,
          seat_number: selectedSeat.seatNumber,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || "Seat is not available.");
        await loadSeats(selectedFlight.flightId);
        return;
      }

      setLock(data);
      setSuccessMessage(
        `Seat ${data.seat_number} locked successfully for 10 minutes.`
      );
    } catch (error) {
      console.error("Seat lock error:", error);
      setErrorMessage("Could not connect to the booking service.");
    } finally {
      setLoadingBooking(false);
    }
  };

  // -------------------------
  // CONFIRM BOOKING
  // -------------------------
  const bookTicket = async () => {
    setErrorMessage("");
    setSuccessMessage("");

    if (!lock) {
      setErrorMessage("Please lock a seat first.");
      return;
    }

    if (!passengerName || !passengerEmail || !passengerPhone) {
      setErrorMessage("Please enter all passenger details.");
      return;
    }

    try {
      setLoadingBooking(true);

      const response = await fetch(`${API_URL}/api/bookings`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          flight_id: selectedFlight.flightId,
          passenger_name: passengerName,
          passenger_email: passengerEmail,
          passenger_phone: passengerPhone,
          seat_number: selectedSeat.seatNumber,
          lock_id: lock.lock_id,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setErrorMessage(data.detail || "Booking failed.");
        return;
      }

      setPnr(data.pnr);
      setSuccessMessage("Booking confirmed successfully!");
      setLock(null);

      // Refresh seat map so the booked seat is reflected.
      await loadSeats(selectedFlight.flightId);
      setSelectedSeat(null);
    } catch (error) {
      console.error("Booking error:", error);
      setErrorMessage("Could not connect to the booking service.");
    } finally {
      setLoadingBooking(false);
    }
  };

  // -------------------------
  // RESET
  // -------------------------
  const resetSearch = () => {
    setSource("");
    setDestination("");
    setDate("");
    setFlights([]);
    setSelectedFlight(null);
    setSeats([]);
    setSelectedSeat(null);
    setLock(null);
    setPnr("");

    setPassengerName("");
    setPassengerEmail("");
    setPassengerPhone("");

    setErrorMessage("");
    setSuccessMessage("");
  };

  // -------------------------
  // CREATE SEAT ROWS
  // -------------------------
  const seatRows = [];

  for (let i = 0; i < seats.length; i += 6) {
    seatRows.push(seats.slice(i, i + 6));
  }

  return (
    <div className="app">
      {/* HEADER */}
      <header className="app-header">
        <h1>✈️ Airline Reservation System</h1>
        <p>Flight Search, Seat Management & Booking</p>
      </header>

      {/* MESSAGES */}
      {errorMessage && (
        <div className="message error-message">
          {errorMessage}
        </div>
      )}

      {successMessage && (
        <div className="message success-message">
          {successMessage}
        </div>
      )}

      {/* SEARCH */}
      <section className="section">
        <h2>Search Flights</h2>

        <div className="search-container">
          <div className="input-group">
            <label>From</label>
            <input
              type="text"
              placeholder="e.g. Bangalore"
              value={source}
              onChange={(e) => setSource(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>To</label>
            <input
              type="text"
              placeholder="e.g. Delhi"
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
            />
          </div>

          <div className="input-group">
            <label>Date</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>

          <div className="search-buttons">
            <button
              className="primary-button"
              onClick={searchFlights}
              disabled={loadingFlights}
            >
              {loadingFlights ? "Searching..." : "Search Flights"}
            </button>

            <button
              className="secondary-button"
              onClick={resetSearch}
            >
              Reset
            </button>
          </div>
        </div>
      </section>

      {/* FLIGHT RESULTS */}
      <section className="section">
        <h2>Available Flights</h2>

        {!loadingFlights &&
          flights.length === 0 &&
          !errorMessage && (
            <p className="info-text">
              Enter your journey details and search for flights.
            </p>
          )}

        <div className="flight-list">
          {flights.map((flight) => (
            <div
              className={`flight-card ${
                selectedFlight?.flightId === flight.flightId
                  ? "active-flight"
                  : ""
              }`}
              key={flight.flightId}
            >
              <div className="flight-main">
                <div>
                  <span className="flight-label">Flight</span>
                  <h3>{flight.flightNumber}</h3>

                  <p className="route">
                    {flight.source} → {flight.destination}
                  </p>
                </div>

                <div className="flight-time">
                  <span>Departure</span>
                  <strong>{flight.departureTime}</strong>

                  <span>Arrival</span>
                  <strong>{flight.arrivalTime}</strong>
                </div>

                <div className="flight-info">
                  <span>Date</span>
                  <strong>{flight.date}</strong>

                  <span>Capacity</span>
                  <strong>{flight.capacity} seats</strong>
                </div>
              </div>

              <button
                className="primary-button"
                onClick={() => selectFlight(flight)}
              >
                {selectedFlight?.flightId === flight.flightId
                  ? "Selected"
                  : "Select Flight"}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* SEAT MAP */}
      {selectedFlight && (
        <section className="section seat-section">
          <div className="seat-title">
            <div>
              <h2>Seat Map</h2>

              <p>
                <strong>{selectedFlight.flightNumber}</strong>
                {" — "}
                {selectedFlight.source} →{" "}
                {selectedFlight.destination}
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={() => loadSeats(selectedFlight.flightId)}
              disabled={loadingSeats}
            >
              {loadingSeats ? "Refreshing..." : "Refresh Seats"}
            </button>
          </div>

          {loadingSeats ? (
            <p className="info-text">Loading latest seat availability...</p>
          ) : (
            <>
              <div className="seat-map-container">
                <div className="aircraft-label">
                  FRONT OF AIRCRAFT
                </div>

                <div className="seat-header">
                  <span>A</span>
                  <span>B</span>
                  <span>C</span>
                  <span className="aisle"></span>
                  <span>D</span>
                  <span>E</span>
                  <span>F</span>
                </div>

                {seatRows.map((row, rowIndex) => (
                  <div className="seat-row" key={rowIndex}>
                    {row.slice(0, 3).map((seat) => (
                      <button
                        key={seat.seatId}
                        className={`seat ${seat.status.toLowerCase()} ${
                          selectedSeat?.seatId === seat.seatId
                            ? "selected"
                            : ""
                        }`}
                        disabled={seat.status !== "AVAILABLE"}
                        onClick={() => selectSeat(seat)}
                        title={`${seat.seatNumber} - ${seat.status}`}
                      >
                        {seat.seatNumber}
                      </button>
                    ))}

                    <span className="aisle"></span>

                    {row.slice(3, 6).map((seat) => (
                      <button
                        key={seat.seatId}
                        className={`seat ${seat.status.toLowerCase()} ${
                          selectedSeat?.seatId === seat.seatId
                            ? "selected"
                            : ""
                        }`}
                        disabled={seat.status !== "AVAILABLE"}
                        onClick={() => selectSeat(seat)}
                        title={`${seat.seatNumber} - ${seat.status}`}
                      >
                        {seat.seatNumber}
                      </button>
                    ))}
                  </div>
                ))}

                <div className="aircraft-label">
                  REAR OF AIRCRAFT
                </div>
              </div>

              <div className="legend">
                <div>
                  <span className="legend-box available-box"></span>
                  Available
                </div>

                <div>
                  <span className="legend-box booked-box"></span>
                  Booked
                </div>

                <div>
                  <span className="legend-box locked-box"></span>
                  Locked
                </div>

                <div>
                  <span className="legend-box selected-box"></span>
                  Selected
                </div>
              </div>

              <div className="selected-seat-panel">
                <h3>Selected Seat</h3>

                {selectedSeat ? (
                  <>
                    <p>
                      Seat: <strong>{selectedSeat.seatNumber}</strong>
                    </p>

                    {!lock && (
                      <button
                        className="primary-button"
                        onClick={lockSelectedSeat}
                        disabled={loadingBooking}
                      >
                        {loadingBooking
                          ? "Locking..."
                          : "Lock Selected Seat"}
                      </button>
                    )}
                  </>
                ) : (
                  <p className="info-text">
                    Select one available seat to continue.
                  </p>
                )}
              </div>
            </>
          )}
        </section>
      )}

      {/* LOCK INFORMATION + PASSENGER DETAILS */}
      {lock && (
        <section className="section">
          <div className="lock-box">
            <strong>
              Seat {lock.seat_number} is locked
            </strong>

            <p>
              Lock expires at:{" "}
              {new Date(lock.expires_at).toLocaleString()}
            </p>
          </div>

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
              className="primary-button"
              onClick={bookTicket}
              disabled={loadingBooking}
            >
              {loadingBooking
                ? "Confirming..."
                : "Confirm Booking"}
            </button>
          </div>
        </section>
      )}

      {/* PNR */}
      {pnr && (
        <section className="section">
          <div className="pnr-box">
            <p>Your booking is confirmed!</p>
            <h2>PNR: {pnr}</h2>
            <p>
              Flight: {selectedFlight?.flightNumber}
            </p>
          </div>
        </section>
      )}

      <footer>
        <p>
          Airline Reservation System • Flight Search • Seat
          Management • Booking
        </p>
      </footer>
    </div>
  );
}

export default App;