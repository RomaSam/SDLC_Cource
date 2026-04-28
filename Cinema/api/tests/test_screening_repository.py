"""
Tests for SQLiteScreeningRepository.

Run from repo root:
    py -m pytest Cinema/api/tests/test_screening_repository.py -v

Fixtures are defined in conftest.py (same directory).
All tests use an in-memory SQLite database — cinema.db is never touched.
"""

from unittest.mock import patch

import pytest

from domain.screening import Screening
from infrastructure.screening_repository import SQLiteScreeningRepository

_PATCH_TARGET = "infrastructure.screening_repository.get_connection"


@pytest.fixture
def repo(make_connection):
    """SQLiteScreeningRepository wired to the in-memory test database."""
    with patch(_PATCH_TARGET, side_effect=make_connection):
        yield SQLiteScreeningRepository()


# ── Helpers ──────────────────────────────────────────────────────────────────

def _insert(repo: SQLiteScreeningRepository, screening: Screening) -> Screening:
    """Persist a screening and return the saved entity (with id assigned)."""
    return repo.create(screening)


# ── get_by_id ────────────────────────────────────────────────────────────────

class TestGetById:
    def test_returns_screening_when_id_exists(self, repo, sample_screening):
        """get_by_id returns the correct Screening for a known id."""
        # Arrange
        saved = _insert(repo, sample_screening)

        # Act
        result = repo.get_by_id(saved.id)

        # Assert
        assert result is not None
        assert result.id == saved.id
        assert result.name == sample_screening.name

    def test_returns_none_when_id_missing(self, repo):
        """get_by_id returns None for an id that does not exist."""
        # Arrange — database is empty

        # Act
        result = repo.get_by_id(9999)

        # Assert
        assert result is None


# ── list_all ─────────────────────────────────────────────────────────────────

class TestListAll:
    def test_returns_all_screenings_when_no_filters(self, repo, sample_screening):
        """list_all with no arguments returns every row in the table."""
        # Arrange
        _insert(repo, sample_screening)
        _insert(repo, sample_screening)

        # Act
        results = repo.list_all()

        # Assert
        assert len(results) == 2

    def test_returns_empty_list_when_table_is_empty(self, repo):
        """list_all returns [] when no screenings exist."""
        # Act
        results = repo.list_all()

        # Assert
        assert results == []

    def test_filters_by_genre(self, repo, sample_screening):
        """list_all(genre=...) returns only screenings matching that genre."""
        # Arrange
        _insert(repo, sample_screening)  # genre="Sci-Fi"
        other = Screening(
            name="Parasite",
            genre="Thriller",
            duration_minutes=132,
            screening_date="2026-05-01",
            begins_at="18:00",
            hall="Hall B",
            seats=120,
        )
        _insert(repo, other)

        # Act
        results = repo.list_all(genre="Sci-Fi")

        # Assert
        assert len(results) == 1
        assert results[0].genre == "Sci-Fi"

    def test_filters_by_date(self, repo, sample_screening):
        """list_all(date=...) returns only screenings on that date."""
        # Arrange
        _insert(repo, sample_screening)  # screening_date="2026-05-01"
        other = Screening(
            name="Parasite",
            genre="Thriller",
            duration_minutes=132,
            screening_date="2026-05-02",
            begins_at="18:00",
            hall="Hall B",
            seats=120,
        )
        _insert(repo, other)

        # Act
        results = repo.list_all(date="2026-05-01")

        # Assert
        assert len(results) == 1
        assert results[0].screening_date == "2026-05-01"

    def test_filters_by_hall(self, repo, sample_screening):
        """list_all(hall=...) returns only screenings in that hall."""
        # Arrange
        _insert(repo, sample_screening)  # hall="Hall A"
        other = Screening(
            name="Parasite",
            genre="Thriller",
            duration_minutes=132,
            screening_date="2026-05-01",
            begins_at="18:00",
            hall="Hall B",
            seats=120,
        )
        _insert(repo, other)

        # Act
        results = repo.list_all(hall="Hall A")

        # Assert
        assert len(results) == 1
        assert results[0].hall == "Hall A"

    def test_filters_combined(self, repo, sample_screening):
        """list_all with multiple filters applies all conditions (AND)."""
        # Arrange
        _insert(repo, sample_screening)  # genre="Sci-Fi", hall="Hall A"

        # Act — genre matches but hall does not
        results = repo.list_all(genre="Sci-Fi", hall="Hall Z")

        # Assert
        assert results == []


