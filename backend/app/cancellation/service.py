from app.database import db


# -----------------------------
# CANCEL BOOKING
# -----------------------------

async def cancel_booking(pnr: str):
    booking = await db.bookings.find_one({"pnr": pnr})

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

    seat = booking.get("seat")

    await db.bookings.update_one(
        {"pnr": pnr},
        {
            "$set": {
                "status": "CANCELLED",
                "seat": None
            }
        }
    )

    # Try to promote the next waiting passenger
    promoted = None

    if seat:
        promoted = await promote_next_waitlisted(
            booking.get("flight_id"),
            seat
        )

    if promoted:
        message = (
            f"Booking cancelled. Seat {seat} was assigned "
            f"to waitlisted passenger {promoted.get('pnr')}."
        )
    else:
        message = "Booking cancelled and seat released."

    return {
        "pnr": pnr,
        "status": "CANCELLED",
        "message": message
    }


# -----------------------------
# ADD PASSENGER TO WAITLIST
# -----------------------------

async def add_to_waitlist(
    pnr: str,
    passenger_name: str,
    flight_id: str
):
    existing = await db.waitlist.find_one({"pnr": pnr})

    if existing:
        return {
            "pnr": pnr,
            "status": "ALREADY_WAITLISTED",
            "message": "Passenger is already on the waitlist"
        }

    # Find current last position
    last_entry = await db.waitlist.find_one(
        {"flight_id": flight_id},
        sort=[("position", -1)]
    )

    position = 1

    if last_entry:
        position = last_entry.get("position", 0) + 1

    await db.waitlist.insert_one(
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


# -----------------------------
# GET WAITLIST
# -----------------------------

async def get_waitlist(flight_id: str):
    cursor = db.waitlist.find(
        {
            "flight_id": flight_id,
            "status": "WAITING"
        }
    ).sort("position", 1)

    return await cursor.to_list(length=100)


# -----------------------------
# PROMOTE NEXT WAITLISTED
# -----------------------------

async def promote_next_waitlisted(
    flight_id: str,
    seat: str
):
    if not flight_id:
        return None

    passenger = await db.waitlist.find_one(
        {
            "flight_id": flight_id,
            "status": "WAITING"
        },
        sort=[("position", 1)]
    )

    if not passenger:
        return None

    await db.waitlist.update_one(
        {"_id": passenger["_id"]},
        {
            "$set": {
                "status": "CONFIRMED",
                "seat": seat
            }
        }
    )

    return passenger