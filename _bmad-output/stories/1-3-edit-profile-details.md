# Story 1.3: Edit Profile Details

Status: done

## Story

As a user,
I want to update a profile's name and description, and retrieve a single profile by ID,
so that I can rename or re-describe a profile as my needs evolve.

## Acceptance Criteria

1. `PATCH /api/profiles/{profile_id}` with `{"name": "new name"}` updates the profile name and returns the updated profile.
2. `PATCH /api/profiles/{profile_id}` with `{"description": "new description"}` updates only the description.
3. `PATCH /api/profiles/{profile_id}` with both fields updates both.
4. `PATCH /api/profiles/{profile_id}` for a non-existent `profile_id` returns HTTP 404.
5. `GET /api/profiles/{profile_id}` returns a single profile by ID with HTTP 200, or HTTP 404 if not found.
6. `updated_at` is updated on every successful PATCH.
7. `ProfileService.update_profile()` is implemented and tested in `app/services/profile_service.test.py`.
8. Tiger Style: `update_profile()` asserts `profile_id` is a positive integer on input, and asserts the returned profile's `updated_at >= created_at` after update.

## Tasks / Subtasks

- [x] Task 1: Add `ProfileUpdate` Pydantic schema (AC: 1, 2, 3)
  - [x] 1.1 Add `ProfileUpdate` to `app/schemas/profile.py`: `name: ProfileName | None = None`, `description: str | None = Field(default=None, max_length=PROFILE_DESCRIPTION_MAX_LEN)`. Both fields optional — the caller sends only what they want to change.

- [x] Task 2: Extend `ProfileRepositoryProtocol` (AC: 5, 7)
  - [x] 2.1 Add `get_profile(self, profile_id: int) -> ProfileRead | None` to `ProfileRepositoryProtocol` in `app/interfaces/database.py`
  - [x] 2.2 Add `update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None` to `ProfileRepositoryProtocol`

- [x] Task 3: Implement `get_profile` and `update_profile` in `SQLiteDatabaseAdapter` (AC: 1–6)
  - [x] 3.1 Implement `get_profile(self, profile_id: int) -> ProfileRead | None` — fetch by primary key, return `ProfileRead.model_validate(profile)` if found, `None` if not found
  - [x] 3.2 Implement `update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None` — fetch profile, return `None` if not found; apply only fields present in `data.model_fields_set`; commit with rollback on failure; refresh and return `ProfileRead.model_validate(profile)`

- [x] Task 4: Implement `get_profile` and `update_profile` in `ProfileService` (AC: 5, 7, 8)
  - [x] 4.1 Implement `get_profile(self, profile_id: int) -> ProfileRead` — assert `profile_id > 0`; call adapter; raise `ValueError(f"Profile {profile_id} not found")` if adapter returns `None`; assert result is not None (postcondition)
  - [x] 4.2 Implement `update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead` — assert `profile_id > 0` (precondition); call adapter; raise `ValueError(f"Profile {profile_id} not found")` if None; assert `result.updated_at >= result.created_at` (postcondition); return result

- [x] Task 5: Add routes to the profiles router (AC: 1–5)
  - [x] 5.1 Add `GET /api/profiles/{profile_id}` route to `app/apis/profiles.py` — call `service.get_profile(profile_id)`, catch `ValueError` → `HTTPException(status_code=404, detail="Profile not found")`
  - [x] 5.2 Add `PATCH /api/profiles/{profile_id}` route — call `service.update_profile(profile_id, data)`, catch `ValueError` → `HTTPException(status_code=404, detail="Profile not found")`; return 200 with updated profile

- [x] Task 6: Write unit tests for new service methods (AC: 7)
  - [x] 6.1 Extend `FakeDatabase` in `app/services/profile_service.test.py` with `get_profile` and `update_profile` methods
  - [x] 6.2 Test `get_profile` happy path: existing id → returns `ProfileRead`
  - [x] 6.3 Test `get_profile` not found: unknown id → raises `ValueError`
  - [x] 6.4 Test `update_profile` name only: returns profile with new name, unchanged description
  - [x] 6.5 Test `update_profile` description only: returns profile with new description, unchanged name
  - [x] 6.6 Test `update_profile` both fields: returns profile with both updated
  - [x] 6.7 Test `update_profile` not found: unknown id → raises `ValueError`
  - [x] 6.8 Test Tiger Style: `update_profile(0, ...)` → `AssertionError`

