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

- **W7: Race condition in section/entry limit enforcement** [`app/services/sections/experience_service.py`] — `count_*` and `create_*` are separate DB round-trips with no locking. SQLite write serialization mitigates in practice; requires `SELECT FOR UPDATE` or DB-level constraint to fix, same as De1 from story 1-5.
- **W8: `update_experience_section` post-commit re-fetch uses only `section_id` without `profile_id` scope** [`app/adapters/sqlite_database.py`] — Safe because section PK is unique, but inconsistent with the preceding scoped query. Tighten to `.where(ExperienceSection.id == section.id, ExperienceSection.profile_id == profile_id)` in a future cleanup.
- **W9: Cascade integration test cannot directly verify `experience_entries` row deletion** [`tests/api/test_profiles.py`] — No `GET /entries/{id}` endpoint exists; ORM cascade is defined correctly on `ExperienceSection.entries`. Add verification if a list-entries API is added in a future story.
