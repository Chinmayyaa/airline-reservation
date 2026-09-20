from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.booking.routes import router as booking_router
from app.routes.flight_routes import router as flight_router

app = FastAPI(title="Airline Reservation System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Flight Search + Seat Management
app.include_router(flight_router)

# Booking + PNR + Seat Lock
app.include_router(booking_router)


@app.get("/")
def read_root():
    return {
        "message": "Airline Reservation API is running"
    }