- [x] Task 7: Write API integration tests (AC: 1–6)
  - [x] 7.1 Extend `tests/api/test_profiles.py` with `GET /api/profiles/{id}` tests: found → 200 + profile body; not found → 404
  - [x] 7.2 Test `PATCH` name-only update → 200 + updated name, unchanged description
  - [x] 7.3 Test `PATCH` description-only update → 200 + updated description, unchanged name
  - [x] 7.4 Test `PATCH` both fields → 200 + both updated
  - [x] 7.5 Test `PATCH` non-existent id → 404
  - [x] 7.6 Test `updated_at` changes: PATCH response `updated_at >= created_at`

- [x] Task 8: Run full validation (AC: all)
  - [x] 8.1 `make test-local` — all tests pass, no regressions
  - [x] 8.2 `ruff check . && ruff format --check .` — clean
  - [x] 8.3 `mypy app/` — no errors

## Dev Notes

### Schema Design — PATCH Semantics

`ProfileUpdate` must use **optional fields only** so callers can send a subset. Use `data.model_fields_set` (not `model_dump()`) to determine which fields were explicitly provided:

```python
class ProfileUpdate(BaseModel):
    name: ProfileName | None = None
    description: str | None = Field(default=None, max_length=PROFILE_DESCRIPTION_MAX_LEN)
```

`model_fields_set` is the set of field names explicitly included in the request body. Use `data.model_dump(exclude_unset=True)` in the adapter to build the update dict — only keys in this dict are written to the DB:

```python
update_dict = data.model_dump(exclude_unset=True)
for key, value in update_dict.items():
    setattr(profile, key, value)
```

**Edge case**: if someone sends `{"name": null}`, `name` will be `None` in `update_dict`. The SQLAlchemy `nullable=False` column will raise an `IntegrityError` on commit. This is acceptable — it propagates as a 500, which is correct for malformed input not covered by ACs. No special handling needed.

### 404 Error Handling Pattern

Services must NOT import `HTTPException` (HTTP concern). Pattern used throughout this project:
- Adapter returns `None` when record not found
- Service raises `ValueError("Profile {id} not found")`
- Router catches `ValueError` → `HTTPException(status_code=404)`

```python
# In router
try:
    return await service.get_profile(profile_id)
except ValueError:
    raise HTTPException(status_code=404, detail="Profile not found")
```

### `updated_at` Behavior

`Profile.updated_at` uses `onupdate=_utcnow` in the SQLAlchemy model (already in `app/models/profile.py`). SQLAlchemy triggers this on every `UPDATE` statement. After `commit()` + `refresh(profile)`, `profile.updated_at` reflects the update time.

Tiger Style postcondition uses `>=` not `>` — in tests that create and immediately update a profile, microsecond-level timing may produce equal timestamps:

```python
assert result.updated_at >= result.created_at, "updated_at must not precede created_at"
```

### FakeDatabase Extension Pattern

Extend the existing `FakeDatabase` in `profile_service.test.py`. Match the Protocol structurally — no inheritance:

```python
async def get_profile(self, profile_id: int) -> ProfileRead | None:
    return next((p for p in self._profiles if p.id == profile_id), None)

async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None:
    for i, profile in enumerate(self._profiles):
        if profile.id == profile_id:
            updates = data.model_dump(exclude_unset=True)
            now = datetime.now(tz=UTC)
            updated = profile.model_copy(update={**updates, "updated_at": now})
            self._profiles[i] = updated
            return updated
    return None
```

The fake must import `datetime` and `UTC` from `datetime` module.

### Tiger Style Assertions

```python
async def get_profile(self, profile_id: int) -> ProfileRead:
    assert profile_id > 0, "profile_id must be a positive integer"
    result = await self._db.get_profile(profile_id)
    if result is None:
        raise ValueError(f"Profile {profile_id} not found")
    assert result.id == profile_id, "returned profile id must match requested id"
    return result

async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead:
    assert profile_id > 0, "profile_id must be a positive integer"
    result = await self._db.update_profile(profile_id, data)
    if result is None:
        raise ValueError(f"Profile {profile_id} not found")
    assert result.updated_at >= result.created_at, "updated_at must not precede created_at"
    return result
```

### SQLiteDatabaseAdapter — `get_profile` Implementation

Use `session.get()` for primary-key lookup — more efficient than `select().where()`:

