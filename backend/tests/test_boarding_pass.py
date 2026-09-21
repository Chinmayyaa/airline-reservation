from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.checkin import generate_boarding_pass


def test_generate_boarding_pass_success():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "from": "Bangalore",
        "to": "Delhi",
        "travel_date": "2026-09-20",
        "seat_number": "12A",
        "check_in_status": "checked_in",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        result = generate_boarding_pass("ABC123")

    assert result["message"] == "Boarding pass generated"

    boarding_pass = result["boarding_pass"]

    assert boarding_pass["pnr"] == "ABC123"
    assert boarding_pass["passenger_name"] == "Harini"
    assert boarding_pass["flight_number"] == "AI101"
    assert boarding_pass["from"] == "Bangalore"
    assert boarding_pass["to"] == "Delhi"
    assert boarding_pass["travel_date"] == "2026-09-20"
    assert boarding_pass["seat_number"] == "12A"
    assert boarding_pass["boarding_status"] == "READY"


def test_generate_boarding_pass_pnr_case_insensitive():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "from": "Bangalore",
        "to": "Delhi",
        "travel_date": "2026-09-20",
        "seat_number": "12A",
        "check_in_status": "checked_in",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        result = generate_boarding_pass("abc123")

    assert result["boarding_pass"]["pnr"] == "ABC123"

    mock_db.bookings.find_one.assert_called_once_with(
        {"pnr": "ABC123"},
        {"_id": 0}
    )


def test_generate_boarding_pass_booking_not_found():
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc_info:
            generate_boarding_pass("INVALID")

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Booking not found"


def test_generate_boarding_pass_without_checkin():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "from": "Bangalore",
        "to": "Delhi",
        "travel_date": "2026-09-20",
        "seat_number": "12A",
        "check_in_status": "not_checked_in",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc_info:
            generate_boarding_pass("ABC123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Passenger must complete check-in first"
    )


def test_generate_boarding_pass_missing_checkin_status():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "seat_number": "12A",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc_info:
            generate_boarding_pass("ABC123")

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == (
        "Passenger must complete check-in first"
    )