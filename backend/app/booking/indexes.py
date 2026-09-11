from app.database import db

def create_indexes():
    db.bookings.create_index("pnr", unique=True)
    db.seats.create_index(
        [("flight_id", 1), ("seat_number", 1)],
        unique=True
    )