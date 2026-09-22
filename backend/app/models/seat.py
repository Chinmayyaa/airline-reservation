from pydantic import BaseModel


class Seat(BaseModel):
    seatId: str
    flightId: str
    seatNumber: str
    status: str