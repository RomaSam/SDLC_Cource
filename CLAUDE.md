# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Cinema web app — Python + SQLite + FastAPI REST API, with an MCP server for AI tool integration. The project is split into two independently runnable components: the API server (`Cinema/api`) and the MCP server (`Cinema/mcp`).

---

## Database schema

Source of truth: `Cinema/db/schema.sql`. Single table: `screening` — one row per screening event.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | `INTEGER` | PK, AUTOINCREMENT | Auto-assigned primary key |
| `name` | `TEXT` | NOT NULL | Movie title |
| `genre` | `TEXT` | — | Movie genre (nullable) |
| `duration_minutes` | `INTEGER` | NOT NULL | Runtime in minutes |
| `screening_date` | `TEXT` | NOT NULL | ISO 8601 date (`YYYY-MM-DD`) |
| `begins_at` | `TEXT` | NOT NULL | Start time (`HH:MM`) |
| `hall` | `TEXT` | NOT NULL | Screening room identifier |
| `seats` | `INTEGER` | NOT NULL | Total seat capacity |

---

## Project structure

```
C:\SDLC_Cource\
├── CLAUDE.md                         # This file — guidance for Claude Code
├── README.md                         # Human-readable project overview and quickstart
├── .gitignore
│
├── Cinema/
│   ├── .env                          # Secrets: API_KEY (git-ignored)
│   ├── .gitignore
│   ├── requirements.txt              # API dependencies: fastapi, pydantic-settings, uvicorn
│   │
│   ├── api/                          # FastAPI application
│   │   ├── main.py                   # App factory + router registration
│   │   ├── config.py                 # Typed settings via pydantic-settings (reads Cinema/.env)
│   │   ├── dependencies.py           # FastAPI dependencies: API key auth + repo injection
│   │   ├── domain/
│   │   │   └── screening.py          # Screening dataclass — zero framework imports
│   │   ├── infrastructure/
│   │   │   ├── db.py                 # SQLite connection helper (sqlite3 stdlib)
│   │   │   └── screening_repository.py  # IScreeningRepository ABC + SQLiteScreeningRepository
│   │   └── interfaces/
│   │       ├── routers/
│   │       │   └── screenings.py     # FastAPI router — thin CRUD controller
│   │       └── schemas/
│   │           ├── screening_request.py   # Pydantic input schemas (Create, Patch)
│   │           └── screening_response.py  # Pydantic output schema (ScreeningResponse)
│   │
│   ├── db/
│   │   ├── schema.sql                # DDL — source of truth for DB structure
│   │   └── cinema.db                 # SQLite database (git-ignored)
│   │
│   ├── mcp/                          # MCP server for AI tool integration
│   │   ├── server.py                 # FastMCP entry point — registers tools, resources, prompts
│   │   ├── client.py                 # HTTP client wrapping the Cinema REST API
│   │   ├── config.py                 # Settings: API_KEY + API_BASE_URL (reads Cinema/.env)
│   │   ├── requirements.txt          # MCP dependencies: mcp[cli], httpx, pydantic-settings
│   │   ├── .env.example              # Template: API_KEY, API_BASE_URL
│   │   ├── tools/
│   │   │   └── mcp_tools.py          # MCP tools: list/get/create/replace/patch/delete screening
│   │   ├── resources/
│   │   │   └── mcp_resources.py      # MCP resources: screenings, genres, halls, today's screenings
│   │   └── prompts/
│   │       └── mcp_prompts.py        # MCP prompts: find_movie, summarise_schedule, hall_availability
│   │
│   └── claude_tools/
│       └── hooks/
│           └── hook.js               # Claude tool hook (JS)
│
└── .claude/                          # Claude Code configuration
    ├── settings.json                 # Hooks configuration (PreToolUse / PostToolUse)
    ├── commands/
    │   ├── db_create.md              # /db_create [--recreate] [--init]
    │   ├── git-commit.md             # /git-commit — conventional commit message generator
    │   └── add-test.md               # /add-test <file> — test skeleton generator
    ├── agents/
    │   ├── code-reviewer.md          # Proactive code review agent (Python/SQLite/FastAPI)
    │   └── test-writer.md            # Unit test generator agent (pytest + in-memory SQLite)
    ├── hooks/
    │   ├── check_secrets.py          # PreToolUse: blocks hardcoded secrets on Write/Edit
    │   ├── block_env_read.py         # PreToolUse: blocks Read/Edit of .env files
    │   └── ruff_check.py             # PostToolUse: runs ruff check after every .py Write/Edit
    ├── skills/
    │   └── api/
    │       └── SKILL.md              # /api skill — REST API implementation conventions
    └── agent-memory/
        └── code-reviewer/
            └── MEMORY.md             # Persistent memory index for the code-reviewer agent
```

---

## Dependencies

### API (`Cinema/requirements.txt`)

```
fastapi
pydantic-settings
uvicorn
```

Install:
```bash
cd Cinema
pip install -r requirements.txt
```

### MCP server (`Cinema/mcp/requirements.txt`)

```
mcp[cli]
httpx
pydantic-settings
```

Install:
```bash
cd Cinema/mcp
pip install -r requirements.txt
```

> SQLite is part of Python's standard library — no extra install needed.

---

## Environment setup

