# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is simple Cinema web app based on Python storing data in SQLite database.

## Database schema

See `schema.sql` for the full DDL. Single table: `screening` — one row per screening event.

| Column | Type | Description |
|---|---|---|
| `id` | `INTEGER` | Primary key, auto-incremented by SQLite. |
| `name` | `TEXT` | Movie title. |
| `genre` | `TEXT` | Movie genre. |
| `duration_minutes` | `INTEGER` | Runtime in minutes. |
| `screening_date` | `TEXT` | Date stored as ISO 8601 string (`YYYY-MM-DD`). |
| `begins_at` | `TEXT` | Start time (`HH:MM`), separate from date for easy time-of-day filtering. |
| `hall` | `TEXT` | Screening room identifier. |
| `seats` | `INTEGER` | Total seat capacity for this screening. |

---


## Project structure

```
Cinema/
├── schema.sql        # DDL — source of truth for DB structure
├── requirements.txt  # Python dependencies
├── cinema.db         # SQLite database (git-ignored)
├── .env              # local secrets, e.g. API_KEY (git-ignored)
└── .gitignore

.claude/commands/
├── db_create/          # /db_create [--recreate] — create or recreate cinema.db
├── git-commit/       # /git-commit — generate conventional commit message
└── add-test/         # /add-test <file> — generate test skeleton
```

## Development commands

```bash
# Install dependencies
pip install -r requirements.txt

# Create database (first time)
/db_create

# Recreate database from scratch (drops all data)
/db_create --recreate

# Create and seed with 10 rows of realistic test data
/db_create --init

# Recreate and seed in one step
/db_create --recreate --init
```

> SQLite is part of Python's standard library — no extra install needed.

## Database tooling

### Required / recommended software

| Tool | Purpose | Install |
|---|---|---|
| **Python 3.10+** | Runtime + built-in `sqlite3` module | [python.org](https://python.org) |
| **DB Browser for SQLite** | GUI to browse, query, and edit `cinema.db` | [sqlitebrowser.org](https://sqlitebrowser.org) |
| **SQLite CLI** (`sqlite3`) | Lightweight shell for quick queries | bundled with most OS; Windows: [sqlite.org/download](https://sqlite.org/download.html) |
| **VS Code + SQLite Viewer extension** | Inline DB preview inside the editor | VS Code Marketplace: *SQLite Viewer* by Florian Klampfer |

### Viewing the database

**GUI (DB Browser for SQLite)**
1. Open DB Browser for SQLite.
2. Click **Open Database** and select `Cinema/db/cinema.db`.
3. Use the **Browse Data** tab to inspect rows, or the **Execute SQL** tab to run queries.

**CLI**
```bash
sqlite3 Cinema/db/cinema.db

# Useful commands once inside the shell:
.tables               -- list all tables
.schema screening     -- show table DDL
SELECT * FROM screening LIMIT 10;
.quit
```

**VS Code**
Open `Cinema/db/cinema.db` in VS Code — the SQLite Viewer extension renders it as a read-only spreadsheet directly in the editor.

## Pull request

Refer to `.claude/skills/pr-description/SKILL.md` to create a template for pull request