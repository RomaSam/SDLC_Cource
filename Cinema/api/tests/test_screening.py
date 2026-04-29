"""
Tests for the Screening dataclass (domain/screening.py).

The dataclass has no I/O, no validation, and no framework dependencies —
all behaviour is fully deterministic from the Python dataclass machinery.

Run from repo root:
    py -m pytest Cinema/api/tests/test_screening.py -v
"""

from domain.screening import Screening


# ── Constants ──────────────────────────────────────────────────────────────────

NAME = "Inception"
GENRE = "Sci-Fi"
DURATION = 148
DATE = "2026-05-01"
BEGINS_AT = "20:00"
HALL = "Hall A"
SEATS = 150
SCREENING_ID = 42


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_required_only() -> Screening:
    """Return a Screening populated with only the mandatory fields."""
    return Screening(
        name=NAME,
        duration_minutes=DURATION,
        screening_date=DATE,
        begins_at=BEGINS_AT,
        hall=HALL,
        seats=SEATS,
    )


def _make_full() -> Screening:
    """Return a Screening with every field supplied."""
    return Screening(
        name=NAME,
        genre=GENRE,
        duration_minutes=DURATION,
        screening_date=DATE,
        begins_at=BEGINS_AT,
        hall=HALL,
        seats=SEATS,
        id=SCREENING_ID,
    )


# ── Instantiation ──────────────────────────────────────────────────────────────

class TestInstantiation:

    def test_all_fields_are_stored_correctly(self):
        """All supplied field values are accessible on the instance."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert s.name == NAME
        assert s.genre == GENRE
        assert s.duration_minutes == DURATION
        assert s.screening_date == DATE
        assert s.begins_at == BEGINS_AT
        assert s.hall == HALL
        assert s.seats == SEATS
        assert s.id == SCREENING_ID

    def test_required_fields_only_leaves_optional_fields_as_none(self):
        """genre and id default to None when omitted."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert s.genre is None, "genre should default to None"
        assert s.id is None, "id should default to None"

    def test_required_fields_are_stored_correctly(self):
        """The six mandatory fields are stored without alteration."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert s.name == NAME
        assert s.duration_minutes == DURATION
        assert s.screening_date == DATE
        assert s.begins_at == BEGINS_AT
        assert s.hall == HALL
        assert s.seats == SEATS

    def test_genre_none_is_explicit_default(self):
        """Passing genre=None explicitly gives the same result as omitting it."""
        # Arrange / Act
        s_omitted = _make_required_only()
        s_explicit = Screening(
            name=NAME,
            duration_minutes=DURATION,
            screening_date=DATE,
            begins_at=BEGINS_AT,
            hall=HALL,
            seats=SEATS,
            genre=None,
        )

        # Assert
        assert s_omitted.genre is None
        assert s_explicit.genre is None

    def test_id_none_is_explicit_default(self):
        """Passing id=None explicitly gives the same result as omitting it."""
        # Arrange / Act
        s_omitted = _make_required_only()
        s_explicit = Screening(
            name=NAME,
            duration_minutes=DURATION,
            screening_date=DATE,
            begins_at=BEGINS_AT,
            hall=HALL,
            seats=SEATS,
            id=None,
        )

        # Assert
        assert s_omitted.id is None
        assert s_explicit.id is None


# ── Type preservation ──────────────────────────────────────────────────────────

class TestTypePreservation:
    """Dataclasses perform no type coercion — stored values keep their original type."""

    def test_name_stored_as_str(self):
        """name field retains str type."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.name, str)

    def test_duration_minutes_stored_as_int(self):
        """duration_minutes field retains int type."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.duration_minutes, int)

    def test_screening_date_stored_as_str(self):
        """screening_date field retains str type (not parsed to date)."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.screening_date, str)

    def test_begins_at_stored_as_str(self):
        """begins_at field retains str type (not parsed to time)."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.begins_at, str)

    def test_hall_stored_as_str(self):
        """hall field retains str type."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.hall, str)

    def test_seats_stored_as_int(self):
        """seats field retains int type."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert isinstance(s.seats, int)

    def test_genre_stored_as_str_when_provided(self):
        """genre field retains str type when a value is supplied."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert isinstance(s.genre, str)

    def test_id_stored_as_int_when_provided(self):
        """id field retains int type when a value is supplied."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert isinstance(s.id, int)

    def test_no_coercion_of_float_duration(self):
        """A float passed for duration_minutes is stored as-is, not cast to int."""
        # Arrange / Act
        s = Screening(
            name=NAME,
            duration_minutes=148.9,  # type: ignore[arg-type]
            screening_date=DATE,
            begins_at=BEGINS_AT,
            hall=HALL,
            seats=SEATS,
        )

        # Assert — dataclasses do not coerce, so the float is preserved
        assert s.duration_minutes == 148.9
        assert isinstance(s.duration_minutes, float)


# ── Equality ───────────────────────────────────────────────────────────────────

class TestEquality:

    def test_two_instances_with_same_fields_are_equal(self):
        """Two Screening instances built from identical field values compare equal."""
        # Arrange
        s1 = _make_full()
        s2 = _make_full()

        # Act / Assert
        assert s1 == s2

    def test_instances_with_different_name_are_not_equal(self):
        """Screenings with differing name are not equal."""
        # Arrange
        s1 = _make_full()
        s2 = Screening(
            name="Interstellar",
            genre=GENRE,
            duration_minutes=DURATION,
            screening_date=DATE,
            begins_at=BEGINS_AT,
            hall=HALL,
            seats=SEATS,
            id=SCREENING_ID,
        )

        # Act / Assert
        assert s1 != s2

    def test_instances_with_different_id_are_not_equal(self):
        """Screenings with differing id are not equal even if all other fields match."""
        # Arrange
        s1 = _make_full()
        s2 = Screening(
            name=NAME,
            genre=GENRE,
            duration_minutes=DURATION,
            screening_date=DATE,
            begins_at=BEGINS_AT,
            hall=HALL,
            seats=SEATS,
            id=SCREENING_ID + 1,
        )

        # Act / Assert
        assert s1 != s2

    def test_instance_with_genre_not_equal_to_instance_without_genre(self):
        """A Screening with genre set is not equal to one where genre is None."""
        # Arrange
        s_with_genre = _make_full()
        s_no_genre = _make_required_only()
        # Ensure id also matches so genre is the only difference
        s_no_genre.id = SCREENING_ID

        # Act / Assert
        assert s_with_genre != s_no_genre

    def test_screening_is_not_equal_to_none(self):
        """A Screening instance is never equal to None."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert s != None  # noqa: E711  (intentional identity check against None)

    def test_screening_is_not_equal_to_dict(self):
        """A Screening instance is not equal to a plain dict with the same data."""
        # Arrange
        s = _make_full()
        d = {
            "name": NAME,
            "genre": GENRE,
            "duration_minutes": DURATION,
            "screening_date": DATE,
            "begins_at": BEGINS_AT,
            "hall": HALL,
            "seats": SEATS,
            "id": SCREENING_ID,
        }

        # Act / Assert
        assert s != d


