from app.database import db


def cancel_booking(pnr: str):
    booking = db.bookings.find_one({"pnr": pnr})

    if not booking:
        return {
            "pnr": pnr,
            "status": "NOT_FOUND",
            "message": "Booking not found"
        }

    if booking.get("status") == "CANCELLED":
        return {
            "pnr": pnr,
            "status": "ALREADY_CANCELLED",
            "message": "Booking is already cancelled"
        }

    # Your booking module stores the seat as seat_number
    seat_number = booking.get("seat_number")

    # Mark booking as cancelled
    db.bookings.update_one(
        {"pnr": pnr},
        {
            "$set": {
                "status": "CANCELLED"
            }
        }
    )

    # Release the seat
    if seat_number:
        db.seats.update_one(
            {
                "flight_id": booking.get("flight_id"),
                "seat_number": seat_number
            },
            {
                "$set": {
                    "status": "AVAILABLE"
                },
                "$unset": {
                    "lock_id": "",
                    "lock_expires_at": ""
                }
            }
        )

    # Try to promote the next waiting passenger
    promoted = None

    if seat_number:
        promoted = promote_next_waitlisted(
            booking.get("flight_id"),
            seat_number
        )

    if promoted:
        message = (
            f"Booking cancelled. Seat {seat_number} was assigned "
            f"to waitlisted passenger {promoted.get('pnr')}."
        )
    else:
        message = "Booking cancelled and seat released."

    return {
        "pnr": pnr,
        "status": "CANCELLED",
        "message": message
    }


def add_to_waitlist(
    pnr: str,
    passenger_name: str,
    flight_id: str
):
    existing = db.waitlist.find_one({"pnr": pnr})

    if existing:
        return {
            "pnr": pnr,
            "status": "ALREADY_WAITLISTED",
            "message": "Passenger is already on the waitlist"
        }

    last_entry = db.waitlist.find_one(
        {"flight_id": flight_id},
        sort=[("position", -1)]
    )

    position = 1

    if last_entry:
        position = last_entry.get("position", 0) + 1

    db.waitlist.insert_one(
        {
            "pnr": pnr,
            "passenger_name": passenger_name,
            "flight_id": flight_id,
            "status": "WAITING",
            "position": position
        }
    )

    return {
        "pnr": pnr,
        "status": "WAITING",
        "message": f"Passenger added to waitlist at position {position}"
    }


def get_waitlist(flight_id: str):
    return list(
        db.waitlist.find(
            {
                "flight_id": flight_id,
                "status": "WAITING"
            },
            {"_id": 0}
        ).sort("position", 1)
    )


def promote_next_waitlisted(
    flight_id: str,
    seat_number: str
):
    if not flight_id:
        return None

    passenger = db.waitlist.find_one(
        {
            "flight_id": flight_id,
            "status": "WAITING"
        },
        sort=[("position", 1)]
    )

    if not passenger:
        return None

    # Mark waitlisted passenger as confirmed
    db.waitlist.update_one(
        {"_id": passenger["_id"]},
        {
            "$set": {
                "status": "CONFIRMED",
                "seat_number": seat_number
            }
        }
    )

    # Reserve the released seat for the promoted passenger
    db.seats.update_one(
        {
            "flight_id": flight_id,
            "seat_number": seat_number
        },
        {
            "$set": {
                "status": "BOOKED"
            }
        }
    )

    return {
        **passenger,
        "seat_number": seat_number,
        "status": "CONFIRMED"
    }