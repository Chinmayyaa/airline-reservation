from fastapi import FastAPI

from app.cancellation.routes import router as cancellation_router


app = FastAPI(
    title="Airline Reservation System"
)

app.include_router(cancellation_router)


@app.get("/")
async def root():
    return {
        "message": "Airline Reservation Backend Running"
    }