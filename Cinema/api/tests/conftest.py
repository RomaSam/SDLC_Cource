import sqlite3
import sys
from pathlib import Path

import pytest

# Add Cinema/api to sys.path so absolute imports (domain, infrastructure, …) resolve
sys.path.insert(0, str(Path(__file__).parents[1]))

SCHEMA_PATH = Path(__file__).parents[2] / "db" / "schema.sql"

# A named shared-cache URI lets every connection returned by make_connection()
# point at the same in-memory database while still being closeable individually.
_SHARED_URI = "file:cinema_test?mode=memory&cache=shared"


def _make_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(_SHARED_URI, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@pytest.fixture
def db():
    """Fresh shared in-memory database with schema applied, torn down after each test."""
    conn = _make_conn()
    conn.executescript(SCHEMA_PATH.read_text())
    conn.commit()
    yield conn
    conn.execute("DELETE FROM screening")
    conn.commit()
    conn.close()


@pytest.fixture
def make_connection(db):  # db fixture ensures schema exists before any test connection
    """Drop-in replacement for infrastructure.db.get_connection used in tests."""
    return _make_conn


@pytest.fixture
def sample_screening():
    """A minimal valid Screening instance (no id — not yet persisted)."""
    from domain.screening import Screening

    return Screening(
        name="Inception",
        genre="Sci-Fi",
        duration_minutes=148,
        screening_date="2026-05-01",
        begins_at="20:00",
        hall="Hall A",
        seats=150,
    )