```python
async def get_profile(self, profile_id: int) -> ProfileRead | None:
    profile = await self._session.get(Profile, profile_id)
    if profile is None:
        return None
    return ProfileRead.model_validate(profile)
```

### Files to Touch

- `app/schemas/profile.py` — add `ProfileUpdate`
- `app/interfaces/database.py` — add `get_profile`, `update_profile` to `ProfileRepositoryProtocol`
- `app/adapters/sqlite_database.py` — implement `get_profile`, `update_profile`
- `app/services/profile_service.py` — implement `get_profile`, `update_profile`
- `app/apis/profiles.py` — add `GET /{profile_id}` and `PATCH /{profile_id}` routes
- `app/services/profile_service.test.py` — extend `FakeDatabase`, add unit tests
- `tests/api/test_profiles.py` — add integration tests for new endpoints

**Do NOT create new files.** All changes extend existing files from Story 1.2.

### Previous Story Learnings

From Story 1.2 debug log:
- `ruff` dropped `ANN101`/`ANN102` rules — don't add them to ignore list
- `greenlet` is installed — no action needed
- `SQLiteDatabaseAdapter` wraps `commit()` in try/except with rollback — **replicate this pattern** in `update_profile`
- `mypy` resolves Protocol structural match without `# type: ignore`
- `ProfileRead` uses `model_config = ConfigDict(from_attributes=True)` — required for `model_validate(orm_object)`

From Story 1.2 review patches:
- Rollback on commit failure is required (P3 was patched) — do it in `update_profile` too
- All async functions in adapters and services — no sync calls

### Architecture Rules (Non-Negotiable)

- All functions `async def` — no sync in services, adapters, routers
- No business logic in `apis/profiles.py` — only route dispatch, schema parsing, error conversion
- No HTTP imports in `app/services/` — raise `ValueError`, not `HTTPException`
- No `os.environ` — config via `app/configs/settings.py`
- Type hints on all function signatures (mypy enforced)
- Absolute imports only (`from app.schemas.profile import ProfileUpdate`)

### References

- [Source: _bmad-output/planning/epics.md — Story 1.3]
- [Source: _bmad-output/project-context.md — Framework Rules, Tiger Style]
- [Source: app/schemas/profile.py — existing ProfileName, ProfileCreate, ProfileRead]
- [Source: app/adapters/sqlite_database.py — existing commit/rollback pattern]
- [Source: app/interfaces/database.py — ProfileRepositoryProtocol to extend]
- [Source: app/services/profile_service.test.py — FakeDatabase pattern to extend]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

- All 8 tasks complete. 38 tests pass (12 unit + 14 integration + 12 other). Lint and mypy clean.
- ProfileUpdate schema added with PATCH semantics via model_dump(exclude_unset=True).
- Tiger Style: precondition (profile_id > 0) and postconditions (id match, updated_at >= created_at) on service methods.
- B904 lint fix applied: ValueError → HTTPException raises use `from None` to suppress chain.
- Adapter uses session.get() for PK lookup and mirrors existing commit/rollback pattern.

### File List

- app/schemas/profile.py
- app/interfaces/database.py
- app/adapters/sqlite_database.py
- app/services/profile_service.py
- app/services/profile_service.test.py
- app/apis/profiles.py
- tests/api/test_profiles.py

## Review Findings

- [x] [Review][Decision] F1: `profile_id=0` via API produces unhandled `AssertionError` → HTTP 500 — resolved: added `Path(ge=1)` to both `get_profile` and `update_profile` route signatures; assert kept in service as defense-in-depth.
- [x] [Review][Patch] F2: Weak `updated_at` assertion in integration test [tests/api/test_profiles.py:123] — fixed: now compares `body["updated_at"] >= pre_patch_updated_at` instead of against `created_at`.
- [x] [Review][Patch] F3: Missing Tiger Style test for `get_profile(0)` [app/services/profile_service.test.py] — fixed: added `test_get_profile_zero_id_raises_assertion`.
- [x] [Review][Patch] F4: Missing PATCH whitespace-name 422 test [tests/api/test_profiles.py] — fixed: added `test_patch_whitespace_name_returns_422`.
- [x] [Review][Defer] F5: Empty PATCH body (`{}`) skips write and `updated_at` refresh [app/adapters/sqlite_database.py] — deferred, pre-existing design choice; spec does not cover this edge case
