import sqlite3
from abc import ABC, abstractmethod
from contextlib import closing
from domain.screening import Screening
from infrastructure.db import get_connection

_PATCH_COLUMNS = frozenset(
    {"name", "genre", "duration_minutes", "screening_date", "begins_at", "hall", "seats"}
)

# ── Abstract interface ──────────────────────────────────────────────────────

class IScreeningRepository(ABC):
    @abstractmethod
    def get_by_id(self, screening_id: int) -> Screening | None: ...

    @abstractmethod
    def list_all(
        self,
        genre: str | None,
        date: str | None,
        hall: str | None,
    ) -> list[Screening]: ...

    @abstractmethod
    def create(self, screening: Screening) -> Screening: ...

    @abstractmethod
    def replace(self, screening_id: int, screening: Screening) -> Screening | None: ...

    @abstractmethod
    def patch(self, screening_id: int, data: dict) -> Screening | None: ...

    @abstractmethod
    def delete(self, screening_id: int) -> bool: ...


# ── Helpers ─────────────────────────────────────────────────────────────────

def _row_to_entity(row: sqlite3.Row) -> Screening:
    return Screening(
        id=row["id"],
        name=row["name"],
        genre=row["genre"],
        duration_minutes=row["duration_minutes"],
        screening_date=row["screening_date"],
        begins_at=row["begins_at"],
        hall=row["hall"],
        seats=row["seats"],
    )


# ── SQLite implementation ───────────────────────────────────────────────────

class SQLiteScreeningRepository(IScreeningRepository):

    def get_by_id(self, screening_id: int) -> Screening | None:
        with closing(get_connection()) as conn:
            with conn:
                row = conn.execute(
                    "SELECT * FROM screening WHERE id = ?", (screening_id,)
                ).fetchone()
        return _row_to_entity(row) if row else None

    def list_all(
        self,
        genre: str | None = None,
        date: str | None = None,
        hall: str | None = None,
    ) -> list[Screening]:
        # Column names in WHERE come from this method's own code, not from user input.
        filters: list[str] = []
        params: list[object] = []
        if genre:
            filters.append("genre = ?")
            params.append(genre)
        if date:
            filters.append("screening_date = ?")
            params.append(date)
        if hall:
            filters.append("hall = ?")
            params.append(hall)
        where = ("WHERE " + " AND ".join(filters)) if filters else ""
        with closing(get_connection()) as conn:
            with conn:
                rows = conn.execute(
                    f"SELECT * FROM screening {where}", params
                ).fetchall()
        return [_row_to_entity(r) for r in rows]

    def create(self, screening: Screening) -> Screening:
        with closing(get_connection()) as conn:
            with conn:
                cur = conn.execute(
                    "INSERT INTO screening"
                    " (name, genre, duration_minutes, screening_date, begins_at, hall, seats)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        screening.name, screening.genre, screening.duration_minutes,
                        screening.screening_date, screening.begins_at,
                        screening.hall, screening.seats,
                    ),
                )
                row = conn.execute(
                    "SELECT * FROM screening WHERE id = ?", (cur.lastrowid,)
                ).fetchone()
        return _row_to_entity(row)

    def replace(self, screening_id: int, screening: Screening) -> Screening | None:
        with closing(get_connection()) as conn:
            with conn:
                cur = conn.execute(
                    "UPDATE screening"
                    " SET name=?, genre=?, duration_minutes=?, screening_date=?, begins_at=?, hall=?, seats=?"
                    " WHERE id=?",
                    (
                        screening.name, screening.genre, screening.duration_minutes,
                        screening.screening_date, screening.begins_at,
                        screening.hall, screening.seats, screening_id,
                    ),
                )
                if cur.rowcount == 0:
                    return None
                row = conn.execute(
                    "SELECT * FROM screening WHERE id = ?", (screening_id,)
                ).fetchone()
        return _row_to_entity(row)

    def patch(self, screening_id: int, data: dict) -> Screening | None:
        # If data is empty or all keys fail the whitelist, return current state unchanged (no-op, 200 OK).
        safe = {k: v for k, v in data.items() if k in _PATCH_COLUMNS}
        if not safe:
            return self.get_by_id(screening_id)
        # Whitelist ensures only known column names appear in the SET clause.
        sets = ", ".join(f"{col} = ?" for col in safe)
        params: list[object] = list(safe.values()) + [screening_id]
        with closing(get_connection()) as conn:
            with conn:
                cur = conn.execute(
                    f"UPDATE screening SET {sets} WHERE id = ?", params
                )
                if cur.rowcount == 0:
                    return None
                row = conn.execute(
                    "SELECT * FROM screening WHERE id = ?", (screening_id,)
                ).fetchone()
        return _row_to_entity(row)

    def delete(self, screening_id: int) -> bool:
        with closing(get_connection()) as conn:
            with conn:
                cur = conn.execute("DELETE FROM screening WHERE id = ?", (screening_id,))
        return cur.rowcount > 0