Both the API and the MCP server share a single secrets file: `Cinema/.env`.

```
# Cinema/.env  (never commit)
API_KEY=your-secret-key-here
```

The MCP server also reads `API_BASE_URL` from that file (defaults to `http://localhost:8000`). Use `Cinema/mcp/.env.example` as a template.

---

## Development workflow

### 1. Create / seed the database

```bash
# First time — create from schema
/db_create

# Drop and recreate from scratch
/db_create --recreate

# Create and seed with 10 rows of realistic test data
/db_create --init

# Recreate and seed in one step
/db_create --recreate --init
```

### 2. Start the API server

Run `uvicorn` from inside `Cinema/` so that `Cinema/api` is on `sys.path` and the config can locate `db/cinema.db` via its relative path.

```bash
cd Cinema
uvicorn api.main:app --reload
```

API available at `http://127.0.0.1:8000`. Interactive docs at `http://127.0.0.1:8000/docs`.

### 3. Start the MCP server (with Inspector)

```bash
cd Cinema/mcp
npx @modelcontextprotocol/inspector@0.19.0 py server.py
```

Inspector UI at `http://localhost:5173`.

> Use `py` on Windows. Use `python3` on macOS/Linux.

### 4. Run tests

```bash
# From repo root
py -m pytest --tb=short -q
```

Exit code 5 (no tests collected) is treated as success by the PostToolUse hook.

---

## API reference

All endpoints require the `X-API-Key` header.

| Method | Path | Body | Success | Description |
|---|---|---|---|---|
| `GET` | `/screenings` | — | `200` | List all; supports `?genre=`, `?date=`, `?hall=` |
| `GET` | `/screenings/{id}` | — | `200` / `404` | Get one by ID |
| `POST` | `/screenings` | `CreateScreeningRequest` | `201` | Create |
| `PUT` | `/screenings/{id}` | `CreateScreeningRequest` | `200` / `404` | Full replace |
| `PATCH` | `/screenings/{id}` | `PatchScreeningRequest` | `200` / `404` | Partial update |
| `DELETE` | `/screenings/{id}` | — | `204` / `404` | Delete |

---

## MCP server capabilities

The MCP server exposes three categories of primitives over the Cinema REST API:

**Tools** (actions): `list_screenings`, `get_screening`, `create_screening`, `replace_screening`, `patch_screening`, `delete_screening`

**Resources** (read-only data): `cinema://screenings`, `cinema://screenings/{id}`, `cinema://genres`, `cinema://halls`, `cinema://todays_screenings`

**Prompts** (AI command templates): `find_movie(genre, date)`, `summarise_schedule(date)`, `hall_availability(hall, date)`

---

## Database tooling

| Tool | Purpose | Install |
|---|---|---|
| **Python 3.10+** | Runtime + built-in `sqlite3` module | [python.org](https://python.org) |
| **DB Browser for SQLite** | GUI to browse, query, and edit `cinema.db` | [sqlitebrowser.org](https://sqlitebrowser.org) |
| **SQLite CLI** (`sqlite3`) | Lightweight shell for quick queries | bundled with most OS; Windows: [sqlite.org/download](https://sqlite.org/download.html) |
| **VS Code + SQLite Viewer** | Inline DB preview inside the editor | VS Code Marketplace: *SQLite Viewer* by Florian Klampfer |

```bash
sqlite3 Cinema/db/cinema.db
.tables
.schema screening
SELECT * FROM screening LIMIT 10;
.quit
```

---

## .claude/ folder reference

### Commands (`/command-name`)

| Command | File | Description |
|---|---|---|
| `/db_create [--recreate] [--init]` | `commands/db_create.md` | Create or recreate `cinema.db` from `schema.sql`; `--init` seeds 10 rows |
| `/git-commit` | `commands/git-commit.md` | Generate a Conventional Commits message from staged changes |
| `/add-test <file>` | `commands/add-test.md` | Generate a pytest skeleton for a given file or function |

### Skills (`/skill-name`)

| Skill | File | Description |
|---|---|---|
| `/api` | `skills/api/SKILL.md` | Full conventions for the REST API: layers, SQL safety, Pydantic schemas, auth, naming |

### Agents (spawned automatically by Claude)

| Agent | File | Trigger |
|---|---|---|
| `code-reviewer` | `agents/code-reviewer.md` | After new code is written or modified |
| `test-writer` | `agents/test-writer.md` | After Python functions/classes are added or changed |

### Hooks (run automatically by the harness)

| Hook | File | Event | What it does |
|---|---|---|---|
| `check_secrets.py` | `hooks/check_secrets.py` | PreToolUse `Write\|Edit` | Blocks writes that contain hardcoded API keys, tokens, or passwords |
| `block_env_read.py` | `hooks/block_env_read.py` | PreToolUse `Read\|Edit` | Blocks reads/edits of `.env` files (allows `.env.example` etc.) |
| `ruff_check.py` | `hooks/ruff_check.py` | PostToolUse `Write\|Edit` | Runs `ruff check` on any `.py` file after it is written or edited |
| pytest | `settings.json` | PostToolUse `Write\|Edit` | Runs `pytest --tb=short -q` after every Python file change |

---

## Pull request

Refer to `.claude/skills/pr-description/SKILL.md` to create a template for pull requests.
