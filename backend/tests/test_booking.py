from unittest.mock import MagicMock, patch

from app.booking.service import (
    lock_seat,
    create_booking,
    get_booking_by_pnr,
)


def test_lock_seat_success():
    mock_seat = {
        "flight_id": "AI101",
        "seat_number": "12A",
        "status": "LOCKED",
    }

    mock_db = MagicMock()
    mock_db.seats.find_one_and_update.return_value = mock_seat

    with patch("app.booking.service.db", mock_db):
        result = lock_seat("AI101", "12A")

    assert result is not None
    assert result["flight_id"] == "AI101"
    assert result["seat_number"] == "12A"
    assert result["status"] == "LOCKED"
    assert "lock_id" in result
    assert "expires_at" in result


def test_lock_seat_unavailable():
    mock_db = MagicMock()
    mock_db.seats.find_one_and_update.return_value = None

    with patch("app.booking.service.db", mock_db):
        result = lock_seat("AI101", "12A")

    assert result is None


def test_create_booking_success():
    mock_seat = {
        "flight_id": "AI101",
        "seat_number": "12B",
        "status": "LOCKED",
    }

    mock_db = MagicMock()
    mock_db.seats.find_one_and_update.return_value = mock_seat
    mock_db.bookings.find_one.return_value = None

    with patch("app.booking.service.db", mock_db):
        result = create_booking(
            "AI101",
            "Harini",
            "harini@example.com",
            "9876543210",
            "12B",
            "test-lock-id",
        )

    assert result is not None
    assert len(result["pnr"]) == 6
    assert result["flight_id"] == "AI101"
    assert result["seat_number"] == "12B"
    assert result["status"] == "CONFIRMED"
    mock_db.bookings.insert_one.assert_called_once()


def test_create_booking_invalid_lock():
    mock_db = MagicMock()
    mock_db.seats.find_one_and_update.return_value = None

    with patch("app.booking.service.db", mock_db):
        result = create_booking(
            "AI101",
            "Harini",
            "harini@example.com",
            "9876543210",
            "12B",
            "wrong-lock-id",
        )

    assert result is None


def test_get_booking_by_pnr():
    mock_booking = {
        "pnr": "ABC123",
        "flight_id": "AI101",
        "passenger_name": "Harini",
        "seat_number": "12A",
        "status": "CONFIRMED",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.booking.service.db", mock_db):
        result = get_booking_by_pnr("ABC123")

    assert result == mock_booking