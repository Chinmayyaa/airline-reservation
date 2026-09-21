import pytest
from mongomock_motor import AsyncMongoMockClient

from app.cancellation import service


@pytest.fixture
def mock_db():
    client = AsyncMongoMockClient()
    return client["test_airline"]


@pytest.mark.asyncio
async def test_add_to_waitlist(mock_db):
    service.db = mock_db

    result = await service.add_to_waitlist(
        "WL001",
        "Rahul",
        "FL001"
    )

    assert result["status"] == "WAITING"
    assert result["pnr"] == "WL001"


@pytest.mark.asyncio
async def test_booking_not_found(mock_db):
    service.db = mock_db

    result = await service.cancel_booking("ABC123")

    assert result["status"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_successful_cancellation(mock_db):
    service.db = mock_db

    await mock_db.bookings.insert_one({
        "pnr": "ABC123",
        "flight_id": "FL001",
        "seat": "12A",
        "status": "CONFIRMED"
    })

    result = await service.cancel_booking("ABC123")

    assert result["status"] == "CANCELLED"

    booking = await mock_db.bookings.find_one({
        "pnr": "ABC123"
    })

    assert booking["status"] == "CANCELLED"
    assert booking["seat"] is None


@pytest.mark.asyncio
async def test_already_cancelled(mock_db):
    service.db = mock_db

    await mock_db.bookings.insert_one({
        "pnr": "ABC123",
        "flight_id": "FL001",
        "seat": "12A",
        "status": "CANCELLED"
    })

    result = await service.cancel_booking("ABC123")

    assert result["status"] == "ALREADY_CANCELLED"


@pytest.mark.asyncio
async def test_waitlist_promotion(mock_db):
    service.db = mock_db

    await mock_db.bookings.insert_one({
        "pnr": "ABC123",
        "flight_id": "FL001",
        "seat": "12A",
        "status": "CONFIRMED"
    })

    await service.add_to_waitlist(
        "WL001",
        "Rahul",
        "FL001"
    )

    result = await service.cancel_booking("ABC123")

    assert result["status"] == "CANCELLED"

    waitlisted = await mock_db.waitlist.find_one({
        "pnr": "WL001"
    })

    assert waitlisted["status"] == "CONFIRMED"
    assert waitlisted["seat"] == "12A"