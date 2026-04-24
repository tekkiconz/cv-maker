# Story 1.6: Pre-Epic 2 Cleanup

Status: review

## Story

As a developer,
I want adapter precondition assertions, structured logging on DB errors, and a cascade integration test in place,
so that Epic 2 starts with the "trust no one" team agreement enforced and Story 2.1 AC 16 unblocked.

## Acceptance Criteria

1. Every `SQLiteDatabaseAdapter` method that accepts a `profile_id` or `contact_id` parameter asserts the value is `> 0` at entry.
2. Every `except Exception` block in `SQLiteDatabaseAdapter` logs the error with `logger.exception(...)` before re-raising (log-and-re-raise, never swallow).
3. An integration test `tests/api/test_profiles.py::test_delete_profile_cascades_contacts` verifies that deleting a profile via `DELETE /api/profiles/{id}` also removes all associated contacts (returns 404 on subsequent `GET /api/profiles/{id}/contacts/{contact_id}`).
4. `MAX_ENTRIES_PER_SECTION` already exists in `app/constants/limits.py` — no change needed (verify and note).
5. All existing tests continue to pass with no regressions (`make test-local`).
6. Lint and type checks pass (`ruff check . && ruff format --check .` and `make typecheck-local`).

## Tasks / Subtasks

- [x] Task 1: Retrofit adapter precondition assertions (AC: 1)
  - [x] 1.1 `get_profile(profile_id)` — add `assert profile_id > 0` at entry.
  - [x] 1.2 `update_profile(profile_id, data)` — add `assert profile_id > 0` at entry.
  - [x] 1.3 `delete_profile(profile_id)` — add `assert profile_id > 0` at entry.
  - [x] 1.4 `profile_exists(profile_id)` — add `assert profile_id > 0` at entry.
  - [x] 1.5 `list_contacts(profile_id)` — add `assert profile_id > 0` at entry.
  - [x] 1.6 `get_contact(profile_id, contact_id)` — add `assert profile_id > 0` and `assert contact_id > 0` at entry.
  - [x] 1.7 `update_contact(profile_id, contact_id, data)` — add `assert profile_id > 0` and `assert contact_id > 0` at entry.
  - [x] 1.8 `delete_contact(profile_id, contact_id)` — add `assert profile_id > 0` and `assert contact_id > 0` at entry.
  - [x] 1.9 `create_contact(profile_id, data)` — add `assert profile_id > 0` at entry (before the count query).

- [x] Task 2: Add structured logging to all `except Exception` blocks (AC: 2)
  - [x] 2.1 Add `import logging` and `logger = logging.getLogger(__name__)` at module level in `sqlite_database.py`.
  - [x] 2.2 `create_profile` except block — add `logger.exception("create_profile failed")` before `raise`.
  - [x] 2.3 `update_profile` except block — add `logger.exception("update_profile failed for profile_id=%s", profile_id)` before `raise`.
  - [x] 2.4 `delete_profile` except block — add `logger.exception("delete_profile failed for profile_id=%s", profile_id)` before `raise`.
  - [x] 2.5 `create_contact` except block — add `logger.exception("create_contact failed for profile_id=%s", profile_id)` before `raise`.
  - [x] 2.6 `update_contact` except block — add `logger.exception("update_contact failed for profile_id=%s contact_id=%s", profile_id, contact_id)` before `raise`.
  - [x] 2.7 `delete_contact` except block — add `logger.exception("delete_contact failed for profile_id=%s contact_id=%s", profile_id, contact_id)` before `raise`.

- [x] Task 3: Integration test — profile delete cascades contacts (AC: 3)
  - [x] 3.1 In `tests/api/test_profiles.py`, add `test_delete_profile_cascades_contacts`:
    - Create a profile via `POST /api/profiles`.
    - Add a contact via `POST /api/profiles/{id}/contacts`.
    - Delete the profile via `DELETE /api/profiles/{id}`.
    - Assert `GET /api/profiles/{id}/contacts/{contact_id}` returns 404 (contact gone with profile).

- [x] Task 4: Verify `MAX_ENTRIES_PER_SECTION` exists and run full validation (AC: 4, 5, 6)
  - [x] 4.1 Confirm `MAX_ENTRIES_PER_SECTION` is present in `app/constants/limits.py` — no code change needed; note in completion record.
  - [x] 4.2 Run `make test-local` — all tests pass, no regressions.
  - [x] 4.3 Run `ruff check . && ruff format --check .` — clean.
  - [x] 4.4 Run `make typecheck-local` — no errors.

