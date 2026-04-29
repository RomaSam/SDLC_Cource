"""
Tests for CreateScreeningRequest and PatchScreeningRequest Pydantic schemas.

Run from repo root:
    py -m pytest Cinema/api/tests/test_screening_request.py -v
"""

import pytest
from pydantic import ValidationError

from interfaces.schemas.screening_request import (
    CreateScreeningRequest,
    PatchScreeningRequest,
)


# ── CreateScreeningRequest ────────────────────────────────────────────────────

class TestCreateScreeningRequest:

    def test_valid_payload_is_accepted(self):
        # Arrange
        payload = {
            "name": "Inception",
            "genre": "Sci-Fi",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act
        req = CreateScreeningRequest(**payload)
        # Assert
        assert req.name == "Inception"
        assert req.genre == "Sci-Fi"
        assert req.duration_minutes == 148
        assert req.screening_date == "2026-05-01"
        assert req.begins_at == "20:00"
        assert req.hall == "Hall A"
        assert req.seats == 150

    def test_genre_is_optional(self):
        # Arrange
        payload = {
            "name": "Inception",
            "genre": None,
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act
        req = CreateScreeningRequest(**payload)
        # Assert
        assert req.genre is None

    def test_name_cannot_be_empty(self):
        # Arrange
        payload = {
            "name": "",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    def test_duration_minutes_must_be_positive(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 0,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    def test_duration_minutes_cannot_exceed_maximum(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 601,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    def test_seats_must_be_positive(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 0,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    # ── validate_date ─────────────────────────────────────────────────────────

    def test_screening_date_accepts_valid_iso_date(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act
        req = CreateScreeningRequest(**payload)
        # Assert
        assert req.screening_date == "2026-05-01"

    def test_screening_date_rejects_invalid_format(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "01-05-2026",  # wrong order
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    def test_screening_date_rejects_impossible_date(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-02-30",  # Feb 30 doesn't exist
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    # ── validate_time ─────────────────────────────────────────────────────────

    def test_begins_at_accepts_valid_hhmm_time(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "09:05",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act
        req = CreateScreeningRequest(**payload)
        # Assert
        assert req.begins_at == "09:05"

    def test_begins_at_rejects_invalid_time_format(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "9:5",  # missing leading zeros
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)

    def test_begins_at_rejects_impossible_time(self):
        # Arrange
        payload = {
            "name": "Inception",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "25:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act / Assert
        with pytest.raises(ValidationError):
            CreateScreeningRequest(**payload)


# ── PatchScreeningRequest ─────────────────────────────────────────────────────

class TestPatchScreeningRequest:

    def test_single_field_is_accepted(self):
        # Arrange / Act
        req = PatchScreeningRequest(name="Interstellar")
        # Assert
        assert req.name == "Interstellar"
        assert req.genre is None
        assert req.duration_minutes is None
        assert req.screening_date is None
        assert req.begins_at is None
        assert req.hall is None
        assert req.seats is None

    def test_all_fields_may_be_provided(self):
        # Arrange
        payload = {
            "name": "Inception",
            "genre": "Sci-Fi",
            "duration_minutes": 148,
            "screening_date": "2026-05-01",
            "begins_at": "20:00",
            "hall": "Hall A",
            "seats": 150,
        }
        # Act
        req = PatchScreeningRequest(**payload)
        # Assert
        assert req.name == "Inception"
        assert req.genre == "Sci-Fi"
        assert req.duration_minutes == 148
        assert req.screening_date == "2026-05-01"
        assert req.begins_at == "20:00"
        assert req.hall == "Hall A"
        assert req.seats == 150

    def test_empty_body_is_rejected(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            PatchScreeningRequest()

    def test_name_cannot_be_empty_string(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            PatchScreeningRequest(name="")

    def test_invalid_date_is_rejected(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            PatchScreeningRequest(screening_date="not-a-date")

    def test_invalid_time_is_rejected(self):
        # Arrange / Act / Assert
        with pytest.raises(ValidationError):
            PatchScreeningRequest(begins_at="99:99")

    def test_none_values_are_preserved_as_none(self):
        # Arrange / Act
        req = PatchScreeningRequest(hall="Hall B")
        # Assert
        assert req.name is None
        assert req.hall == "Hall B"
