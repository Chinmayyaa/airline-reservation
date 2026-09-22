from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SeatLockRequest(BaseModel):
    flight_id: str
    seat_number: str


class SeatLockResponse(BaseModel):
    lock_id: str
    flight_id: str
    seat_number: str
    status: str
    expires_at: datetime


class BookingCreate(BaseModel):
    flight_id: str
    passenger_name: str = Field(min_length=2)
    passenger_email: str
    passenger_phone: str
    seat_number: str
    lock_id: str


class BookingResponse(BaseModel):
    pnr: str
    flight_id: str
    passenger_name: str
    passenger_email: str
    passenger_phone: str
    seat_number: str
    status: str
    created_at: datetime
    lock_expires_at: Optional[datetime] = None
    check_in_status: Optional[str] = None
    check_in_time: Optional[datetime] = None