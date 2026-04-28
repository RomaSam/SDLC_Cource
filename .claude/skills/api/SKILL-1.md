# SKILL.md — Cinema CRUD API (Python + FastAPI + SQLite + DDD)

## Stack
- **Language:** Python 3.11+
- **Framework:** FastAPI
- **ORM:** SQLAlchemy (async, with aiosqlite)
- **Database:** SQLite
- **Validation:** Pydantic v2
- **Auth:** API Key via request header (`X-API-Key`)
- **Migration:** Alembic

---

## Project Structure

```
cinema_api/
├── main.py                         # FastAPI app entry point, router registration
├── config.py                       # Settings (API key, DB URL) via pydantic-settings
├── dependencies.py                 # Shared FastAPI dependencies (auth, db session)
│
├── domain/
│   ├── entities/
│   │   └── movie.py                # Movie entity (pure Python, no ORM imports)
│   ├── value_objects/
│   │   └── movie_id.py             # Typed value objects (e.g. MovieId)
│   ├── repositories/
│   │   └── movie_repository.py     # IMovieRepository — abstract interface only
│   └── exceptions.py               # Domain exceptions (MovieNotFoundError, etc.)
│
├── application/
│   └── use_cases/
│       ├── create_movie.py         # CreateMovieUseCase
│       ├── get_movie.py            # GetMovieUseCase
│       ├── list_movies.py          # ListMoviesUseCase
│       ├── update_movie.py         # UpdateMovieUseCase
│       └── delete_movie.py         # DeleteMovieUseCase
│
├── infrastructure/
│   ├── database/
│   │   ├── db.py                   # Async SQLAlchemy engine + session factory
│   │   └── models.py               # SQLAlchemy ORM model (MovieModel)
│   └── repositories/
│       └── sqlite_movie_repository.py  # SQLite impl of IMovieRepository
│
└── interfaces/
    ├── routers/
    │   └── movie_router.py         # FastAPI router — CRUD endpoints
    └── schemas/
        ├── movie_request.py        # CreateMovieRequest, UpdateMovieRequest (Pydantic)
        └── movie_response.py       # MovieResponse DTO (Pydantic)
```

---

## DDD Layer Rules

### Domain Layer (`domain/`)
- Contains **pure Python** entities and interfaces — zero framework or ORM imports
- `Movie` entity holds business fields and enforces invariants (e.g. release year > 1888)
- `IMovieRepository` is an **abstract base class** (ABC) with async method signatures only
- Domain exceptions live here (e.g. `MovieNotFoundError`, `DuplicateMovieError`)

### Application Layer (`application/`)
- One file per use case — each class has a single `execute()` async method
- Use cases accept **primitive types or simple dataclasses** as input, never HTTP objects
- Use cases depend on `IMovieRepository` (injected via constructor) — never on SQLAlchemy directly
- No HTTP status codes, no FastAPI imports here

### Infrastructure Layer (`infrastructure/`)
- `MovieModel` is the SQLAlchemy ORM model — **separate from the domain entity**
- `SQLiteMovieRepository` implements `IMovieRepository` and maps between `MovieModel` ↔ `Movie`
- All DB access is async (`async with session` pattern)

### Interface Layer (`interfaces/`)
- Controllers (routers) are thin: validate input → call use case → return DTO
- Always map domain entities to response schemas before returning — never return raw entities
- HTTP concerns (status codes, headers) belong only here

---

## API Key Authentication

- Clients must send `X-API-Key: <key>` header on every request
- Validation is done via a FastAPI dependency in `dependencies.py`
- The valid API key is loaded from environment variable `API_KEY` via `config.py`
- Return `HTTP 401` with `{"detail": "Invalid or missing API key"}` on failure
- Apply the dependency at the **router level** (not globally) using `dependencies=[Depends(verify_api_key)]`

```python
# dependencies.py — example
from fastapi import Header, HTTPException, status
from config import settings

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid or missing API key")
```

---

## Validation Rules (Pydantic v2)

- All request bodies use Pydantic `BaseModel` with field-level validation
- Use `Annotated` + `Field(...)` for constraints (min/max length, gt/lt, regex)
- `UpdateMovieRequest` uses all-optional fields (`title: str | None = None`)
- Validation errors return FastAPI's default `422 Unprocessable Entity` — do not suppress

Example fields for `Movie`:
```python
title: Annotated[str, Field(min_length=1, max_length=255)]
director: Annotated[str, Field(min_length=1, max_length=255)]
release_year: Annotated[int, Field(gt=1888, le=2100)]
genre: Annotated[str, Field(min_length=1, max_length=100)]
duration_minutes: Annotated[int, Field(gt=0, le=600)]
```

---

## Repository Pattern

```python
# domain/repositories/movie_repository.py
from abc import ABC, abstractmethod
from domain.entities.movie import Movie

class IMovieRepository(ABC):
    @abstractmethod
    async def get_by_id(self, movie_id: str) -> Movie | None: ...
    @abstractmethod
    async def list_all(self) -> list[Movie]: ...
    @abstractmethod
    async def save(self, movie: Movie) -> Movie: ...
    @abstractmethod
    async def update(self, movie: Movie) -> Movie: ...
    @abstractmethod
    async def delete(self, movie_id: str) -> None: ...
```

- The SQLite implementation maps ORM model → entity and entity → ORM model
- Use `uuid.uuid4()` for entity IDs generated in the domain layer

---

## CRUD Endpoints

| Method | Path | Description | Status |
|--------|------|-------------|--------|
| POST | `/movies` | Create a movie | 201 |
| GET | `/movies` | List all movies | 200 |
| GET | `/movies/{id}` | Get movie by ID | 200 / 404 |
| PUT | `/movies/{id}` | Full update | 200 / 404 |
| DELETE | `/movies/{id}` | Delete movie | 204 / 404 |

---

## Naming Conventions

| Concept | Convention | Example |
|---|---|---|
| Entity | PascalCase class | `Movie` |
| ORM Model | PascalCase + `Model` suffix | `MovieModel` |
| Repository interface | `I` prefix | `IMovieRepository` |
| Repository impl | DB name prefix | `SQLiteMovieRepository` |
| Use Case | PascalCase + `UseCase` suffix | `CreateMovieUseCase` |
| Request schema | PascalCase + `Request` | `CreateMovieRequest` |
| Response schema | PascalCase + `Response` | `MovieResponse` |
| Router file | snake_case + `_router` | `movie_router.py` |

---

## Rules — What NOT to Do

- ❌ Never import SQLAlchemy in `domain/` or `application/`
- ❌ Never return a domain entity directly from a router — always convert to a response schema
- ❌ Never put business logic in routers or ORM models
- ❌ Never hardcode the API key — always load from environment/config
- ❌ Never use sync SQLAlchemy — always use `AsyncSession`
- ❌ Never raise HTTP exceptions inside use cases — raise domain exceptions and handle them in routers

---

## Dependency Injection Pattern

Use cases receive the repository via constructor injection. FastAPI wires them via `Depends`:

```python
# dependencies.py
async def get_movie_repository(session: AsyncSession = Depends(get_session)):
    return SQLiteMovieRepository(session)

async def get_create_movie_use_case(repo = Depends(get_movie_repository)):
    return CreateMovieUseCase(repo)
```

---

## How to Use This File with Claude Code

Start every Claude Code session with:
> "Follow the conventions in SKILL.md. We are building a Cinema CRUD API with Python, FastAPI, SQLite, and DDD. Generate [file/feature] next."

Reference it when Claude drifts:
> "This violates SKILL.md — use cases must not import FastAPI. Fix it."