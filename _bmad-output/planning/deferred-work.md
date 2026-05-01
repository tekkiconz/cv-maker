# Deferred Work

## Deferred from: code review of 1-2-create-and-list-profiles (2026-04-21)

- **De1: Global engine instantiated at import time** [`app/apis/dependencies.py:11-12`] — `_engine = create_async_engine(settings.database_url, ...)` executes at module import; if env not set, import fails. Known design tradeoff; tests bypass via dependency overrides.
- **De2: `MAX_PROFILES` limit not enforced** [`app/services/profile_service.py`, `app/adapters/sqlite_database.py`] — `MAX_PROFILES = 1000` constant defined in `limits.py` but never checked before insert or in list; unbounded profile creation possible. No story has specified enforcement yet.
- **De3: `OperationalError` propagates as unstructured 500** [`app/adapters/sqlite_database.py:20-27`] — Raw SQLAlchemy `OperationalError` (e.g. DB locked) propagates to client with no structured error response. Cross-cutting error handling concern; needs a global exception handler story.

## Deferred from: code review of 1-2-create-and-list-profiles (2026-04-23)

- **De1: Dead `DatabaseProtocol` generic methods** [`app/adapters/sqlite_database.py:14-29`, `app/interfaces/database.py:11-19`] — `connect`, `disconnect`, `execute`, `fetch_one`, `fetch_all` implemented in adapter but never called by any service. `ProfileService` uses `ProfileRepositoryProtocol` only. Remove or use in a future story that needs raw query access.

## Deferred from: code review of 1-3-edit-profile-details (2026-04-23)

- **De1: Empty PATCH body (`{}`) skips write and `updated_at` refresh** [`app/adapters/sqlite_database.py`] — When `ProfileUpdate` has no fields set, the adapter returns the existing record without issuing any UPDATE statement. `updated_at` is not refreshed and the caller cannot distinguish a real update from a no-op. Spec does not cover this edge case; acceptable for now but may need a dedicated response shape or HTTP 204 in a future story.

## Deferred from: code review of 1-5-manage-profile-contacts (2026-04-24)

- **De1: TOCTOU race on contact count check** [`app/adapters/sqlite_database.py` create_contact] — `SELECT COUNT` then `INSERT` with no locking. SQLite write serialization mitigates in practice; fix requires `SELECT FOR UPDATE` or DB-level unique constraint, out of scope for this story.
- **De2: `ContactRead.model_validate` no exception handling** [`app/adapters/sqlite_database.py`] — A corrupt or legacy DB row with an invalid `type` string causes an uncaught Pydantic `ValidationError` during list/get operations. Pre-existing pattern for all `model_validate` calls in the codebase; needs a global error handling story.
- **De3: No pagination on `list_contacts`** [`app/adapters/sqlite_database.py`] — `SELECT` with no `LIMIT`; bounded by `MAX_CONTACTS_PER_PROFILE=20` today. Pagination is an Epic 2+ concern.
- **De4: DB exceptions from `profile_exists` propagate as unhandled 500** [`app/services/contact_service.py`] — `OperationalError` (DB locked, connection lost) is not caught; same pre-existing pattern as De3 from story 1-2. Needs global exception handler story.
- **De5: Write-time assertion gap for enum type round-trip** [`app/adapters/sqlite_database.py` create_contact] — Adapter postcondition asserts `contact.id is not None` but not that `contact.type` persisted correctly as a valid `ContactType` value. Latent risk; actual StrEnum-to-string storage is correct today.

## Deferred from: code review of 2-1-experience-section-crud (2026-04-24)