# ── Mutability ────────────────────────────────────────────────────────────────

class TestMutability:

    def test_name_can_be_reassigned(self):
        """name field is mutable after construction."""
        # Arrange
        s = _make_required_only()

        # Act
        s.name = "Dune"

        # Assert
        assert s.name == "Dune"

    def test_genre_can_be_set_from_none_to_string(self):
        """genre can be changed from None to a string after construction."""
        # Arrange
        s = _make_required_only()
        assert s.genre is None

        # Act
        s.genre = "Drama"

        # Assert
        assert s.genre == "Drama"

    def test_genre_can_be_cleared_to_none(self):
        """genre can be reset back to None after being set."""
        # Arrange
        s = _make_full()
        assert s.genre == GENRE

        # Act
        s.genre = None

        # Assert
        assert s.genre is None

    def test_id_can_be_set_after_construction(self):
        """id can be assigned after the instance is created (simulates DB insert)."""
        # Arrange
        s = _make_required_only()
        assert s.id is None

        # Act
        s.id = 7

        # Assert
        assert s.id == 7

    def test_seats_can_be_updated(self):
        """seats field is mutable after construction."""
        # Arrange
        s = _make_required_only()

        # Act
        s.seats = 200

        # Assert
        assert s.seats == 200

    def test_mutation_does_not_affect_other_instance(self):
        """Mutating one Screening instance does not affect a separately constructed one."""
        # Arrange
        s1 = _make_full()
        s2 = _make_full()

        # Act
        s1.name = "Changed"

        # Assert
        assert s2.name == NAME, "s2 must be unaffected by s1 mutation"


# ── Repr ──────────────────────────────────────────────────────────────────────

class TestRepr:

    def test_repr_contains_class_name(self):
        """repr() includes 'Screening' as the class name."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert "Screening" in repr(s)

    def test_repr_contains_name_value(self):
        """repr() includes the movie name."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert NAME in repr(s)

    def test_repr_contains_hall_value(self):
        """repr() includes the hall identifier."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert HALL in repr(s)

    def test_repr_contains_id_value(self):
        """repr() includes the id value when set."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert str(SCREENING_ID) in repr(s)

    def test_repr_shows_none_for_missing_id(self):
        """repr() shows id=None when id has not been assigned."""
        # Arrange / Act
        s = _make_required_only()

        # Assert
        assert "None" in repr(s)

    def test_repr_is_a_string(self):
        """repr() always returns a str."""
        # Arrange / Act
        s = _make_full()

        # Assert
        assert isinstance(repr(s), str)
