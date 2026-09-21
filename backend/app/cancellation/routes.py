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


# -----------------------------
# CANCEL BOOKING
# -----------------------------

@router.post("/cancel", response_model=CancellationResponse)
async def cancel(request: CancellationRequest):
    return await cancel_booking(request.pnr)


# -----------------------------
# ADD TO WAITLIST
# -----------------------------

@router.post("/waitlist", response_model=WaitlistResponse)
async def waitlist(request: WaitlistRequest):
    return await add_to_waitlist(
        request.pnr,
        request.passenger_name,
        request.flight_id
    )


# -----------------------------
# VIEW WAITLIST
# -----------------------------

@router.get("/waitlist/{flight_id}")
async def get_flight_waitlist(flight_id: str):
    return await get_waitlist(flight_id)