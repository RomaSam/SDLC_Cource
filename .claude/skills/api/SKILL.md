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

| Concern | Library |
|---|---|
| Framework | `flask` |
| Validation | `marshmallow` |
| Env loading | `python-dotenv` |
| DB access | `sqlite3` (stdlib) |

Install dependencies if not already present:

```bash
pip install flask marshmallow python-dotenv
```

Add them to `Cinema/requirements.txt`.

---

## Project layout

Place new files under `Cinema/`:

```
Cinema/
├── app.py              # Flask application factory + route registration
├── auth.py             # API Key authentication decorator
├── db.py               # SQLite connection helper
├── schemas.py          # Marshmallow schemas for input validation
├── routes/
│   └── screenings.py   # Blueprint with all /screenings endpoints
└── .env                # API_KEY=<secret>  (already git-ignored)
```

---

## API Key authentication

Read the key from `.env` via `python-dotenv`. Clients pass it in the `X-API-Key` request header.

**`Cinema/auth.py`**

```python
import os
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key", "")
        if not key or key != os.environ.get("API_KEY", ""):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated
```

Set `API_KEY` in `Cinema/.env`:

```
API_KEY=your-secret-key-here
```

---

## Database helper

**`Cinema/db.py`**

```python
import sqlite3
import pathlib

DB_PATH = pathlib.Path(__file__).parent / "db" / "cinema.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
```

Always use `with get_connection() as conn:` so the connection closes automatically. Never use string formatting in SQL — use `?` placeholders.

---

## Input validation schemas

**`Cinema/schemas.py`**

```python
from marshmallow import Schema, fields, validate, validates, ValidationError
import re

class ScreeningSchema(Schema):
    name             = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    genre            = fields.Str(load_default=None, validate=validate.Length(max=100))
    duration_minutes = fields.Int(required=True, validate=validate.Range(min=1, max=600))
    screening_date   = fields.Str(required=True)
    begins_at        = fields.Str(required=True)
    hall             = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    seats            = fields.Int(required=True, validate=validate.Range(min=1, max=10000))

    @validates("screening_date")
    def validate_date(self, value):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValidationError("Must be ISO 8601 format: YYYY-MM-DD")

    @validates("begins_at")
    def validate_time(self, value):
        if not re.fullmatch(r"\d{2}:\d{2}", value):
            raise ValidationError("Must be HH:MM format")

# Partial schema reuses the same fields but marks all as optional (for PATCH)
ScreeningPatchSchema = ScreeningSchema(partial=True)
```

---

## Endpoints

Register a Blueprint in **`Cinema/routes/screenings.py`**:

| Method | Path | Description |
|---|---|---|
| `GET` | `/screenings` | List all screenings. Supports `?genre=`, `?date=`, `?hall=` query params. |
| `GET` | `/screenings/<int:id>` | Get one screening by ID. |
| `POST` | `/screenings` | Create a new screening. Body: full `ScreeningSchema`. |
| `PUT` | `/screenings/<int:id>` | Replace a screening. Body: full `ScreeningSchema`. |
| `PATCH` | `/screenings/<int:id>` | Partial update. Body: any subset of fields. |
| `DELETE` | `/screenings/<int:id>` | Delete a screening. |

### Response conventions

- Success with body → `200` (GET, PUT, PATCH) or `201` (POST).
- Success no body → `204` (DELETE).
- Validation error → `400` with `{"error": "Validation failed", "details": {...}}`.
- Not found → `404` with `{"error": "Not found"}`.
- Auth failure → `401` with `{"error": "Unauthorized"}`.

All responses use `Content-Type: application/json`.

### Implementation template

