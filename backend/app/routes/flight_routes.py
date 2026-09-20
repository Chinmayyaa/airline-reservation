from fastapi import APIRouter, HTTPException
from app.database import db

router = APIRouter(prefix="/api/flights", tags=["Flights"])


# Search flights
@router.get("/search")
def search_flights(source: str, destination: str, date: str):

    flights = list(
        db.flights.find(
            {
                "source": source,
                "destination": destination,
                "date": date
            },
            {"_id": 0}
        )
    )

    return {
        "count": len(flights),
        "flights": flights
    }


# Get flight details
@router.get("/{flight_id}")
def get_flight(flight_id: str):

    flight = db.flights.find_one(
        {"flightId": flight_id},
        {"_id": 0}
    )

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    return flight


# Get seat availability
@router.get("/{flight_id}/seats")
def get_seats(flight_id: str):

    # First check whether the flight exists
    flight = db.flights.find_one(
        {"flightId": flight_id}
    )

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    # Get seats from MongoDB
    seats = list(
        db.seats.find(
            {"flightId": flight_id},
            {"_id": 0}
        )
    )

    return {
        "flightId": flight_id,
        "count": len(seats),
        "seats": seats
    }
    
    # Update seat status
@router.patch("/{flight_id}/seats/{seat_number}")
def update_seat_status(flight_id: str, seat_number: str, status: str):

    # Check whether flight exists
    flight = db.flights.find_one(
        {"flightId": flight_id}
    )

    if not flight:
        raise HTTPException(
            status_code=404,
            detail="Flight not found"
        )

    # Validate status
    allowed_statuses = ["AVAILABLE", "LOCKED", "BOOKED"]

    if status.upper() not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid seat status"
        )

    # Check whether seat exists
    seat = db.seats.find_one(
        {
            "flightId": flight_id,
            "seatNumber": seat_number
        }
    )

    if not seat:
        raise HTTPException(
            status_code=404,
            detail="Seat not found"
        )

    # Update seat
    db.seats.update_one(
        {
            "flightId": flight_id,
            "seatNumber": seat_number
        },
        {
            "$set": {
                "status": status.upper()
            }
        }
    )

    return {
        "message": "Seat status updated successfully",
        "flightId": flight_id,
        "seatNumber": seat_number,
        "status": status.upper()
    }



