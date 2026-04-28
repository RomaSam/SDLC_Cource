---
name: api
description: Implement a REST API for the Cinema app with API Key authentication, input validation, repository pattern, and domain model
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(pip install *), Bash(py *), Bash(python3 *), Bash(uvicorn *)
---

# REST API Implementation Skill

This document defines the architectural conventions, coding standards, and implementation patterns for the Cinema REST API. Follow them exactly. When Claude drifts, cite the relevant section and correct it.

---

## Role

You are acting as a **Senior Python Engineer**. Enforce all standards in this document rigidly. Do not introduce abstractions beyond what is described here.

---

## Stack

| Concern | Library | Why |
|---|---|---|
| Framework | `fastapi` | Built-in OpenAPI docs, Pydantic integration, type safety |
| Validation | `pydantic` v2 | Native to FastAPI, concise, fast |
| Config / secrets | `pydantic-settings` | Typed settings loaded from `.env` |
| DB access | `sqlite3` (stdlib) | No ORM needed for a single table |
| ASGI server | `uvicorn` | Standard FastAPI runner |

Install and record dependencies:

```bash
pip install fastapi pydantic-settings uvicorn
```

Add to `Cinema/requirements.txt`:
```
fastapi
pydantic-settings
uvicorn
```

---

## Project layout

All API files live under `Cinema/`:

```
Cinema/
├── main.py                              # FastAPI app factory + router registration
├── config.py                            # Typed settings via pydantic-settings
├── dependencies.py                      # FastAPI dependencies: auth + repository injection
│
├── domain/
│   └── screening.py                     # Screening dataclass — pure Python, zero framework imports
│
├── infrastructure/
│   ├── db.py                            # SQLite connection helper (sqlite3 stdlib)
│   └── screening_repository.py          # IScreeningRepository (ABC) + SQLiteScreeningRepository
│
└── interfaces/
    ├── routers/
    │   └── screenings.py                # FastAPI router — thin controller, CRUD only
    └── schemas/
        ├── screening_request.py         # Pydantic input schemas (Create, Patch)
        └── screening_response.py        # Pydantic output schema (ScreeningResponse)
```

---

## Layer rules

### Domain (`domain/`)
- Contains **pure Python** dataclasses — **zero** imports from fastapi, sqlite3, or pydantic.
- Enforces domain invariants in `__post_init__` if needed (e.g. `duration_minutes > 0`).
- `id` is `int | None` — `None` before persistence.

### Infrastructure (`infrastructure/`)
- `db.py` provides the SQLite connection.
- All SQL **values** use `?` placeholders — never interpolate user-supplied data into SQL strings.
- Column names in dynamic SET/WHERE clauses must be validated against an explicit whitelist before use.
- `screening_repository.py` contains both the abstract interface (`IScreeningRepository`) and its SQLite implementation (`SQLiteScreeningRepository`).
- The repository maps `sqlite3.Row` → domain entity and domain entity → SQL parameters.
- **No FastAPI imports** in this layer.

### Interface (`interfaces/`)
- Routers are **thin controllers**: validate input → call repository → return response schema.
- Always convert the domain entity to a `ScreeningResponse` before returning — never return raw entities or `sqlite3.Row` objects.
- HTTP status codes, headers, and error responses belong **only** in this layer.

---

## Config

**`Cinema/config.py`**

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_key: str
    db_path: str = "Cinema/db/cinema.db"

    model_config = SettingsConfigDict(env_file="Cinema/.env", env_file_encoding="utf-8")

settings = Settings()
```

`Cinema/.env` (never commit):
```
API_KEY=your-secret-key-here
```

---

## Domain entity

**`Cinema/domain/screening.py`**

```python
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
```

No ORM annotations, no Pydantic, no FastAPI — this is the source of truth for what a screening *is*.

---

## Database helper

**`Cinema/infrastructure/db.py`**

```python
import sqlite3
from config import settings

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    return conn
```

Always open connections inside a `with` block so they close automatically:

```python
with get_connection() as conn:
    ...
