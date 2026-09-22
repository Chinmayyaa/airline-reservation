from fastapi import APIRouter, HTTPException

from app.booking.schemas import (
    BookingCreate,
    BookingResponse,
    SeatLockRequest,
    SeatLockResponse,
)
from app.booking.service import (
    lock_seat,
    create_booking,
    get_booking_by_pnr,
)


router = APIRouter(
    prefix="/api",
    tags=["Booking"]
)


@router.post("/seats/lock", response_model=SeatLockResponse)
def lock_seat_endpoint(request: SeatLockRequest):
    result = lock_seat(
        request.flight_id,
        request.seat_number
    )

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Seat is not available"
        )

    return result


@router.post("/bookings", response_model=BookingResponse)
def create_booking_endpoint(request: BookingCreate):
    result = create_booking(
        request.flight_id,
        request.passenger_name,
        request.passenger_email,
        request.passenger_phone,
        request.seat_number,
        request.lock_id
    )

    if result is None:
        raise HTTPException(
            status_code=409,
            detail="Seat lock is invalid or has expired"
        )

    return result


@router.get("/bookings/{pnr}", response_model=BookingResponse)
def get_booking_endpoint(pnr: str):
    booking = get_booking_by_pnr(pnr)

    if booking is None:
        raise HTTPException(
            status_code=404,
            detail="Booking not found"
        )

    return booking