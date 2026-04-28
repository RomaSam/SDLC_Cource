---
name: Cinema project test patterns
description: Established fixtures, shared-cache SQLite setup, and patch target for SQLiteScreeningRepository tests
type: project
---

The Cinema project test suite uses these conventions:

**Shared-cache in-memory SQLite setup:**
- URI: `file:cinema_test?mode=memory&cache=shared`
- `_make_conn()` creates each connection with `check_same_thread=False` and `row_factory = sqlite3.Row`
- The `db` fixture applies schema via `conn.executescript(SCHEMA_PATH.read_text())`, yields, then `DELETE FROM screening` + `conn.close()`
- `make_connection` fixture depends on `db` (ensuring schema exists) and returns `_make_conn` (the function)

**Patch target:** `infrastructure.screening_repository.get_connection`
- The `repo` fixture wraps `SQLiteScreeningRepository()` inside `patch(_PATCH_TARGET, side_effect=make_connection)`
- `side_effect=make_connection` means each call to `get_connection()` in the repo calls `_make_conn()`, returning a fresh connection to the shared in-memory DB

**Fixture dependency chain:** `db` → `make_connection` → `repo`

**Schema path:** `Path(__file__).parents[2] / "db" / "schema.sql"` (from `Cinema/api/tests/`)

**sys.path insert:** `sys.path.insert(0, str(Path(__file__).parents[1]))` in conftest.py adds `Cinema/api/` so `domain.screening` and `infrastructure.screening_repository` resolve

**Why:** The `patch()` method with an empty dict or unknown-only keys calls `self.get_by_id()` internally, which also calls `get_connection()` — so the shared-cache approach is essential for cross-connection data visibility.

**How to apply:** Use these same fixtures for any new repository tests. The `_make_conn` / shared URI pattern is the established approach — do not switch to a single-connection approach or tmpfile.
