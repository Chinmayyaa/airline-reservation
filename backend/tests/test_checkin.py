from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.checkin import (
    CheckInRequest,
    checkin_health,
    get_booking_for_checkin,
    check_in,
    generate_boarding_pass,
)


# --------------------------------------------------
# Health check
# --------------------------------------------------

def test_checkin_health():
    result = checkin_health()

    assert result["message"] == "Check-in module is working"


# --------------------------------------------------
# PNR / Booking lookup
# --------------------------------------------------

def test_get_booking_for_checkin_success():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "status": "confirmed",
        "seat_number": "12A",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        result = get_booking_for_checkin("ABC123")

    assert result["message"] == "Booking found"
    assert result["booking"] == mock_booking


def test_get_booking_for_checkin_invalid_pnr():
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            get_booking_for_checkin("INVALID")

    assert exc.value.status_code == 404


# --------------------------------------------------
# Check-in
# --------------------------------------------------

def test_check_in_success():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "status": "confirmed",
        "seat_number": "12A",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        result = check_in(CheckInRequest(pnr="ABC123"))

    assert result["message"] == "Check-in successful"
    assert result["pnr"] == "ABC123"
    assert result["check_in_status"] == "checked_in"
    assert "check_in_time" in result

    mock_db.bookings.update_one.assert_called_once()


def test_check_in_booking_not_found():
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            check_in(CheckInRequest(pnr="INVALID"))

    assert exc.value.status_code == 404


def test_check_in_already_checked_in():
    mock_booking = {
        "pnr": "ABC123",
        "status": "confirmed",
        "check_in_status": "checked_in",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            check_in(CheckInRequest(pnr="ABC123"))

    assert exc.value.status_code == 400


def test_check_in_unconfirmed_booking():
    mock_booking = {
        "pnr": "ABC123",
        "status": "cancelled",
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            check_in(CheckInRequest(pnr="ABC123"))

    assert exc.value.status_code == 400


# --------------------------------------------------
# Boarding Pass
# --------------------------------------------------

def test_generate_boarding_pass_success():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "from": "Bangalore",
        "to": "Delhi",
        "travel_date": "2026-10-01",
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
    assert boarding_pass["seat_number"] == "12A"
    assert boarding_pass["boarding_status"] == "READY"


def test_generate_boarding_pass_before_checkin():
    mock_booking = {
        "pnr": "ABC123",
        "passenger_name": "Harini",
        "flight_number": "AI101",
        "check_in_status": None,
    }

    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = mock_booking

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            generate_boarding_pass("ABC123")

    assert exc.value.status_code == 400


def test_generate_boarding_pass_booking_not_found():
    mock_db = MagicMock()
    mock_db.bookings.find_one.return_value = None

    with patch("app.checkin.db", mock_db):
        with pytest.raises(HTTPException) as exc:
            generate_boarding_pass("INVALID")

    assert exc.value.status_code == 404