```

---

## Repository

`replace` uses a fixed SQL statement (PUT — full replacement).
`patch` uses a dynamic SET clause restricted to a column whitelist (PATCH — partial update).
This keeps PUT safe with literal SQL and confines dynamic SQL to PATCH where it is unavoidable.

**`Cinema/infrastructure/screening_repository.py`**

```python
import sqlite3
from abc import ABC, abstractmethod
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
        with get_connection() as conn:
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
        with get_connection() as conn:
            rows = conn.execute(
                f"SELECT * FROM screening {where}", params
            ).fetchall()
        return [_row_to_entity(r) for r in rows]

    def create(self, screening: Screening) -> Screening:
        with get_connection() as conn:
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
        with get_connection() as conn:
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
        if not data:
            return self.get_by_id(screening_id)
        # Whitelist: only allow known column names — never use raw user-supplied keys in SQL.
        safe = {k: v for k, v in data.items() if k in _PATCH_COLUMNS}
        if not safe:
            return self.get_by_id(screening_id)
        sets = ", ".join(f"{col} = ?" for col in safe)
        params: list[object] = list(safe.values()) + [screening_id]
        with get_connection() as conn:
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
        with get_connection() as conn:
            cur = conn.execute("DELETE FROM screening WHERE id = ?", (screening_id,))
        return cur.rowcount > 0
```

---

## Pydantic schemas

`_ScreeningBase` holds the shared validators. Both request schemas inherit from it so the validators work correctly for both required (`str`) and optional (`str | None`) fields without type conflicts.

### Request schemas — `Cinema/interfaces/schemas/screening_request.py`

```python
import re
from typing import Annotated
from pydantic import BaseModel, Field, field_validator

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_TIME_RE = re.compile(r"^\d{2}:\d{2}$")


class _ScreeningBase(BaseModel):
    @field_validator("screening_date", mode="before")
    @classmethod
    def validate_date(cls, v: object) -> object:
        if v is None:
            return v
        if not _DATE_RE.match(str(v)):
            raise ValueError("Must be ISO 8601 format: YYYY-MM-DD")
        return v

    @field_validator("begins_at", mode="before")
    @classmethod
    def validate_time(cls, v: object) -> object:
        if v is None:
            return v
        if not _TIME_RE.match(str(v)):
            raise ValueError("Must be HH:MM format")
        return v


class CreateScreeningRequest(_ScreeningBase):
    name: Annotated[str, Field(min_length=1, max_length=200)]
    genre: Annotated[str | None, Field(default=None, max_length=100)]
    duration_minutes: Annotated[int, Field(gt=0, le=600)]
    screening_date: str
    begins_at: str
    hall: Annotated[str, Field(min_length=1, max_length=50)]
    seats: Annotated[int, Field(gt=0, le=10000)]


class PatchScreeningRequest(_ScreeningBase):
    name: Annotated[str | None, Field(default=None, min_length=1, max_length=200)]
    genre: Annotated[str | None, Field(default=None, max_length=100)]
    duration_minutes: Annotated[int | None, Field(default=None, gt=0, le=600)]
    screening_date: str | None = None
    begins_at: str | None = None
    hall: Annotated[str | None, Field(default=None, min_length=1, max_length=50)]
    seats: Annotated[int | None, Field(default=None, gt=0, le=10000)]
```

### Response schema — `Cinema/interfaces/schemas/screening_response.py`

```python
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
```

---

## Authentication

**`Cinema/dependencies.py`**

```python
from fastapi import Header, HTTPException, status
from config import settings
from infrastructure.screening_repository import IScreeningRepository, SQLiteScreeningRepository


async def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_screening_repo() -> IScreeningRepository:
    return SQLiteScreeningRepository()
```

Apply auth at the **router level** using `dependencies=[Depends(verify_api_key)]` — not per-endpoint, not globally.

---

## Router (controller)

**`Cinema/interfaces/routers/screenings.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from dependencies import verify_api_key, get_screening_repo
from infrastructure.screening_repository import IScreeningRepository
from interfaces.schemas.screening_request import CreateScreeningRequest, PatchScreeningRequest
from interfaces.schemas.screening_response import ScreeningResponse
from domain.screening import Screening

