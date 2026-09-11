from fastapi import FastAPI

from app.booking.routes import router as booking_router


app = FastAPI(title="Airline Reservation System")


app.include_router(booking_router)


@app.get("/")
def root():
    return {"message": "Airline Reservation API is running"}