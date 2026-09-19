from fastapi import FastAPI
from app.checkin import router as checkin_router

app = FastAPI(title="Airline Reservation System")

app.include_router(checkin_router)


@app.get("/")
def root():
    return {
        "message": "Airline Reservation API is running"
    }