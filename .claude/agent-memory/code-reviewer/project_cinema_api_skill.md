---
name: Cinema API Skill Review Findings
description: Key bugs and patterns found during review of the api SKILL.md used to generate the Cinema REST API
type: project
---

The api SKILL.md at `.claude/skills/api/SKILL.md` was reviewed in depth on 2026-04-28.

**Critical bug confirmed**: `@field_validator` decorators on `_ScreeningBase` for fields (`screening_date`, `begins_at`) that are not defined on the base class itself cause a hard `PydanticUserError` crash at class definition time in Pydantic v2. Fix: add `check_fields=False` to both decorators.

**Why:** Pydantic v2 changed behavior — validators referencing fields not present on the declaring class raise an error by default unless `check_fields=False` is explicitly passed.

**How to apply:** Whenever reviewing or generating Pydantic v2 code that uses inheritance with field_validator on a base class, verify `check_fields=False` is set when the validated field is defined on a subclass.

**Other confirmed issues:**
- `config.py` default `db_path = "Cinema/db/cinema.db"` is wrong when uvicorn runs from `Cinema/` (the skill instructs `cd Cinema; uvicorn main:app`). Should be `db/cinema.db`.
- No `__init__.py` files are mentioned; the project relies on implicit namespace packages and uvicorn adding cwd to sys.path.
- `sqlite3` context manager (`with conn`) does NOT close the connection — it only commits/rolls back. The skill's prose says "connections close automatically" which is misleading.
- `model_dump(exclude_unset=True, exclude_none=True)` in PATCH router silently drops fields explicitly set to `null`, making it impossible to clear the nullable `genre` field via PATCH.
- `ScreeningResponse.id` typed as `int`, but `Screening.id` is `int | None` — a type mismatch that would cause a Pydantic ValidationError if `from_entity()` is ever called on an unpersisted entity.
- `tests` skill and `add-test` skill exist but no test instructions are in the api SKILL.md.
