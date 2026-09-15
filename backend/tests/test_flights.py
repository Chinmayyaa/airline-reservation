from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# --------------------------------------------------
# TEST 1: Valid flight search
# --------------------------------------------------

def test_search_flights_success():

    response = client.get(
        "/api/flights/search",
        params={
            "source": "Bangalore",
            "destination": "Delhi",
            "date": "2026-09-20"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] >= 1
    assert len(data["flights"]) >= 1

    flight = data["flights"][0]

    assert flight["source"] == "Bangalore"
    assert flight["destination"] == "Delhi"
    assert flight["date"] == "2026-09-20"


# --------------------------------------------------
# TEST 2: No flights found
# --------------------------------------------------

def test_search_flights_no_results():

    response = client.get(
        "/api/flights/search",
        params={
            "source": "Bangalore",
            "destination": "Kolkata",
            "date": "2026-09-20"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["count"] == 0
    assert data["flights"] == []


# --------------------------------------------------
# TEST 3: Seat availability
# --------------------------------------------------

def test_get_seat_availability():

    response = client.get(
        "/api/flights/F101/seats"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["flightId"] == "F101"
    assert data["count"] == 180
    assert len(data["seats"]) == 180


# --------------------------------------------------
# TEST 4: Seat status validation
# --------------------------------------------------

def test_update_seat_invalid_status():

    response = client.patch(
        "/api/flights/F101/seats/1A",
        params={
            "status": "INVALID"
        }
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Invalid seat status"


# --------------------------------------------------
# TEST 5: Invalid flight ID
# --------------------------------------------------

def test_invalid_flight_id():

    response = client.get(
        "/api/flights/INVALID/seats"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Flight not found"


# --------------------------------------------------
# TEST 6: Invalid seat number
# --------------------------------------------------

def test_invalid_seat_number():

    response = client.patch(
        "/api/flights/F101/seats/99Z",
        params={
            "status": "BOOKED"
        }
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Seat not found"