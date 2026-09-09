from fastapi import FastAPI

app = FastAPI(title="Airline Reservation System")


@app.get("/")
def root():
    return {"message": "Airline Reservation API is running"}