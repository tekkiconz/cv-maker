# Deferred Work

## Deferred from: code review of 1-4-delete-profile (2026-04-23)

- **Bare `except Exception` without logging** — `app/adapters/sqlite_database.py` — all adapter commit/rollback blocks catch `Exception` and re-raise without a `logger.exception()` call; violates the "never swallow exceptions" enforcement rule; pre-existing across `create_profile`, `update_profile`, and `delete_profile`.
- **Double-delete concurrent race** — `app/adapters/sqlite_database.py` — `session.get()` check and `session.delete()+commit()` are non-atomic; two concurrent deletes on the same id can both pass the None guard and cause an unexpected DB error; fixing requires serializable transactions or SELECT FOR UPDATE.
- **Adapter methods missing Tiger Style precondition assertions** — `app/adapters/sqlite_database.py` — none of the adapter methods assert their inputs; Tiger Style requires at minimum one input precondition per function; pre-existing across all methods.
- **No test for non-integer path segment on any route** — `tests/api/test_profiles.py` — FastAPI path coercion returns 422 for non-integer segments but this is untested for GET, PATCH, and DELETE routes.
- **Postcondition `get_profile` call unprotected on connection drop** — `app/services/profile_service.py` — the postcondition DB call after a successful delete has no error handling; a transient connection failure between commit and verification would surface as an unhandled exception after a logically successful delete.
- **No test for large integer boundary on `profile_id`** — `tests/api/test_profiles.py` — `Path(ge=1)` accepts any Python `int`; values near SQLite's signed 64-bit max should be verified to return 404 cleanly rather than an adapter error.
