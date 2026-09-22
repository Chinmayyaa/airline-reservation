from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone
from .database import db


router = APIRouter(
    prefix="/api/checkin",
    tags=["Check-in"]
)


# -----------------------------
# Request model
# -----------------------------

class CheckInRequest(BaseModel):
    pnr: str


# -----------------------------
# Health check
# -----------------------------

@router.get("/health")
def checkin_health():
    return {
        "message": "Check-in module is working"
    }


# -----------------------------
# Find booking using PNR
# -----------------------------

@router.get("/{pnr}")
def get_booking_for_checkin(pnr: str):

    pnr = pnr.strip().upper()

    if not pnr:
        raise HTTPException(
            status_code=400,
            detail="PNR cannot be empty"
        )

    # Booking collection will be created/used
    # by the Booking + PNR module.
    booking = db.bookings.find_one(
        {"pnr": pnr},
        {"_id": 0}
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found for this PNR"
        )

    return {
        "message": "Booking found",
        "booking": booking
    }


# -----------------------------
# Perform check-in
# -----------------------------

@router.post("/")
def check_in(request: CheckInRequest):

    pnr = request.pnr.strip().upper()

    if not pnr:
        raise HTTPException(
            status_code=400,
            detail="PNR cannot be empty"
        )

    booking = db.bookings.find_one(
        {"pnr": pnr}
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    # Prevent duplicate check-in
    if booking.get("check_in_status") == "checked_in":
        raise HTTPException(
            status_code=400,
            detail="Passenger is already checked in"
        )

    # Check whether booking is confirmed
    if booking.get("status") not in [None, "CONFIRMED", "confirmed"]:
        raise HTTPException(
            status_code=400,
            detail="Only confirmed bookings can check in"
        )

    checkin_time = datetime.now(timezone.utc)

    db.bookings.update_one(
        {"pnr": pnr},
        {
            "$set": {
                "check_in_status": "checked_in",
                "check_in_time": checkin_time
            }
        }
    )

    return {
        "message": "Check-in successful",
        "pnr": pnr,
        "check_in_status": "checked_in",
        "check_in_time": checkin_time
    }


# -----------------------------
# Generate boarding pass
# -----------------------------

@router.get("/{pnr}/boarding-pass")
def generate_boarding_pass(pnr: str):

    pnr = pnr.strip().upper()

    booking = db.bookings.find_one(
        {"pnr": pnr},
        {"_id": 0}
    )

    if not booking:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    if booking.get("check_in_status") != "checked_in":
        raise HTTPException(
            status_code=400,
            detail="Passenger must complete check-in first"
        )

    flight = db.flights.find_one(
        {"flightId": booking.get("flight_id")},
        {"_id": 0}
    )

    boarding_pass = {
        "pnr": pnr,
        "passenger_name": booking.get("passenger_name"),
        "flight_number": (
            booking.get("flight_number")
            or (flight or {}).get("flightNumber")
        ),
        "from": (
            booking.get("from")
            or (flight or {}).get("source")
        ),
        "to": (
            booking.get("to")
            or (flight or {}).get("destination")
        ),
        "travel_date": (
            booking.get("travel_date")
            or (flight or {}).get("date")
        ),
        "seat_number": booking.get("seat_number"),
        "boarding_status": "READY"
    }

    return {
        "message": "Boarding pass generated",
        "boarding_pass": boarding_pass
    }