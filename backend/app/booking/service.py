from datetime import datetime, timedelta, timezone
import secrets

from app.database import db


SEAT_LOCK_MINUTES = 10


def generate_pnr():
    """Generate a unique 6-character PNR."""
    characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    while True:
        pnr = "".join(secrets.choice(characters) for _ in range(6))

        if db.bookings.find_one({"pnr": pnr}) is None:
            return pnr


def lock_seat(flight_id: str, seat_number: str):
    """
    Atomically lock an available seat for 10 minutes.

    If the seat is already locked but its lock has expired,
    it can be locked again.
    """

    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(minutes=SEAT_LOCK_MINUTES)

    lock_id = secrets.token_urlsafe(16)

    seat = db.seats.find_one_and_update(
        {
            "flight_id": flight_id,
            "seat_number": seat_number,
            "$or": [
                {"status": "AVAILABLE"},
                {
                    "status": "LOCKED",
                    "lock_expires_at": {"$lte": now}
                }
            ]
        },
        {
            "$set": {
                "status": "LOCKED",
                "lock_id": lock_id,
                "lock_expires_at": expires_at
            }
        },
        return_document=True
    )

    if seat is None:
        return None

    return {
        "lock_id": lock_id,
        "flight_id": flight_id,
        "seat_number": seat_number,
        "status": "LOCKED",
        "expires_at": expires_at
    }


def create_booking(
    flight_id: str,
    passenger_name: str,
    passenger_email: str,
    passenger_phone: str,
    seat_number: str,
    lock_id: str
):
    """
    Confirm a booking using a valid seat lock.
    """

    now = datetime.now(timezone.utc)

    # Confirm that this user still owns the seat lock.
    seat = db.seats.find_one_and_update(
        {
            "flight_id": flight_id,
            "seat_number": seat_number,
            "status": "LOCKED",
            "lock_id": lock_id,
            "lock_expires_at": {"$gt": now}
        },
        {
            "$set": {
                "status": "BOOKED"
            },
            "$unset": {
                "lock_id": "",
                "lock_expires_at": ""
            }
        },
        return_document=True
    )

    if seat is None:
        return None

    pnr = generate_pnr()

    booking = {
        "pnr": pnr,
        "flight_id": flight_id,
        "passenger_name": passenger_name,
        "passenger_email": passenger_email,
        "passenger_phone": passenger_phone,
        "seat_number": seat_number,
        "status": "CONFIRMED",
        "created_at": now
    }

    db.bookings.insert_one(booking)

    return booking


def get_booking_by_pnr(pnr: str):
    """Find a booking using its PNR."""
    return db.bookings.find_one(
        {"pnr": pnr},
        {"_id": 0}
    )