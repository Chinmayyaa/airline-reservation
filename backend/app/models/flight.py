from pydantic import BaseModel
from typing import Optional


class Flight(BaseModel):
    flightId: str
    flightNumber: str
    source: str
    destination: str
    date: str
    departureTime: str
    arrivalTime: str
    capacity: int