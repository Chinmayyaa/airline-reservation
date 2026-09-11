from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.booking.routes import router as booking_router


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


app.include_router(booking_router)


@app.get("/")
def root():
    return {"message": "Airline Reservation API is running"}