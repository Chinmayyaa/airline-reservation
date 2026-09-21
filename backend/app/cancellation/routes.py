from fastapi import APIRouter

from .schemas import (
    CancellationRequest,
    CancellationResponse,
    WaitlistRequest,
    WaitlistResponse,
)

from .service import (
    cancel_booking,
    add_to_waitlist,
    get_waitlist,
)


router = APIRouter(
    prefix="/api/cancellation",
    tags=["Cancellation & Waitlist"]
)


@router.post("/cancel", response_model=CancellationResponse)
def cancel(request: CancellationRequest):
    return cancel_booking(request.pnr)


@router.post("/waitlist", response_model=WaitlistResponse)
def waitlist(request: WaitlistRequest):
    return add_to_waitlist(
        request.pnr,
        request.passenger_name,
        request.flight_id
    )


@router.get("/waitlist/{flight_id}")
def get_flight_waitlist(flight_id: str):
    return get_waitlist(flight_id)