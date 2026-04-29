---
name: Cinema API Skill Review Findings
description: Key bugs and patterns found during review of the Cinema API codebase (api/ tree) and the api SKILL.md
type: project
---

## SKILL.md pre-review (2026-04-28)

`@field_validator` decorators on `_ScreeningBase` for fields not defined on the base class cause a hard `PydanticUserError` crash at class definition time in Pydantic v2. Fix: `check_fields=False` on both decorators.

**Why:** Pydantic v2 raises an error by default when validators reference fields not present on the declaring class.

**How to apply:** Whenever reviewing or generating Pydantic v2 code that uses inheritance with field_validator on a base class, verify `check_fields=False` is set when the validated field is defined on a subclass.

---

## Full api/ tree review (2026-04-29)

### Confirmed fixes from SKILL.md review now present in actual code
- `check_fields=False` is correctly applied on both `_ScreeningBase` validators — crash is fixed.
- `db_path` default is `db/cinema.db` (relative to `Cinema/`) — correct.
- `model_dump(exclude_unset=True)` without `exclude_none=True` in PATCH router — correct; allows clearing nullable `genre`.
- `ScreeningResponse.from_entity()` guards `s.id is None` with a `ValueError` — type safety preserved.
- `with conn` inside `with closing(conn)` pattern is correctly used for commit/rollback, not for closing.

### Remaining / new issues found

**Connection hygiene (Major):** Each repository method opens a brand-new `sqlite3.Connection` per call. No connection pool or reuse. Acceptable for low traffic but a known scalability ceiling.

**`patch()` no-op on empty safe dict does a second DB round-trip:** When all keys fail the whitelist, `patch()` calls `self.get_by_id()` (another connection open/close) to return the current entity. A caller sending only garbage keys gets two DB connections for a single PATCH. Not a bug, but wasteful.

**`list_all` f-string with WHERE clause:** Column names in the WHERE clause come entirely from this method's own code (not user input), so no injection risk — the comment in the source correctly explains this. The `params` list carries values safely. This is a correctly documented safe pattern.

**Test quality — incomplete assertions (Major):** `test_screening_request.py` has ~8 tests where the assertion block is a TODO comment. The tests instantiate the object but assert nothing. This means the test suite can pass even if the schema is completely broken (e.g., accepts empty names, allows invalid dates).

**Test quality — overly broad `pytest.raises(Exception)` (Minor):** All error-path tests in `test_screening_request.py` catch bare `Exception` rather than `pydantic.ValidationError`. A `TypeError` or `AttributeError` would pass the assertion silently.

**`PatchScreeningRequest.at_least_one_field` validator gap (Major):** The model_validator fires only when `values` is an empty dict. If a client sends `{"unknown_key": "value"}` (a non-empty body with no recognized fields), Pydantic v2 with `extra="ignore"` (default) will silently drop the key and call `at_least_one_field` with `{}` only after field population — however, because all fields have defaults, the model builds successfully with all-None values and the validator sees `values` = the raw dict (non-empty `{"unknown_key": "value"}`). The validator passes, but the router's `model_dump(exclude_unset=True)` call returns `{}`, and the repo does a no-op. This is a silent 200 OK with no change when the client sent an all-unknown-key body.

**No router-level exception handler for DB errors (Major):** `SQLiteOperationalError` or `IntegrityError` from sqlite3 will bubble up as unhandled 500s without a meaningful API error response. No try/except wraps repository calls in the router.

**`get_screening_repo()` creates a new repo instance per request (Minor/Design):** Acceptable with stateless repository, but worth noting — if repository ever acquires state, this pattern needs revisiting.

**`Screening` dataclass is mutable with no validation (Suggestion):** Domain object accepts floats for `duration_minutes` and `seats` (confirmed by `test_no_coercion_of_float_duration`). This is a conscious design decision (dataclasses don't coerce), but the test explicitly documents it as expected behavior.

**`conftest.py` teardown is DELETE not DROP+recreate (Minor):** Between tests, `DELETE FROM screening` is used rather than dropping and recreating the table. This is fine for isolation between tests using the `db` fixture, but if a test creates a corrupt schema state, subsequent tests in the same session will not see a clean schema.

### Architectural observations
- No `__init__.py` files — project uses implicit namespace packages. uvicorn adds `Cinema/` to sys.path at startup. Tests add `Cinema/api/` manually in conftest.py.
- Separation of concerns is clean: domain has zero framework imports, infrastructure owns all SQL, routers are thin controllers.
- ABC pattern for `IScreeningRepository` enables test-time mocking/patching cleanly.
- Auth dependency (`verify_api_key`) is applied at router level via `dependencies=[...]`, not per-endpoint — correct for uniform enforcement.
