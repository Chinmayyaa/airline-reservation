import { useState } from "react";
import "./App.css";

const API_BASE_URL = "http://127.0.0.1:8000";

function App() {
  // Search fields
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [date, setDate] = useState("");

  // Flight data
  const [flights, setFlights] = useState([]);
  const [selectedFlight, setSelectedFlight] = useState(null);

  // Seat data
  const [seats, setSeats] = useState([]);
  const [selectedSeats, setSelectedSeats] = useState([]);

  // UI states
  const [loadingFlights, setLoadingFlights] = useState(false);
  const [loadingSeats, setLoadingSeats] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // --------------------------------------------------
  // SEARCH FLIGHTS
  // --------------------------------------------------
  const searchFlights = async () => {
    setErrorMessage("");
    setSuccessMessage("");
    setSelectedFlight(null);
    setSeats([]);
    setSelectedSeats([]);

    // Validation
    if (!source.trim() || !destination.trim() || !date) {
      setErrorMessage("Please enter source, destination and date.");
      return;
    }

    if (
      source.trim().toLowerCase() ===
      destination.trim().toLowerCase()
    ) {
      setErrorMessage(
        "Source and destination cannot be the same."
      );
      return;
    }

    try {
      setLoadingFlights(true);

      const url =
        `${API_BASE_URL}/api/flights/search` +
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
        setSuccessMessage(
          `${data.flights.length} flight(s) found.`
        );
      }
    } catch (error) {
      console.error("Flight search error:", error);
      setFlights([]);
      setErrorMessage(
        "Unable to connect to the flight service."
      );
    } finally {
      setLoadingFlights(false);
    }
  };

  // --------------------------------------------------
  // LOAD SEATS
  // --------------------------------------------------
  const loadSeats = async (flightId) => {
    try {
      setLoadingSeats(true);
      setErrorMessage("");
      setSuccessMessage("");

      const response = await fetch(
        `${API_BASE_URL}/api/flights/${flightId}/seats`
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);

        throw new Error(
          errorData?.detail || "Failed to load seats"
        );
      }

      const data = await response.json();

      setSeats(data.seats || []);

      // Remove selected seats that are no longer available
      setSelectedSeats((currentSelectedSeats) =>
        currentSelectedSeats.filter((selectedSeat) =>
          (data.seats || []).some(
            (seat) =>
              seat.seatId === selectedSeat.seatId &&
              seat.status === "AVAILABLE"
          )
        )
      );
    } catch (error) {
      console.error("Seat loading error:", error);
      setSeats([]);
      setSelectedSeats([]);
      setErrorMessage(
        error.message || "Unable to load seat information."
      );
    } finally {
      setLoadingSeats(false);
    }
  };

  // --------------------------------------------------
  // SELECT FLIGHT
  // --------------------------------------------------
  const selectFlight = async (flight) => {
    setSelectedFlight(flight);
    setSelectedSeats([]);
    setErrorMessage("");
    setSuccessMessage("");

    await loadSeats(flight.flightId);
  };

  // --------------------------------------------------
  // SELECT / DESELECT SEAT
  // --------------------------------------------------
  const selectSeat = (seat) => {
    setErrorMessage("");
    setSuccessMessage("");

    // Only available seats can be selected
    if (seat.status !== "AVAILABLE") {
      return;
    }

    const alreadySelected = selectedSeats.some(
      (selectedSeat) =>
        selectedSeat.seatId === seat.seatId
    );

    if (alreadySelected) {
      setSelectedSeats(
        selectedSeats.filter(
          (selectedSeat) =>
            selectedSeat.seatId !== seat.seatId
        )
      );
    } else {
      setSelectedSeats([
        ...selectedSeats,
        seat
      ]);
    }
  };

  // --------------------------------------------------
  // CREATE SEAT ROWS
  // --------------------------------------------------
  const seatRows = [];

  for (let i = 0; i < seats.length; i += 6) {
    seatRows.push(seats.slice(i, i + 6));
  }

  // --------------------------------------------------
  // CONTINUE TO BOOKING MODULE
  // --------------------------------------------------
  const continueToBooking = () => {
    setErrorMessage("");
    setSuccessMessage("");

    if (!selectedFlight) {
      setErrorMessage("Please select a flight.");
      return;
    }

    if (selectedSeats.length === 0) {
      setErrorMessage(
        "Please select at least one available seat."
      );
      return;
    }

    const bookingData = {
      flightId: selectedFlight.flightId,
      flightNumber: selectedFlight.flightNumber,
      seatNumbers: selectedSeats.map(
        (seat) => seat.seatNumber
      ),
    };

    // Handoff data for Booking Module
    console.log(
      "Sending data to Booking Module:",
      bookingData
    );

    setSuccessMessage(
      `Selected seats: ${bookingData.seatNumbers.join(", ")}`
    );

    /*
      IMPORTANT:
      This is the integration point for the Booking Module.

      The Booking teammate can receive:

      {
        flightId,
        flightNumber,
        seatNumbers
      }

      Your module does NOT implement the actual booking.
    */
  };

  // --------------------------------------------------
  // RESET SEARCH
  // --------------------------------------------------
  const resetSearch = () => {
    setSource("");
    setDestination("");
    setDate("");
    setFlights([]);
    setSelectedFlight(null);
    setSeats([]);
    setSelectedSeats([]);
    setErrorMessage("");
    setSuccessMessage("");
  };

  return (
    <div className="app">

      {/* HEADER */}
      <header className="app-header">
        <h1>✈️ Airline Reservation System</h1>
        <p>
          Flight Search & Seat Management
        </p>
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

      {/* SEARCH SECTION */}
      <section className="section">
        <h2>Search Flights</h2>

        <div className="search-container">

          <div className="input-group">
            <label>From</label>
            <input
              type="text"
              placeholder="e.g. Bangalore"
              value={source}
              onChange={(event) =>
                setSource(event.target.value)
              }
            />
          </div>

          <div className="input-group">
            <label>To</label>
            <input
              type="text"
              placeholder="e.g. Delhi"
              value={destination}
              onChange={(event) =>
                setDestination(event.target.value)
              }
            />
          </div>

          <div className="input-group">
            <label>Date</label>
            <input
              type="date"
              value={date}
              onChange={(event) =>
                setDate(event.target.value)
              }
            />
          </div>

          <div className="search-buttons">
            <button
              className="primary-button"
              onClick={searchFlights}
              disabled={loadingFlights}
            >
              {loadingFlights
                ? "Searching..."
                : "Search Flights"}
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

        {loadingFlights && (
          <p className="info-text">
            Searching flights...
          </p>
        )}

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
                  <span className="flight-label">
                    Flight
                  </span>

                  <h3>
                    {flight.flightNumber}
                  </h3>

                  <p className="route">
                    {flight.source} → {flight.destination}
                  </p>
                </div>

                <div className="flight-time">
                  <span>
                    Departure
                  </span>

                  <strong>
                    {flight.departureTime}
                  </strong>

                  <span>
                    Arrival
                  </span>

                  <strong>
                    {flight.arrivalTime}
                  </strong>
                </div>

                <div className="flight-info">
                  <span>
                    Date
                  </span>

                  <strong>
                    {flight.date}
                  </strong>

                  <span>
                    Capacity
                  </span>

                  <strong>
                    {flight.capacity} seats
                  </strong>
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

      {/* SEAT SECTION */}
      {selectedFlight && (
        <section className="section seat-section">

          <div className="seat-title">
            <div>
              <h2>Seat Map</h2>

              <p>
                <strong>
                  {selectedFlight.flightNumber}
                </strong>
                {" — "}
                {selectedFlight.source}
                {" → "}
                {selectedFlight.destination}
              </p>
            </div>

            <button
              className="secondary-button"
              onClick={() =>
                loadSeats(selectedFlight.flightId)
              }
              disabled={loadingSeats}
            >
              {loadingSeats
                ? "Refreshing..."
                : "Refresh Seats"}
            </button>
          </div>

          {loadingSeats ? (
            <p className="info-text">
              Loading latest seat availability...
            </p>
          ) : (
            <>
              {/* SEAT MAP */}
              <div className="seat-map-container">

                <div className="aircraft-label">
                  FRONT OF AIRCRAFT
                </div>

                {/* COLUMN HEADERS */}
                <div className="seat-header">

                  <span>A</span>
                  <span>B</span>
                  <span>C</span>

                  <span className="aisle"></span>

                  <span>D</span>
                  <span>E</span>
                  <span>F</span>

                </div>

                {/* SEAT ROWS */}
                {seatRows.map((row, rowIndex) => (

                  <div
                    className="seat-row"
                    key={rowIndex}
                  >

                    {row.slice(0, 3).map((seat) => (

                      <button
                        key={seat.seatId}
                        className={`seat ${seat.status.toLowerCase()} ${
                          selectedSeats.some(
                            (selectedSeat) =>
                              selectedSeat.seatId ===
                              seat.seatId
                          )
                            ? "selected"
                            : ""
                        }`}
                        disabled={
                          seat.status !== "AVAILABLE"
                        }
                        onClick={() =>
                          selectSeat(seat)
                        }
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
                          selectedSeats.some(
                            (selectedSeat) =>
                              selectedSeat.seatId ===
                              seat.seatId
                          )
                            ? "selected"
                            : ""
                        }`}
                        disabled={
                          seat.status !== "AVAILABLE"
                        }
                        onClick={() =>
                          selectSeat(seat)
                        }
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

              {/* LEGEND */}
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

              {/* SELECTED SEATS */}
              <div className="selected-seat-panel">

                <h3>
                  Selected Seats
                </h3>

                {selectedSeats.length === 0 ? (
                  <p className="info-text">
                    No seats selected
                  </p>
                ) : (
                  <div className="selected-seat-list">

                    {selectedSeats.map((seat) => (
                      <span
                        className="selected-seat-tag"
                        key={seat.seatId}
                      >
                        {seat.seatNumber}
                      </span>
                    ))}

                  </div>
                )}

                <div className="seat-actions">

                  <button
                    className="primary-button booking-button"
                    onClick={continueToBooking}
                    disabled={
                      selectedSeats.length === 0
                    }
                  >
                    Continue to Booking
                  </button>

                </div>

              </div>

            </>
          )}

        </section>
      )}

      {/* FOOTER */}
      <footer>
        <p>
          Airline Reservation System • Flight Search &
          Seat Management Module
        </p>
      </footer>

    </div>
  );
}

export default App;