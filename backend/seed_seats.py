from app.database import db


def create_seats_for_all_flights():

    flights = list(db.flights.find({}, {"_id": 0}))

    seat_letters = ["A", "B", "C", "D", "E", "F"]

    total_created = 0

    for flight in flights:

        flight_id = flight["flightId"]
        capacity = flight["capacity"]

        seats = []

        rows = capacity // 6

        for row in range(1, rows + 1):

            for letter in seat_letters:

                seats.append({
                    "seatId": f"{flight_id}-{row}{letter}",
                    "flightId": flight_id,
                    "seatNumber": f"{row}{letter}",
                    "status": "AVAILABLE"
                })

        # Remove old seats for this flight
        db.seats.delete_many({
            "flightId": flight_id
        })

        # Insert fresh seats
        if seats:
            db.seats.insert_many(seats)

        print(
            f"{flight_id}: {len(seats)} seats created"
        )

        total_created += len(seats)

    print(
        f"\nSeat generation completed."
        f"\nTotal seats created: {total_created}"
    )


create_seats_for_all_flights()