router = APIRouter(
    prefix="/screenings",
    tags=["screenings"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/", response_model=list[ScreeningResponse])
def list_screenings(
    genre: str | None = Query(default=None),
    date: str | None = Query(default=None),
    hall: str | None = Query(default=None),
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> list[ScreeningResponse]:
    return [ScreeningResponse.from_entity(s) for s in repo.list_all(genre, date, hall)]


@router.get("/{screening_id}", response_model=ScreeningResponse)
def get_screening(
    screening_id: int,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    s = repo.get_by_id(screening_id)
    if s is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(s)


@router.post("/", response_model=ScreeningResponse, status_code=status.HTTP_201_CREATED)
def create_screening(
    body: CreateScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    entity = Screening(**body.model_dump())
    return ScreeningResponse.from_entity(repo.create(entity))


@router.put("/{screening_id}", response_model=ScreeningResponse)
def replace_screening(
    screening_id: int,
    body: CreateScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    entity = Screening(**body.model_dump())
    updated = repo.replace(screening_id, entity)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(updated)


@router.patch("/{screening_id}", response_model=ScreeningResponse)
def patch_screening(
    screening_id: int,
    body: PatchScreeningRequest,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> ScreeningResponse:
    data = body.model_dump(exclude_unset=True, exclude_none=True)
    updated = repo.patch(screening_id, data)
    if updated is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return ScreeningResponse.from_entity(updated)


@router.delete("/{screening_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_screening(
    screening_id: int,
    repo: IScreeningRepository = Depends(get_screening_repo),
) -> None:
    if not repo.delete(screening_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
```

---

## Application factory

**`Cinema/main.py`**

```python
from fastapi import FastAPI
from interfaces.routers.screenings import router as screenings_router


def create_app() -> FastAPI:
    app = FastAPI(title="Cinema API", version="1.0.0")
    app.include_router(screenings_router)
    return app


app = create_app()
```

Run locally:

```bash
cd Cinema
uvicorn main:app --reload
```

Interactive docs available at `http://localhost:8000/docs`.

---

## Endpoints reference

| Method | Path | Body | Success | Description |
|---|---|---|---|---|
| `GET` | `/screenings` | — | `200` | List all; supports `?genre=`, `?date=`, `?hall=` |
| `GET` | `/screenings/{id}` | — | `200` / `404` | Get one by ID |
| `POST` | `/screenings` | `CreateScreeningRequest` | `201` | Create |
| `PUT` | `/screenings/{id}` | `CreateScreeningRequest` | `200` / `404` | Full replace (fixed SQL) |
| `PATCH` | `/screenings/{id}` | `PatchScreeningRequest` | `200` / `404` | Partial update (whitelisted dynamic SQL) |
| `DELETE` | `/screenings/{id}` | — | `204` / `404` | Delete |

---

## Naming conventions

| Concept | Convention | Example |
|---|---|---|
| Domain entity | PascalCase dataclass | `Screening` |
| Repository interface | `I` prefix | `IScreeningRepository` |
| Repository implementation | DB name prefix | `SQLiteScreeningRepository` |
| Request schema | PascalCase + `Request` | `CreateScreeningRequest` |
| Response schema | PascalCase + `Response` | `ScreeningResponse` |
| Router file | snake_case, resource plural | `screenings.py` |
| Config key in `.env` | `UPPER_SNAKE_CASE` | `API_KEY` |

---

## Rules — what NOT to do

- Never import `fastapi`, `sqlite3`, or `pydantic` in `domain/`.
- Never return a domain entity or `sqlite3.Row` directly from a router — always use `ScreeningResponse.from_entity()`.
- Never put business logic in routers or schemas.
- Never hardcode the API key — always load from `config.settings`.
- Never interpolate user-supplied data into SQL strings — always use `?` placeholders for values.
- When column names must be dynamic (PATCH only), validate them against `_PATCH_COLUMNS` before use.
- Never put HTTP status codes or `HTTPException` inside the repository.
- Never define validators with a narrower type (`str`) on a base class when subclasses override the field to `str | None` — use `mode="before"` and guard against `None` explicitly.
- Use `replace()` for PUT and `patch()` for PATCH — they are not interchangeable.

---

## Implementation checklist

- [ ] `Cinema/.env` contains `API_KEY` (never committed).
- [ ] `Cinema/db/cinema.db` exists — run `/db_create` if not.
- [ ] All SQL values use `?` placeholders; dynamic column names in `patch()` validated against `_PATCH_COLUMNS`.
- [ ] Every router is guarded with `dependencies=[Depends(verify_api_key)]` at the router level.
- [ ] `domain/screening.py` imports nothing outside the stdlib.
- [ ] `ScreeningResponse.from_entity()` is the only place that converts a `Screening` entity to JSON.
- [ ] `replace()` is called for PUT, `patch()` is called for PATCH.
- [ ] `requirements.txt` contains `fastapi`, `pydantic-settings`, `uvicorn`.
- [ ] Smoke test: `curl -H "X-API-Key: <key>" http://localhost:8000/screenings/` returns a JSON array.
- [ ] OpenAPI docs load at `http://localhost:8000/docs` without errors.
