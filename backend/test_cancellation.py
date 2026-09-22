from unittest.mock import MagicMock, patch

from app.cancellation.service import (
    add_to_waitlist,
    cancel_booking,
    get_waitlist,
    promote_next_waitlisted,
)


def test_cancel_booking_not_found():
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.cancellation.service.db", mock_db):
        result = cancel_booking("ABC123")

    assert result["status"] == "NOT_FOUND"


def test_cancel_booking_already_cancelled():
    mock_db = MagicMock()

    mock_db.bookings.find_one.return_value = {
        "pnr": "ABC123",
        "status": "CANCELLED",
        "seat_number": "12A",
        "flight_id": "AI101",
    }

    with patch("app.cancellation.service.db", mock_db):
        result = cancel_booking("ABC123")

    assert result["status"] == "ALREADY_CANCELLED"


def test_cancel_booking_success():
    mock_db = MagicMock()

    mock_db.bookings.find_one.return_value = {
        "pnr": "ABC123",
        "status": "CONFIRMED",
        "seat_number": "12A",
        "flight_id": "AI101",
    }

    mock_db.waitlist.find_one.return_value = None

    with patch("app.cancellation.service.db", mock_db):
        result = cancel_booking("ABC123")

    assert result["status"] == "CANCELLED"

    mock_db.bookings.update_one.assert_called_once()
    mock_db.seats.update_one.assert_called_once()


def test_add_to_waitlist():
    mock_db = MagicMock()

    mock_db.waitlist.find_one.return_value = None

    with patch("app.cancellation.service.db", mock_db):
        result = add_to_waitlist(
            "WL001",
            "Rahul",
            "AI101"
        )

    assert result["status"] == "WAITING"
    assert result["pnr"] == "WL001"
    assert "position" in result["message"]

    mock_db.waitlist.insert_one.assert_called_once()


def test_add_duplicate_to_waitlist():
    mock_db = MagicMock()

    mock_db.waitlist.find_one.return_value = {
        "pnr": "WL001",
        "status": "WAITING"
    }

    with patch("app.cancellation.service.db", mock_db):
        result = add_to_waitlist(
            "WL001",
            "Rahul",
            "AI101"
        )

    assert result["status"] == "ALREADY_WAITLISTED"