- **W1: Migration FK constraints have no `ON DELETE CASCADE`** [`migrations/versions/82e204f0235c_*.py`] — ORM-level cascade handles this for current usage; pre-existing project pattern. Fix requires adding `ondelete="CASCADE"` to FK columns in migration.
- **W2: `display_order` accepts negative integers** [`app/schemas/sections/experience.py`] — No spec requirement for non-negative; no stated ordering semantics require it. Add `ge=0` constraint in a future schema hardening story.
- **W3: `list_entries` method in service/adapter/protocol with no API route** — Spec correctly has no GET-entries endpoint. Method used in tests for state inspection. Remove or expose in a future story if a list-entries API is needed.
- **W4: `count_sections_for_profile`/`count_entries` exposed in Protocol** [`app/interfaces/database.py`] — These are internal limit-check helpers leaked into the public protocol interface. Refactor in a future protocol cleanup story.
- **W5: Tests directly mutate `fake_db._entries`/`fake_db._sections`** [`app/services/sections/experience_service.test.py`] — Fragile test design; bypasses public API of fake. Refactor to use `create_entry`/`create_section` in a loop if fake is ever changed.
- **W6: `start_date`/`end_date` accept arbitrary strings with no format validation** [`app/schemas/sections/experience.py`] — ISO 8601 intent not enforced. Add `pattern=` constraint in a future schema hardening story.

## Deferred from: code review of 2-1-experience-section-crud (2026-04-25)

## Deferred from: code review of 2-2-education-section-crud (2026-04-30)

- **W1: Router collapses profile-not-found and section-not-found into same 404** [`app/apis/sections/education.py`] — `except ValueError` catches both error types and emits identical `"Section not found"` / `"Profile not found"` responses. Pre-existing pattern from experience router. Fix requires typed exception subclasses or structured error payloads.
- **W2: `_education_section_to_read` hardcodes `entries=[]` with no usage guard** [`app/adapters/sqlite_database.py`] — Helper always emits empty entries list; safe for list endpoint but silently wrong if misapplied to a path that expects populated entries. Pre-existing pattern from experience. Add a docstring or `assert` guard if reused.
- **W3: No FK column indexes on `education_sections.profile_id` / `education_entries.section_id`** [`migrations/versions/c8dba486b875_*.py`] — SQLite does not auto-index FK columns; all list/count queries do full table scans. Pre-existing from experience migration. Add explicit `op.create_index` in a future migration.
- **W4: `organisation` field allows empty string on create/update** [`app/schemas/sections/education.py`] — `organisation: str | None` has no `min_length=1`; `""` and `None` are stored differently but semantically equivalent. Add `min_length=1` when empty string should be treated as absent.
- **W5: No integration tests for education adapter methods** — `get_education_section` with `selectinload`, two-query `update_education_section`, and cascade delete have no real-database coverage. Pre-existing gap from experience.
- **W6: No API-level tests for education router** — FastAPI routing, response codes, and error mapping are entirely untested at HTTP boundary. Pre-existing gap from experience.

- **W7: Race condition in section/entry limit enforcement** [`app/services/sections/experience_service.py`] — `count_*` and `create_*` are separate DB round-trips with no locking. SQLite write serialization mitigates in practice; requires `SELECT FOR UPDATE` or DB-level constraint to fix, same as De1 from story 1-5.
- **W8: `update_experience_section` post-commit re-fetch uses only `section_id` without `profile_id` scope** [`app/adapters/sqlite_database.py`] — Safe because section PK is unique, but inconsistent with the preceding scoped query. Tighten to `.where(ExperienceSection.id == section.id, ExperienceSection.profile_id == profile_id)` in a future cleanup.
- **W9: Cascade integration test cannot directly verify `experience_entries` row deletion** [`tests/api/test_profiles.py`] — No `GET /entries/{id}` endpoint exists; ORM cascade is defined correctly on `ExperienceSection.entries`. Add verification if a list-entries API is added in a future story.

## Deferred from: code review of 2-3-projects-section-crud (2026-05-01)

