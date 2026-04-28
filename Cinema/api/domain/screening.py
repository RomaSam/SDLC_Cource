from dataclasses import dataclass


@dataclass
class Screening:
    name: str
    duration_minutes: int
    screening_date: str   # ISO 8601: YYYY-MM-DD
    begins_at: str        # HH:MM
    hall: str
    seats: int
    genre: str | None = None
    id: int | None = None
