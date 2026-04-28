# Cinema API

A Cinema screening management system built with **Python**, **FastAPI**, and **SQLite**, paired with an **MCP server** that exposes the API to AI assistants as tools, resources, and prompts.

---

## Table of contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Project structure](#project-structure)
- [Technologies](#technologies)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment setup](#environment-setup)
- [Running locally](#running-locally)
- [API reference](#api-reference)
- [MCP server capabilities](#mcp-server-capabilities)
- [Database](#database)
- [Testing](#testing)

---

## Overview

Cinema API manages movie screening schedules for a cinema. It provides a RESTful HTTP API to create, read, update, and delete screenings, and exposes the same data to AI assistants via an MCP (Model Context Protocol) server.

The system consists of two independently runnable services:

| Service | Purpose | Default URL |
|---|---|---|
| **Cinema API** | REST API for screening CRUD | `http://localhost:8000` |
| **MCP server** | Bridges the API to AI tools | launched via MCP Inspector |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Clients                          │
│   HTTP clients / Swagger UI    AI assistants (MCP)      │
└───────────────┬─────────────────────────┬───────────────┘
                │                         │
                ▼                         ▼
┌──────────────────────┐    ┌──────────────────────────┐
│    Cinema REST API   │◄───│       MCP Server         │
│    (FastAPI)         │    │  tools / resources /     │
│                      │    │  prompts (FastMCP)       │
│  ┌────────────────┐  │    └──────────────────────────┘
│  │   Interfaces   │  │
│  │  (routers +    │  │
│  │   schemas)     │  │
│  └───────┬────────┘  │
│          │           │
│  ┌───────▼────────┐  │
│  │   Domain       │  │
│  │  (Screening    │  │
│  │   dataclass)   │  │
│  └───────┬────────┘  │
│          │           │
│  ┌───────▼────────┐  │
│  │ Infrastructure │  │
│  │  (SQLite repo) │  │
└──┴────────────────┴──┘
           │
           ▼
    ┌─────────────┐
    │  cinema.db  │
    │  (SQLite)   │
    └─────────────┘
```

The API follows a layered architecture:

- **Interfaces** — FastAPI routers and Pydantic schemas. Handles HTTP concerns and input validation.
- **Domain** — Plain `Screening` dataclass with no framework dependencies.
- **Infrastructure** — `IScreeningRepository` ABC with a `SQLiteScreeningRepository` implementation.

---

## Project structure

```
C:\SDLC_Cource\
├── Cinema/
│   ├── .env                          # Secrets: API_KEY (git-ignored)
│   ├── requirements.txt              # API dependencies
│   │
│   ├── api/                          # FastAPI application
│   │   ├── main.py                   # App factory + router registration
│   │   ├── config.py                 # Typed settings via pydantic-settings
│   │   ├── dependencies.py           # API key auth + repository injection
│   │   ├── domain/
│   │   │   └── screening.py          # Screening dataclass — no framework imports
│   │   ├── infrastructure/
│   │   │   ├── db.py                 # SQLite connection helper
│   │   │   └── screening_repository.py  # Repository ABC + SQLite implementation
│   │   ├── interfaces/
│   │   │   ├── routers/
│   │   │   │   └── screenings.py     # CRUD router
│   │   │   └── schemas/
│   │   │       ├── screening_request.py   # Pydantic input schemas (Create, Patch)
│   │   │       └── screening_response.py  # Pydantic output schema
│   │   └── tests/
│   │       ├── conftest.py           # In-memory SQLite fixtures
│   │       └── test_screening_repository.py
│   │
│   ├── db/
│   │   ├── schema.sql                # DDL — source of truth for DB structure
│   │   └── cinema.db                 # SQLite database file (git-ignored)
│   │
│   └── mcp/                          # MCP server
│       ├── server.py                 # FastMCP entry point
│       ├── client.py                 # HTTP client wrapping the Cinema REST API
│       ├── config.py                 # Settings: API_KEY + API_BASE_URL
│       ├── requirements.txt          # MCP dependencies
│       ├── .env.example              # Secrets template
│       ├── tools/
│       │   └── mcp_tools.py          # list/get/create/replace/patch/delete
│       ├── resources/
│       │   └── mcp_resources.py      # screenings, genres, halls, today's screenings
│       └── prompts/
│           └── mcp_prompts.py        # find_movie, summarise_schedule, hall_availability
```

---

## Technologies

| Technology | Role |
|---|---|
| **Python 3.10+** | Runtime |
| **FastAPI** | REST API framework |
| **Pydantic v2** | Request/response validation and settings management |
| **SQLite** | Embedded relational database (stdlib `sqlite3`) |
| **Uvicorn** | ASGI server for FastAPI |
| **FastMCP** | MCP server framework (`mcp[cli]`) |
| **httpx** | Async HTTP client used by the MCP server |
| **pytest** | Test runner |
| **ruff** | Linter (runs automatically on every `.py` save via hook) |

---

## Prerequisites

The following must be installed before running the project locally:

| Tool | Minimum version | Notes |
|---|---|---|
| **Python** | 3.10 | [python.org](https://python.org) — includes `sqlite3` and `pip` |
| **Node.js** | 18 LTS | Required to run `npx` for the MCP Inspector |
| **Git** | any | For cloning the repository |

Optional but recommended:

| Tool | Purpose |
|---|---|
| **DB Browser for SQLite** | GUI for browsing and editing `cinema.db` |
| **VS Code + SQLite Viewer** | Inline database preview in the editor |

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd SDLC_Cource
```

### 2. Install API dependencies

```bash
cd Cinema
pip install -r requirements.txt
```

### 3. Install MCP server dependencies

```bash
cd Cinema/mcp
pip install -r requirements.txt
```

> SQLite is part of Python's standard library — no extra install needed.

---

## Environment setup

Both services share a single secrets file at `Cinema/.env`. Create it from the template:

```bash
cp Cinema/mcp/.env.example Cinema/.env
```

Then edit `Cinema/.env`:

```env
# Cinema/.env  — never commit this file
API_KEY=your-secret-key-here
API_BASE_URL=http://localhost:8000   # MCP server uses this to reach the API
```

`API_KEY` is required by both the REST API (enforced on every request via `X-API-Key` header) and the MCP server (passed through to the API).

---

## Running locally

### 1. Create the database

Run from the repo root using the `/db_create` Claude command, or manually:

```bash
# Create schema only
sqlite3 Cinema/db/cinema.db < Cinema/db/schema.sql

# Or recreate and seed with 10 sample rows via Claude command
/db_create --recreate --init
```

### 2. Start the Cinema API

Run from inside `Cinema/` so that `Cinema/api` is on `sys.path`:

```bash
cd Cinema
uvicorn api.main:app --reload
```

| URL | Description |
|---|---|
| `http://127.0.0.1:8000` | API root |
| `http://127.0.0.1:8000/docs` | Interactive Swagger UI |
| `http://127.0.0.1:8000/redoc` | ReDoc documentation |

### 3. Start the MCP server

Use the pinned Inspector version to avoid known bugs in other releases:

```bash
cd Cinema/mcp
npx @modelcontextprotocol/inspector@0.19.0 py server.py
```

Inspector UI opens at `http://localhost:5173`.

> Use `py` on Windows. Use `python3` on macOS/Linux.

**Note:** The Inspector does not auto-refresh resources. To load current data for any resource, click the resource name in the sidebar, then click **"Read Resource"** in the detail pane.

Both services must be running simultaneously for the MCP server to work — it calls the REST API over HTTP.

---

## API reference

All endpoints require the `X-API-Key` header matching the value in `Cinema/.env`.

### Screening endpoints

| Method | Path | Body | Status | Description |
|---|---|---|---|---|
| `GET` | `/screenings` | — | `200` | List all screenings. Supports `?genre=`, `?date=` (YYYY-MM-DD), `?hall=` |
| `GET` | `/screenings/{id}` | — | `200` / `404` | Get a single screening by ID |
| `POST` | `/screenings` | `CreateScreeningRequest` | `201` | Create a new screening |
| `PUT` | `/screenings/{id}` | `CreateScreeningRequest` | `200` / `404` | Fully replace a screening |
| `PATCH` | `/screenings/{id}` | `PatchScreeningRequest` | `200` / `404` | Partially update a screening |
| `DELETE` | `/screenings/{id}` | — | `204` / `404` | Delete a screening |

### Request body — `CreateScreeningRequest`

| Field | Type | Constraints | Description |
|---|---|---|---|
| `name` | `string` | required, 1–200 chars | Movie title |
| `genre` | `string \| null` | max 100 chars | Genre (optional) |
| `duration_minutes` | `integer` | 1–600 | Runtime in minutes |
| `screening_date` | `string` | `YYYY-MM-DD`, valid calendar date | Screening date |
| `begins_at` | `string` | `HH:MM`, valid time | Start time |
| `hall` | `string` | 1–50 chars | Screening room identifier |
| `seats` | `integer` | 1–10,000 | Seat capacity |

`PatchScreeningRequest` accepts the same fields, all optional. At least one field must be provided.

### Example request

```bash
curl -X POST http://localhost:8000/screenings \
  -H "X-API-Key: your-secret-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Inception",
    "genre": "Sci-Fi",
    "duration_minutes": 148,
    "screening_date": "2026-05-01",
    "begins_at": "19:30",
    "hall": "A1",
    "seats": 120
  }'
```

---

## MCP server capabilities

The MCP server bridges the Cinema REST API to AI assistants via three primitive types:

### Tools (actions the AI can invoke)

| Tool | Description |
|---|---|
| `list_screenings` | List all screenings, optionally filtered by `genre`, `date`, or `hall` |
| `get_screening` | Fetch a single screening by ID |
| `create_screening` | Create a new screening |
| `replace_screening` | Fully replace an existing screening (PUT) |
| `patch_screening` | Partially update a screening (PATCH) |
| `delete_screening` | Delete a screening by ID |

### Resources (read-only data injected into AI context)

| URI | Description |
|---|---|
| `cinema://screenings` | Full list of all screenings |
| `cinema://screenings/{id}` | Single screening by ID |
| `cinema://genres` | Sorted list of distinct genres |
| `cinema://halls` | Sorted list of distinct hall identifiers |
| `cinema://todays_screenings` | All screenings scheduled for today |

### Prompts (reusable AI command templates)

| Prompt | Parameters | Description |
|---|---|---|
| `find_movie` | `genre`, `date` | Recommend screenings matching a genre on a given date |
| `summarise_schedule` | `date` | Summarise all screenings for a day, grouped by hall |
| `hall_availability` | `hall`, `date` | Report seat availability for a specific hall on a date |

---

## Database

Source of truth: `Cinema/db/schema.sql`. Single table: `screening`.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | PK, AUTOINCREMENT | Auto-assigned primary key |
| `name` | `TEXT` | NOT NULL | Movie title |
| `genre` | `TEXT` | — | Genre (nullable) |
| `duration_minutes` | `INTEGER` | NOT NULL | Runtime in minutes |
| `screening_date` | `TEXT` | NOT NULL | ISO 8601 date (`YYYY-MM-DD`) |
| `begins_at` | `TEXT` | NOT NULL | Start time (`HH:MM`) |
| `hall` | `TEXT` | NOT NULL | Screening room identifier |
| `seats` | `INTEGER` | NOT NULL | Total seat capacity |

### Useful SQLite commands

```bash
sqlite3 Cinema/db/cinema.db
.tables
.schema screening
SELECT * FROM screening LIMIT 10;
.quit
```

---

## Testing

Tests use `pytest` with an in-memory SQLite database — no running server required.

```bash
# From repo root
py -m pytest --tb=short -q        # Windows
python3 -m pytest --tb=short -q   # macOS / Linux
```

Tests live in `Cinema/api/tests/`. The `conftest.py` provides an in-memory `SQLiteScreeningRepository` fixture shared across all test modules.