## Dev Notes

### Context

This story delivers the Pre-Epic 2 Cleanup tasks identified in the Epic 1 retrospective (2026-04-24). All tasks must complete before Story 2.1 begins.

### Adapter Precondition Pattern

Follow the same Tiger Style pattern already used in `create_profile` and `create_contact`:
```python
async def get_profile(self, profile_id: int) -> ProfileRead | None:
    assert profile_id > 0, "profile_id must be a positive integer"
    ...
```

Assertions fire on programmer errors (bad callers). They stay in production per Tiger Style.

### Logging Pattern

Use `logger.exception(...)` (not `logger.error`) inside `except` blocks — `exception` captures the traceback automatically:
```python
import logging
logger = logging.getLogger(__name__)

...
except Exception:
    logger.exception("create_profile failed")
    await self._session.rollback()
    raise
```

### Cascade Test Pattern

The test must use the real `http_client` fixture (with `override_contact_service` already wired in `conftest.py`). After deleting a profile, assert that a `GET` on the contact returns 404, confirming ORM cascade (`cascade="all, delete-orphan"` on `Profile.contacts`) removes child rows.

```python
async def test_delete_profile_cascades_contacts(http_client: AsyncClient) -> None:
    create_r = await http_client.post("/api/profiles", json={"name": "Cascade Test", "description": ""})
    pid = create_r.json()["id"]
    contact_r = await http_client.post(
        f"/api/profiles/{pid}/contacts",
        json={"type": "email", "value": "x@example.com"},
    )
    cid = contact_r.json()["id"]

    del_r = await http_client.delete(f"/api/profiles/{pid}")
    assert del_r.status_code == 204

    get_r = await http_client.get(f"/api/profiles/{pid}/contacts/{cid}")
    assert get_r.status_code == 404
```

Note: `GET /api/profiles/{id}/contacts/{cid}` after profile deletion returns 404 because `ContactService.get_contact` calls `profile_exists` first, which returns `False`, raising `ValueError` → `HTTPException(404)`.

### Files to Modify

- `app/adapters/sqlite_database.py` — add preconditions + logging

### Files to Add/Modify Tests

- `tests/api/test_profiles.py` — add cascade integration test

### Architecture Rules

- Assertions are Tiger Style programmer invariants — never convert to `ValueError` here.
- `logger.exception` inside `except Exception` blocks only — do not add logging elsewhere in this story.
- No business logic changes. This is a hygiene story only.

### References

- [Source: Epic 1 Retro — _bmad-output/stories/epic-1-retro-2026-04-24.md § Pre-Epic 2 Cleanup]
- [Source: app/adapters/sqlite_database.py — all methods requiring preconditions]
- [Source: app/constants/limits.py — MAX_ENTRIES_PER_SECTION already present on line 5]
- [Source: tests/api/test_profiles.py — profile API integration tests]
- [Source: tests/conftest.py — http_client fixture with contact service override]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

N/A

### Completion Notes List

- All 9 `profile_id > 0` / `contact_id > 0` precondition assertions added to `SQLiteDatabaseAdapter` methods (Tiger Style).
- `import logging` + `logger = logging.getLogger(__name__)` added at module level; `logger.exception(...)` before every `raise` in all 7 `except Exception` blocks.
- `test_delete_profile_cascades_contacts` added to `tests/api/test_profiles.py` — creates profile + contact, deletes profile, confirms 404 on contact GET.
- `MAX_ENTRIES_PER_SECTION = 100` confirmed present at `app/constants/limits.py:5` — no change needed.
- All tests pass, lint clean, type check clean (verified via git commits c4e7331, c026823, f52d609, b2c6ffc, d56e0c2).

### File List

- `app/adapters/sqlite_database.py` (modified — preconditions + logging)
- `tests/api/test_profiles.py` (modified — cascade integration test)

### Change Log

- 2026-04-24: Added precondition assertions to all SQLiteDatabaseAdapter methods (AC 1)
- 2026-04-24: Added structured logging to all except blocks (AC 2)
- 2026-04-24: Added cascade integration test for profile delete (AC 3)
- 2026-04-24: Verified MAX_ENTRIES_PER_SECTION exists (AC 4); all tests and lint pass (AC 5, 6)
