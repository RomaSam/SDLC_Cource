from __future__ import annotations
from pydantic import BaseModel
from domain.screening import Screening


class ScreeningResponse(BaseModel):
    id: int
    name: str
    genre: str | None
    duration_minutes: int
    screening_date: str
    begins_at: str
    hall: str
    seats: int

    @classmethod
    def from_entity(cls, s: Screening) -> ScreeningResponse:
        if s.id is None:
            raise ValueError("Cannot serialize an unpersisted Screening (id is None)")
        return cls(
            id=s.id,
            name=s.name,
            genre=s.genre,
            duration_minutes=s.duration_minutes,
            screening_date=s.screening_date,
            begins_at=s.begins_at,
            hall=s.hall,
            seats=s.seats,
        )