```python
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from auth import require_api_key
from db import get_connection
from schemas import ScreeningSchema, ScreeningPatchSchema

bp = Blueprint("screenings", __name__, url_prefix="/screenings")
schema = ScreeningSchema()
patch_schema = ScreeningPatchSchema


def row_to_dict(row):
    return dict(row)


@bp.get("/")
@require_api_key
def list_screenings():
    filters, params = [], []
    for col in ("genre", "hall"):
        val = request.args.get(col)
        if val:
            filters.append(f"{col} = ?")
            params.append(val)
    date = request.args.get("date")
    if date:
        filters.append("screening_date = ?")
        params.append(date)

    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM screening {where}", params).fetchall()
    return jsonify([row_to_dict(r) for r in rows])


@bp.get("/<int:id>")
@require_api_key
def get_screening(id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM screening WHERE id = ?", (id,)).fetchone()
    if row is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(row_to_dict(row))


@bp.post("/")
@require_api_key
def create_screening():
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO screening (name, genre, duration_minutes, screening_date, begins_at, hall, seats) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (data["name"], data.get("genre"), data["duration_minutes"],
             data["screening_date"], data["begins_at"], data["hall"], data["seats"]),
        )
        new_id = cur.lastrowid
        row = conn.execute("SELECT * FROM screening WHERE id = ?", (new_id,)).fetchone()
    return jsonify(row_to_dict(row)), 201


@bp.put("/<int:id>")
@require_api_key
def replace_screening(id):
    try:
        data = schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    with get_connection() as conn:
        cur = conn.execute(
            "UPDATE screening SET name=?, genre=?, duration_minutes=?, screening_date=?, begins_at=?, hall=?, seats=? "
            "WHERE id=?",
            (data["name"], data.get("genre"), data["duration_minutes"],
             data["screening_date"], data["begins_at"], data["hall"], data["seats"], id),
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        row = conn.execute("SELECT * FROM screening WHERE id = ?", (id,)).fetchone()
    return jsonify(row_to_dict(row))


@bp.patch("/<int:id>")
@require_api_key
def update_screening(id):
    try:
        data = patch_schema.load(request.get_json(force=True) or {})
    except ValidationError as e:
        return jsonify({"error": "Validation failed", "details": e.messages}), 400

    if not data:
        return jsonify({"error": "No fields provided"}), 400

    sets = ", ".join(f"{k} = ?" for k in data)
    params = list(data.values()) + [id]
    with get_connection() as conn:
        cur = conn.execute(f"UPDATE screening SET {sets} WHERE id = ?", params)
        if cur.rowcount == 0:
            return jsonify({"error": "Not found"}), 404
        row = conn.execute("SELECT * FROM screening WHERE id = ?", (id,)).fetchone()
    return jsonify(row_to_dict(row))


@bp.delete("/<int:id>")
@require_api_key
def delete_screening(id):
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM screening WHERE id = ?", (id,))
    if cur.rowcount == 0:
        return jsonify({"error": "Not found"}), 404
    return "", 204
```

---

## Application factory

**`Cinema/app.py`**

```python
from flask import Flask
from dotenv import load_dotenv

load_dotenv()  # loads Cinema/.env

def create_app():
    app = Flask(__name__)
    from routes.screenings import bp as screenings_bp
    app.register_blueprint(screenings_bp)
    return app

if __name__ == "__main__":
    create_app().run(debug=True)
```

Run locally:

```bash
cd Cinema
py app.py
```

---

## Implementation checklist

When implementing this skill, verify:

- [ ] `Cinema/.env` contains `API_KEY` (never commit the value).
- [ ] All SQL uses `?` placeholders — no f-strings or `.format()` in queries.
- [ ] Every endpoint is decorated with `@require_api_key`.
- [ ] `ScreeningSchema` is used for POST/PUT; `ScreeningPatchSchema` for PATCH.
- [ ] `requirements.txt` lists `flask`, `marshmallow`, and `python-dotenv`.
- [ ] `Cinema/db/cinema.db` exists (run `/db_create` if not).
- [ ] Manual smoke test: `curl -H "X-API-Key: <key>" http://localhost:5000/screenings/` returns JSON array.


