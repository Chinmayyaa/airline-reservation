from pydantic import BaseModel


class CancellationRequest(BaseModel):
    pnr: str


class CancellationResponse(BaseModel):
    pnr: str
    status: str
    message: str


class WaitlistRequest(BaseModel):
    pnr: str
    passenger_name: str
    flight_id: str


class WaitlistResponse(BaseModel):
    pnr: str
    status: str
    message: str