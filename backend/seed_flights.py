from app.database import db


flights = [
    {
        "flightId": "F101",
        "flightNumber": "AI101",
        "source": "Bangalore",
        "destination": "Delhi",
        "date": "2026-09-20",
        "departureTime": "08:00",
        "arrivalTime": "10:45",
        "capacity": 180
    },
    {
        "flightId": "F102",
        "flightNumber": "6E202",
        "source": "Bangalore",
        "destination": "Mumbai",
        "date": "2026-09-20",
        "departureTime": "11:30",
        "arrivalTime": "13:15",
        "capacity": 180
    },
    {
        "flightId": "F103",
        "flightNumber": "AI303",
        "source": "Bangalore",
        "destination": "Delhi",
        "date": "2026-09-21",
        "departureTime": "18:00",
        "arrivalTime": "20:45",
        "capacity": 180
    },
    {
        "flightId": "F104",
        "flightNumber": "6E404",
        "source": "Bangalore",
        "destination": "Chennai",
        "date": "2026-09-21",
        "departureTime": "09:00",
        "arrivalTime": "10:00",
        "capacity": 180
    },
    {
        "flightId": "F105",
        "flightNumber": "AI505",
        "source": "Bangalore",
        "destination": "Hyderabad",
        "date": "2026-09-22",
        "departureTime": "14:00",
        "arrivalTime": "15:15",
        "capacity": 180
    },
    {
        "flightId": "F106",
        "flightNumber": "6E606",
        "source": "Bangalore",
        "destination": "Mumbai",
        "date": "2026-09-22",
        "departureTime": "17:30",
        "arrivalTime": "19:20",
        "capacity": 180
    },
    {
        "flightId": "F107",
        "flightNumber": "AI707",
        "source": "Delhi",
        "destination": "Bangalore",
        "date": "2026-09-23",
        "departureTime": "07:30",
        "arrivalTime": "10:15",
        "capacity": 180
    },
    {
        "flightId": "F108",
        "flightNumber": "6E808",
        "source": "Mumbai",
        "destination": "Bangalore",
        "date": "2026-09-23",
        "departureTime": "12:00",
        "arrivalTime": "13:45",
        "capacity": 180
    }
]


db.flights.delete_many({})
db.flights.insert_many(flights)

print(f"{len(flights)} flights inserted successfully")