# ── create ───────────────────────────────────────────────────────────────────

class TestCreate:
    def test_returns_screening_with_assigned_id(self, repo, sample_screening):
        """create persists the record and returns it with a non-None id."""
        # Act
        result = repo.create(sample_screening)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, int)

    def test_persisted_data_matches_input(self, repo, sample_screening):
        """Fields in the returned Screening match those of the input."""
        # Act
        result = repo.create(sample_screening)

        # Assert
        assert result.name == sample_screening.name
        assert result.genre == sample_screening.genre
        assert result.duration_minutes == sample_screening.duration_minutes
        assert result.screening_date == sample_screening.screening_date
        assert result.begins_at == sample_screening.begins_at
        assert result.hall == sample_screening.hall
        assert result.seats == sample_screening.seats

    def test_nullable_genre_is_stored_as_none(self, repo):
        """create with genre=None stores NULL and returns genre=None."""
        # Arrange
        screening = Screening(
            name="No Genre Film",
            genre=None,
            duration_minutes=90,
            screening_date="2026-05-01",
            begins_at="12:00",
            hall="Hall C",
            seats=80,
        )

        # Act
        result = repo.create(screening)

        # Assert
        assert result.genre is None


# ── replace ──────────────────────────────────────────────────────────────────

class TestReplace:
    def test_replaces_all_fields_for_existing_id(self, repo, sample_screening):
        """replace overwrites every column for the given id."""
        # Arrange
        saved = _insert(repo, sample_screening)
        updated = Screening(
            name="Replaced Title",
            genre="Action",
            duration_minutes=99,
            screening_date="2026-06-01",
            begins_at="10:00",
            hall="Hall C",
            seats=200,
        )

        # Act
        result = repo.replace(saved.id, updated)

        # Assert
        assert result is not None
        assert result.id == saved.id
        assert result.name == "Replaced Title"
        assert result.genre == "Action"

    def test_returns_none_for_missing_id(self, repo, sample_screening):
        """replace returns None when the target id does not exist."""
        # Act
        result = repo.replace(9999, sample_screening)

        # Assert
        assert result is None


# ── patch ────────────────────────────────────────────────────────────────────

class TestPatch:
    def test_updates_only_provided_fields(self, repo, sample_screening):
        """patch changes only the supplied fields, leaving others unchanged."""
        # Arrange
        saved = _insert(repo, sample_screening)

        # Act
        result = repo.patch(saved.id, {"name": "Patched Title"})

        # Assert
        assert result is not None
        assert result.name == "Patched Title"
        assert result.genre == sample_screening.genre  # unchanged

    def test_returns_current_state_for_empty_data(self, repo, sample_screening):
        """patch with an empty dict is a no-op and returns the current record."""
        # Arrange
        saved = _insert(repo, sample_screening)

        # Act
        result = repo.patch(saved.id, {})

        # Assert
        assert result is not None
        assert result.id == saved.id

    def test_ignores_unknown_columns(self, repo, sample_screening):
        """patch silently drops keys not in the column whitelist."""
        # Arrange
        saved = _insert(repo, sample_screening)

        # Act — "malicious_col" is not in _PATCH_COLUMNS
        result = repo.patch(saved.id, {"malicious_col": "DROP TABLE screening"})

        # Assert
        assert result is not None  # no error raised, row unchanged

    def test_returns_none_for_missing_id(self, repo):
        """patch returns None when the target id does not exist."""
        # Act
        result = repo.patch(9999, {"name": "Ghost"})

        # Assert
        assert result is None


# ── delete ───────────────────────────────────────────────────────────────────

class TestDelete:
    def test_returns_true_and_removes_record(self, repo, sample_screening):
        """delete removes the row and returns True."""
        # Arrange
        saved = _insert(repo, sample_screening)

        # Act
        deleted = repo.delete(saved.id)

        # Assert
        assert deleted is True
        assert repo.get_by_id(saved.id) is None

    def test_returns_false_for_missing_id(self, repo):
        """delete returns False when the id does not exist."""
        # Act
        result = repo.delete(9999)

        # Assert
        assert result is False