- **W1: `count_project_entries`/`list_project_entries` adapter methods take only `section_id` — no `profile_id` guard** [`app/adapters/sqlite_database.py:296,327`] — Safe via service enforcement today; unguarded for future direct callers. Pre-existing pattern (same as W4 from 2.1).
- **W2: Concurrent TOCTOU race on section/entry count checks** [`app/services/sections/projects_service.py:26,84`] — `count_*` then `create_*` with no locking; SQLite write serialization mitigates. Pre-existing (same as W7 from 2.1, De1 from 1-5). Fix requires DB-level CHECK constraint or serialized transaction.
- **W3: IDOR — `profile_id` from URL path trusted without ownership check** [`app/apis/sections/projects.py`] — Auth middleware is a stub per CLAUDE.md. Systemic gap; fix requires auth implementation story.

## Deferred from: re-review of 2-3-projects-section-crud (2026-05-01)

- **W4: No SQLite `PRAGMA foreign_keys=ON` event listener** [`app/adapters/factories.py`] — FK enforcement disabled by default; ORM cascade covers normal paths but raw SQL or bulk operations leave orphaned rows. Pre-existing systemic issue affecting all tables.
- **W5: Migration `34a634dca953` missing `server_default` for NOT NULL columns** [`migrations/versions/34a634dca953_add_project_section_tables.py`] — `is_enabled`, `display_order`, `created_at`, `updated_at` on `project_sections` have no `server_default`; direct SQL inserts without ORM defaults fail with NOT NULL violation. Migration already applied; cannot change in-place.
- **W6: No router-level API tests for projects** — `tests/api/` has no `test_projects.py`; HTTP routing, path-param validation, error mapping all untested at boundary. Pre-existing gap matching education/experience (W6 from 2.2).
- **W7: Empty PATCH body triggers unnecessary DB commit** [`app/adapters/sqlite_database.py` update_project_section] — `model_dump(exclude_unset=True)` returns `{}`; loop is no-op but `commit()` still fires. Pre-existing pattern across all section adapters (De1 from 1-3).
- **W8: `_project_section_to_read` latent misuse risk — always returns `entries=[]`** [`app/adapters/sqlite_database.py`] — Correct for list/create paths; silently wrong if applied to a path expecting populated entries. Same pattern as W2 from 2.2. Add docstring guard.
- **W9: `assert` guards disabled by Python `-O` flag** — Tiger Style assertions stripped at `PYTHONOPTIMIZE=1`; invalid IDs bypass all guards. Pre-existing systemic issue across entire codebase.
- **W10: SQLite `datetime('now')` server_default lacks timezone info** — `DateTime(timezone=True)` columns get naive datetimes from migration server defaults. Known SQLite limitation; rows inserted via ORM are fine.
- **W11: Two Alembic migrations for project_entries timestamps instead of one** — AC5 requires one migration for both tables; timestamps were added as a review patch in a second revision. Cannot retroactively merge without breaking Alembic checksums on applied DBs.

## Deferred from: code review of 2-3-projects-section-crud fourth review (2026-05-01)

- **W12: Missing DB indexes on FK columns** [`migrations/versions/34a634dca953_add_project_section_tables.py`] — `profile_id` on `project_sections` and `section_id` on `project_entries` have no explicit indexes; SQLite won't auto-create FK indexes; full table scan on every list/get/update/delete query. Same pattern in experience/education migrations (W3 from 2.2). Add explicit `op.create_index` in a future migration.
- **W13: `update_project_section` concurrent-delete race — 404 for successful mutation** [`app/adapters/sqlite_database.py`] — After commit, re-fetch returns None if section was concurrently deleted; service raises ValueError → caller gets 404 even though the update succeeded. Variant of TOCTOU family (W2 this story). `session.refresh()` with eager-load options would resolve this.
- **W14: `list_entries` double-query — loads full section with entries for ownership check, discards them, then issues separate `list_project_entries` query** [`app/services/sections/projects_service.py`] — Two DB round-trips where one would suffice. Pre-existing pattern across section services.
- **W15: `_utcnow` duplicated across all model files** [`app/models/sections/projects.py`] — Identical function in every section model file. Extract to `app/models/base.py` or a shared utility in a future model cleanup.
