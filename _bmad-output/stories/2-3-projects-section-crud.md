# Story 2.3: Projects Section CRUD

Status: review

## Story

As a user,
I want to add, view, edit, delete, and toggle project entries on a profile,
so that I can showcase my personal and professional projects.

## Acceptance Criteria

1. Full CRUD via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/projects` and `/{section_id}`.
2. Entry sub-resource for bullet points: `POST/PATCH/DELETE .../projects/{section_id}/entries`.
3. `is_enabled` toggle works (PATCH with `{"is_enabled": false/true}`).
4. `ProjectSection` and `ProjectEntry` SQLAlchemy models exist in `app/models/sections/projects.py`, with `Base` imported from `app/models/base.py`.
5. Alembic migration creates `project_sections` and `project_entries` tables (one migration version for both).
6. `ProjectSectionService` in `app/services/sections/projects_service.py` with unit tests in `projects_service.test.py`.
7. Router `app/apis/sections/projects.py` auto-registered via `app/apis/sections/__init__.py`.
8. Tiger Style assertions mirroring Story 2.1/2.2 pattern: `assert profile_id > 0` on all service methods, `assert section_id > 0` where applicable, postcondition `assert result.profile_id == profile_id` on create.

## Tasks / Subtasks

- [x] Task 1: Add projects string-length constants (AC: 4)
  - [x] 1.1 In `app/constants/limits.py`, add: `PROJECT_TITLE_MAX_LEN: Final[int] = 255`, `PROJECT_ORGANISATION_MAX_LEN: Final[int] = 255`, `PROJECT_DATE_MAX_LEN: Final[int] = 20`, `PROJECT_ENTRY_CONTENT_MAX_LEN: Final[int] = 1000`

- [x] Task 2: Add `ProjectSectionRepositoryProtocol` to `app/interfaces/database.py` (AC: 6)
  - [x] 2.1 Add TYPE_CHECKING imports for all project schemas
  - [x] 2.2 Add `ProjectSectionRepositoryProtocol(Protocol)` with methods: `profile_exists`, `create_project_section`, `list_project_sections`, `get_project_section`, `update_project_section`, `delete_project_section`, `create_entry`, `list_entries`, `update_entry`, `delete_entry`, `count_entries`, `count_sections_for_profile`

- [x] Task 3: Create projects ORM models (AC: 4)
  - [x] 3.1 `app/models/sections/__init__.py` **already exists** — skip creation
  - [x] 3.2 Create `app/models/sections/projects.py` with `ProjectSection` and `ProjectEntry` classes
  - [x] 3.3 Add `project_sections` relationship to `Profile` in `app/models/profile.py` (mirroring `experience_sections` and `education_sections` already there)

- [x] Task 4: Create Alembic migration (AC: 5)
  - [x] 4.1 Run: `docker compose run --rm app alembic revision --autogenerate -m "add project section tables"`
  - [x] 4.2 Apply: `docker compose run --rm app alembic upgrade head`

- [x] Task 5: Create Pydantic schemas (AC: 6)
  - [x] 5.1 `app/schemas/sections/__init__.py` **already exists** — skip creation
  - [x] 5.2 Create `app/schemas/sections/projects.py` with: `ProjectSectionCreate`, `ProjectSectionRead`, `ProjectSectionUpdate`, `ProjectEntryCreate`, `ProjectEntryRead`, `ProjectEntryUpdate`

- [x] Task 6: Implement `ProjectSectionService` (AC: 6, 8)
  - [x] 6.1 `app/services/sections/__init__.py` **already exists** — skip creation
  - [x] 6.2 Create `app/services/sections/projects_service.py`

- [x] Task 7: Add projects methods to `SQLiteDatabaseAdapter` (AC: 1, 2, 3)
  - [x] 7.1 Add all `ProjectSectionRepositoryProtocol` method implementations to `app/adapters/sqlite_database.py`

- [x] Task 8: Create unit tests (AC: 6)
  - [x] 8.1 Create `app/services/sections/projects_service.test.py` with `FakeProjectSectionRepository` and full test coverage

- [x] Task 9: Create router and wire DI (AC: 7)
  - [x] 9.1 Create `app/apis/sections/projects.py`
  - [x] 9.2 Add `from app.apis.sections.projects import router as projects_router` and `sections_router.include_router(projects_router)` to `app/apis/sections/__init__.py`
  - [x] 9.3 Add `get_project_section_service` to `app/apis/dependencies.py`

- [x] Task 10: Verify (AC: all)
  - [x] 10.1 Run `make test-local` — all tests pass
  - [x] 10.2 Run `make lint-local` — clean
  - [x] 10.3 Run `make typecheck-local` — no errors

## Dev Notes

### Story 2.2 Status: MERGED TO MAIN

Story 2.2 is fully merged. All scaffolding is live in `main`. The following **already exist** — do not recreate:
- `app/models/sections/__init__.py`
- `app/models/sections/experience.py`
- `app/models/sections/education.py`
- `app/services/sections/__init__.py`
- `app/services/sections/experience_service.py`, `experience_service.test.py`
- `app/services/sections/education_service.py`, `education_service.test.py`
- `app/schemas/sections/__init__.py`
- `app/schemas/sections/experience.py`
- `app/schemas/sections/education.py`
- `app/apis/sections/__init__.py` (already wires `experience_router` and `education_router`)
- `SectionLimitExceededError` and `EntryLimitExceededError` in `app/exceptions.py`
- `experience_sections` and `education_sections` relationships on `Profile`

### Exact File Paths

| File | Action |
|------|--------|
| `app/constants/limits.py` | Add 4 new constants |
| `app/interfaces/database.py` | Add `ProjectSectionRepositoryProtocol` |
| `app/models/sections/projects.py` | Create — `ProjectSection`, `ProjectEntry` |
| `app/models/profile.py` | Add `project_sections` relationship |
| `app/schemas/sections/projects.py` | Create — 6 schema classes |
| `app/services/sections/projects_service.py` | Create — `ProjectSectionService` |
| `app/services/sections/projects_service.test.py` | Create — full test suite |
| `app/adapters/sqlite_database.py` | Add projects imports + CRUD methods |
| `app/apis/sections/projects.py` | Create — FastAPI router |
| `app/apis/sections/__init__.py` | Register `projects_router` |
| `app/apis/dependencies.py` | Add `get_project_section_service` |
| `alembic/versions/<hash>_add_project_section_tables.py` | Generated by alembic |

### Model Schema

**`project_sections` table columns:**
- `id` — int, PK, autoincrement
- `profile_id` — int, FK → `profiles.id`, not nullable
- `title` — str (project name, e.g. "CVMaker"), max `PROJECT_TITLE_MAX_LEN`, not nullable
- `organisation` — str | None (company or "Personal"), max `PROJECT_ORGANISATION_MAX_LEN`, nullable
- `start_date` — str | None (text, e.g. "2024"), max `PROJECT_DATE_MAX_LEN`, nullable
- `end_date` — str | None (text, nullable — use None for "Present"), max `PROJECT_DATE_MAX_LEN`, nullable
- `is_enabled` — bool, default True, not nullable
- `display_order` — int, default 0, not nullable
- `created_at` — DateTime(timezone=True), default `_utcnow`
- `updated_at` — DateTime(timezone=True), default `_utcnow`, onupdate `_utcnow`

**`project_entries` table columns:**
- `id` — int, PK, autoincrement
- `section_id` — int, FK → `project_sections.id`, not nullable
- `content` — str (bullet point text), max `PROJECT_ENTRY_CONTENT_MAX_LEN`, not nullable
- `display_order` — int, default 0, not nullable

Column layout is identical to `experience_sections`/`education_sections`. `title` = project name, `organisation` = company or affiliation (nullable).

### ORM Pattern (mirror `app/models/sections/education.py`)

```python
# app/models/sections/projects.py
from __future__ import annotations
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.constants.limits import (
    PROJECT_DATE_MAX_LEN,
    PROJECT_ENTRY_CONTENT_MAX_LEN,
    PROJECT_ORGANISATION_MAX_LEN,
    PROJECT_TITLE_MAX_LEN,
)
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile

def _utcnow() -> datetime:
    return datetime.now(tz=UTC)

class ProjectSection(Base):
    __tablename__ = "project_sections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(PROJECT_TITLE_MAX_LEN), nullable=False)
    organisation: Mapped[str | None] = mapped_column(String(PROJECT_ORGANISATION_MAX_LEN), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(PROJECT_DATE_MAX_LEN), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(PROJECT_DATE_MAX_LEN), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
    entries: Mapped[list[ProjectEntry]] = relationship("ProjectEntry", cascade="all, delete-orphan")
    profile: Mapped[Profile] = relationship("Profile", back_populates="project_sections")

class ProjectEntry(Base):
    __tablename__ = "project_entries"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("project_sections.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(PROJECT_ENTRY_CONTENT_MAX_LEN), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
```

### Profile Model Update

`app/models/profile.py` already has `experience_sections` and `education_sections`. Add `project_sections` the same way:

```python
# Add to TYPE_CHECKING block:
if TYPE_CHECKING:
    from app.models.sections.projects import ProjectSection  # add this line
    # existing imports remain

# Add to Profile class body (after education_sections):
project_sections: Mapped[list[ProjectSection]] = relationship(
    "ProjectSection", cascade="all, delete-orphan", back_populates="profile"
)
```

### Protocol Interface Pattern

Add after `EducationSectionRepositoryProtocol` in `app/interfaces/database.py`. Pattern is identical — swap type names:

```python
@runtime_checkable
class ProjectSectionRepositoryProtocol(Protocol):
    async def profile_exists(self, profile_id: int) -> bool: ...
    async def create_project_section(self, profile_id: int, data: ProjectSectionCreate) -> ProjectSectionRead: ...
    async def list_project_sections(self, profile_id: int) -> list[ProjectSectionRead]: ...
    async def get_project_section(self, profile_id: int, section_id: int) -> ProjectSectionRead | None: ...
    async def update_project_section(self, profile_id: int, section_id: int, data: ProjectSectionUpdate) -> ProjectSectionRead | None: ...
    async def delete_project_section(self, profile_id: int, section_id: int) -> bool: ...
    async def create_entry(self, section_id: int, data: ProjectEntryCreate) -> ProjectEntryRead: ...
    async def list_entries(self, section_id: int) -> list[ProjectEntryRead]: ...
    async def update_entry(self, section_id: int, entry_id: int, data: ProjectEntryUpdate) -> ProjectEntryRead | None: ...
    async def delete_entry(self, section_id: int, entry_id: int) -> bool: ...
    async def count_entries(self, section_id: int) -> int: ...
    async def count_sections_for_profile(self, profile_id: int) -> int: ...
```

Add to the `TYPE_CHECKING` block at the top of `database.py`:
```python
from app.schemas.sections.projects import (
    ProjectEntryCreate,
    ProjectEntryRead,
    ProjectEntryUpdate,
    ProjectSectionCreate,
    ProjectSectionRead,
    ProjectSectionUpdate,
)
```

### Schema Pattern

`app/schemas/sections/projects.py` — mirror `app/schemas/sections/education.py` exactly. Class names change; field names identical (`title`, `organisation`, `start_date`, `end_date`). Use `PROJECT_*` constants.

Key rule: `model_config = ConfigDict(from_attributes=True)` on `ProjectSectionRead` and `ProjectEntryRead` only (not Create/Update).

### Service Pattern

`ProjectSectionService` is a direct rename of `EducationSectionService` — all method names change `education` → `project`. Constructor takes `ProjectSectionRepositoryProtocol`. Same limits, same assertion patterns, same error types.

Tiger Style (every method):
- `assert profile_id > 0` on all methods
- `assert section_id > 0` on section/entry ops
- `assert entry_id > 0` on entry ops
- `assert result.profile_id == profile_id` after section create
- `assert result.section_id == section_id` after entry create

### SQLiteDatabaseAdapter Pattern

**Add imports at top of `app/adapters/sqlite_database.py`** alongside existing education imports:
```python
from app.models.sections.projects import ProjectEntry, ProjectSection
from app.schemas.sections.projects import (
    ProjectEntryCreate,
    ProjectEntryRead,
    ProjectEntryUpdate,
    ProjectSectionCreate,
    ProjectSectionRead,
    ProjectSectionUpdate,
)
```

**Critical adapter patterns** (confirmed from actual merged code — replicate exactly):

1. **`_project_section_to_read` static method** — dict-based constructor, NOT `model_validate(orm_obj)` directly:
   ```python
   @staticmethod
   def _project_section_to_read(section: ProjectSection) -> ProjectSectionRead:
       return ProjectSectionRead.model_validate({
           "id": section.id,
           "profile_id": section.profile_id,
           "title": section.title,
           "organisation": section.organisation,
           "start_date": section.start_date,
           "end_date": section.end_date,
           "is_enabled": section.is_enabled,
           "display_order": section.display_order,
           "created_at": section.created_at,
           "updated_at": section.updated_at,
           "entries": [],
       })
   ```

2. **`get_project_section`** — use `selectinload` for eager-loading entries, then `model_validate(orm_obj)`:
   ```python
   stmt = (
       select(ProjectSection)
       .options(selectinload(ProjectSection.entries))
       .where(ProjectSection.id == section_id, ProjectSection.profile_id == profile_id)
   )
   result = await self._session.execute(stmt)
   section = result.scalar_one_or_none()
   if section is None:
       return None
   return ProjectSectionRead.model_validate(section)
   ```

3. **`update_project_section`** — after commit, re-fetch with **both** `section_id` AND `profile_id` in the WHERE clause (fix from 2.2 review W8):
   ```python
   refreshed = await self._session.execute(
       select(ProjectSection)
       .options(selectinload(ProjectSection.entries))
       .where(ProjectSection.id == section.id, ProjectSection.profile_id == profile_id)
   )
   return ProjectSectionRead.model_validate(refreshed.scalar_one())
   ```

4. **`count_sections_for_profile`** — counts only `project_sections`:
   ```python
   result = await self._session.execute(
       select(func.count()).select_from(ProjectSection).where(ProjectSection.profile_id == profile_id)
   )
   count = result.scalar() or 0
   assert count >= 0, "count_sections_for_profile must return non-negative"
   return count
   ```

5. **`profile_exists`** — already implemented on `SQLiteDatabaseAdapter`; no new implementation needed.

6. Every `except Exception` block: `logger.exception(...)` then `await self._session.rollback()` then `raise`.

### Router Pattern

`app/apis/sections/projects.py` — identical to `app/apis/sections/education.py`. Rename education → project:
- Prefix: `/api/profiles/{profile_id}/sections/projects`
- Tags: `["projects"]`
- `ServiceDep = Annotated[ProjectSectionService, Depends(get_project_section_service)]`
- `SectionLimitExceededError` → HTTP 422; `ValueError` → HTTP 404

### Auto-Registration

`app/apis/sections/__init__.py` currently contains:
```python
from fastapi import APIRouter
from app.apis.sections.education import router as education_router
from app.apis.sections.experience import router as experience_router

sections_router = APIRouter()
sections_router.include_router(experience_router)
sections_router.include_router(education_router)
```

Add:
```python
from app.apis.sections.projects import router as projects_router
sections_router.include_router(projects_router)
```

### DI Wiring

`app/apis/dependencies.py` — add alongside existing `get_education_section_service`:
```python
from app.services.sections.projects_service import ProjectSectionService

async def get_project_section_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ProjectSectionService:
    adapter = make_sqlite_adapter(session)
    return ProjectSectionService(adapter)
```

### Unit Test Pattern

`app/services/sections/projects_service.test.py` — `FakeProjectSectionRepository` mirrors `FakeEducationSectionRepository` in `app/services/sections/education_service.test.py`. Read that file as the canonical template.

Test suite MUST cover (all required by review findings from 2.2):
- Section CRUD happy paths
- Section limit exceeded raises `SectionLimitExceededError`
- Entry CRUD happy paths
- Entry limit exceeded raises `EntryLimitExceededError`
- Profile-not-found raises `ValueError` on **every** service method (including `list_project_sections`, `list_entries`)
- Cross-profile access prevention (section belongs to profile 1; profile 2 cannot create/update/delete entries on it)
- Tiger Style assertion failures for zero ids — **must include**:
  - `list_project_sections(profile_id=0)` → AssertionError
  - `list_entries(section_id=0)` → AssertionError (this was a gap caught in 2.2 review)
- `get_project_section` returns populated entries; `list_project_sections` returns `entries=[]`

### Tiger Style Requirements

Every service method:
- Precondition: `assert profile_id > 0` (all), `assert section_id > 0` (section ops), `assert entry_id > 0` (entry ops)
- Postcondition on create: `assert result.profile_id == profile_id` (section create), `assert result.section_id == section_id` (entry create)

Every adapter method:
- Precondition: same assertions
- Error handling: `logger.exception("...")` before every `raise` in `except` blocks

### Existing Errors to Reuse

`app/exceptions.py` contains:
```python
class SectionLimitExceededError(ValueError): pass
class EntryLimitExceededError(ValueError): pass
```

Do NOT create new exception classes — reuse `SectionLimitExceededError` and `EntryLimitExceededError`.

### Alembic Migration

Run AFTER models are created:
```bash
docker compose run --rm app alembic revision --autogenerate -m "add project section tables"
docker compose run --rm app alembic upgrade head
```

Migration must create both `project_sections` and `project_entries` in one revision. Verify the generated file references `profiles.id` as FK target for `project_sections.profile_id`.

### Common Mistakes to Avoid

1. **Do NOT call `declarative_base()` in the model file** — import `Base` from `app/models/base.py` only.
2. **Do NOT add `project_sections` to Profile without `if TYPE_CHECKING` guard** for the import — circular import risk.
3. **Do NOT register the router directly in `main.py`** — only in `apis/sections/__init__.py`.
4. **Do NOT use `os.environ` in any new file** — all config via `app/configs/settings.py`.
5. **Do NOT forget `model_config = ConfigDict(from_attributes=True)`** on `ProjectSectionRead` and `ProjectEntryRead` only.
6. **Do NOT use `model_validate(orm_obj)` in `_project_section_to_read`** — use the dict-based approach (matches experience/education pattern).
7. **Do NOT swallow exceptions** — every `except Exception` block must `logger.exception(...)` then `raise`.
8. **Do NOT skip `selectinload`** in `get_project_section` and `update_project_section` — entries will be empty without it.
9. **Do NOT scope `update_project_section` re-fetch with only `section_id`** — include `profile_id` in the WHERE clause (fix from 2.2 review W8).
10. **Do NOT skip the zero-id Tiger Style tests** for `list_project_sections` and `list_entries` (gap caught in 2.2 review).

### Project Structure (post story 2.2 merge)

These directories and files exist on `main`:
- `app/models/sections/` — `__init__.py`, `experience.py`, `education.py`
- `app/services/sections/` — `__init__.py`, `experience_service.py`, `experience_service.test.py`, `education_service.py`, `education_service.test.py`
- `app/schemas/sections/` — `__init__.py`, `experience.py`, `education.py`
- `app/apis/sections/` — `__init__.py`, `experience.py`, `education.py`

This story adds parallel `projects.py` (and `projects_service.py`, `projects_service.test.py`) files. No new directories needed.

### References (actual paths on main)

- `app/models/sections/education.py` — ORM model pattern (canonical for this story)
- `app/services/sections/education_service.py` — service pattern
- `app/services/sections/education_service.test.py` — test pattern (FakeRepo + all test cases)
- `app/apis/sections/education.py` — router pattern
- `app/apis/sections/__init__.py` — auto-registration pattern
- `app/apis/dependencies.py` — DI wiring pattern
- `app/interfaces/database.py` — protocol pattern (EducationSectionRepositoryProtocol is the latest addition)
- `app/schemas/sections/education.py` — schema pattern
- `app/constants/limits.py` — existing constants
- `app/adapters/sqlite_database.py` — adapter (education methods are most recent; follow those patterns)

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

None.

### Completion Notes List

- Implemented via subagent-driven-development on branch `story/2-3-projects-section-crud`
- `migrations/env.py` required a fix to register `ProjectSection`/`ProjectEntry` with Alembic metadata (missing import discovered in Task 2 review)
- Alembic auto-generate included false-positive FK ops on `profile_contacts` (SQLite ALTER constraint limitation); these were removed from the migration before applying
- Ruff auto-fix updated imports to `X | Y` union syntax in migration file (style only)
- All 206 tests pass, lint clean, typecheck clean

### File List

- `app/constants/limits.py` — added 4 PROJECT_* constants
- `app/interfaces/database.py` — added ProjectSectionRepositoryProtocol
- `app/models/sections/projects.py` — created ProjectSection, ProjectEntry ORM models
- `app/models/profile.py` — added project_sections relationship
- `app/schemas/sections/projects.py` — created 6 Pydantic schema classes
- `app/services/sections/projects_service.py` — created ProjectSectionService
- `app/services/sections/projects_service.test.py` — 42 unit tests
- `app/adapters/sqlite_database.py` — added 12 project adapter methods
- `app/apis/sections/projects.py` — created FastAPI router (8 endpoints)
- `app/apis/sections/__init__.py` — registered projects_router
- `app/apis/dependencies.py` — added get_project_section_service
- `migrations/env.py` — added project models import for Alembic metadata
- `migrations/versions/34a634dca953_add_project_section_tables.py` — Alembic migration

## Review Findings

> Reviewed 2026-05-01. Blind Hunter + Edge Case Hunter (Acceptance Auditor timed out — AC audit done inline).
> AC inline audit: AC1–AC8 all PASS except AC2 (no GET entries route) and AC8 (`update_entry`/`delete_entry` missing `profile_exists` assertion).

### Decision-Needed

_(all resolved)_

- [x] [Review][Decision→Patch] Missing `GET /{section_id}/entries` endpoint — resolved: add the route now
- [x] [Review][Decision→Patch] `ProjectEntry` missing `created_at`/`updated_at` timestamps — resolved: add timestamps + migration

### Patches

- [x] [Review][Patch] Add `GET /{section_id}/entries` endpoint (list entries route) [`app/apis/sections/projects.py`]
- [x] [Review][Patch] Add `created_at`/`updated_at` timestamps to `ProjectEntry` model + new Alembic migration [`app/models/sections/projects.py`]
- [x] [Review][Patch] `update_entry`/`delete_entry` skip `profile_exists` check — inconsistent with all other service methods; `update_entry` and `delete_entry` go straight to section lookup without verifying the profile exists [`app/services/sections/projects_service.py:105,119`]
- [x] [Review][Patch] `ProjectSectionUpdate.title` is `str | None` — PATCH `{"title": null}` accepted by Pydantic, passed via `exclude_unset=True`, sets DB column to NULL, triggers NOT NULL violation on commit [`app/schemas/sections/projects.py:53`]
- [x] [Review][Patch] `update_project_section` re-fetch uses `scalar_one()` — if section deleted between commit and re-fetch, raises unhandled `NoResultFound` (500) instead of graceful 404 [`app/adapters/sqlite_database.py:269`]
- [x] [Review][Patch] `ProjectEntry` missing `back_populates` on entries relationship — `ProjectSection.entries` has no `back_populates='section'`; `ProjectEntry` has no `section` attribute [`app/models/sections/projects.py:736`]
- [x] [Review][Patch] `display_order` allows negative integers on both section and entry schemas — add `ge=0` [`app/schemas/sections/projects.py:21,62`]
- [x] [Review][Patch] `start_date`/`end_date` allow empty string `""` — add `min_length=1` [`app/schemas/sections/projects.py:18-19`]
- [x] [Review][Patch] Non-deterministic ordering when `display_order` values tie — add secondary `.order_by(..., ProjectSection.id)` / `.order_by(..., ProjectEntry.id)` [`app/adapters/sqlite_database.py:213,333`]
- [x] [Review][Patch] `organisation` allows empty string `""` — add `min_length=1` (same as W4 from 2.2 education) [`app/schemas/sections/projects.py:17`]
- [x] [Review][Patch] Test limit-exceeded tests directly inject entries with hardcoded IDs that may collide with IDs already consumed by section creation [`app/services/sections/projects_service.test.py:1210-1214`]
- [x] [Review][Patch] `migrations/env.py` inconsistent `noqa` comments — experience line had `noqa: F401` removed, projects line added it, education line has neither [`migrations/env.py:1442-1445`]

### Deferred

- [x] [Review][Defer] `count_project_entries` and `list_project_entries` adapter methods take only `section_id` — no `profile_id` guard at adapter/protocol level; safe via service enforcement but unguarded for future direct callers [`app/adapters/sqlite_database.py:296,327`] — deferred, pre-existing pattern (same as W4 from 2.1)
- [x] [Review][Defer] Concurrent TOCTOU race on section/entry count checks — `count_*` and `create_*` are separate DB round-trips with no locking; SQLite write serialization mitigates in practice [`app/services/sections/projects_service.py:26,84`] — deferred, pre-existing (same as W7 from 2.1, De1 from 1-5)
- [x] [Review][Defer] IDOR — `profile_id` taken from URL path without ownership check; auth middleware is a stub per CLAUDE.md [`app/apis/sections/projects.py`] — deferred, systemic auth gap known

## Re-Review Findings (2026-05-01)

> Re-reviewed 2026-05-01. All 3 layers: Blind Hunter + Edge Case Hunter + Acceptance Auditor.

### Patches

- [x] [Review][Patch] `ProjectEntryUpdate.content: str | None` has no null-guard validator — `{"content": null}` passes Pydantic, sets NOT NULL DB column to None, triggers unhandled `IntegrityError` → HTTP 500 [`app/schemas/sections/projects.py`]
- [x] [Review][Patch] Router emits `"Section not found"` for all `ValueError` on 5 endpoints (get, update, delete, list_entries, update_entry) — when profile doesn't exist caller gets wrong 404 detail; `create` and `list` already emit `"Profile not found"` correctly [`app/apis/sections/projects.py:69-72,84-87,98-101,113-116,152-155`]
- [x] [Review][Patch] Fake `list_project_sections` sorts only by `display_order` — DB sorts by `(display_order, id)`; tie-break diverges in tests [`app/services/sections/projects_service.test.py:60-63`]
- [x] [Review][Patch] Fake `list_project_entries` is unordered — DB orders by `(display_order, id)` [`app/services/sections/projects_service.test.py:113-114`]
- [x] [Review][Patch] `create_project_entry` adapter missing postcondition `assert result.section_id == section_id` after entry create [`app/adapters/sqlite_database.py` create_project_entry]

### Deferred

- [x] [Review][Defer] No SQLite `PRAGMA foreign_keys=ON` event listener — FK enforcement disabled by default; ORM cascade covers normal paths but raw SQL bypasses it — deferred, pre-existing systemic issue affecting all tables
- [x] [Review][Defer] Migration `34a634dca953` missing `server_default` for `is_enabled`, `display_order`, `created_at`, `updated_at` on `project_sections` — direct SQL inserts without ORM defaults fail — deferred, migration already applied; can't modify applied migration file
- [x] [Review][Defer] No router-level API tests for projects endpoints — deferred, pre-existing gap (education/experience also lack router tests; see W6 from 2.2)
- [x] [Review][Defer] Empty PATCH body triggers unnecessary commit — deferred, pre-existing pattern across all section adapters (see De1 from 1-3)
- [x] [Review][Defer] `_project_section_to_read` always returns `entries=[]` — latent misuse risk if applied to paths expecting populated entries — deferred, by design; same pattern as W2 from 2.2
- [x] [Review][Defer] `assert` guards disabled by Python `-O` flag — deferred, pre-existing systemic issue across entire codebase
- [x] [Review][Defer] SQLite `datetime('now')` server_default in migrations lacks timezone info — inconsistent with `DateTime(timezone=True)` column type — deferred, known SQLite limitation
- [x] [Review][Defer] Two Alembic migrations for `project_entries` instead of one (AC5) — timestamps added as review patch; retroactive merge would break applied-migration checksums — deferred, not fixable without breaking Alembic state
- [x] [Review][Defer] TOCTOU race on section/entry count checks — deferred, already in deferred-work.md W2 from this story

## Third Review Findings (2026-05-01)

> Reviewed 2026-05-01. All 3 layers: Blind Hunter + Edge Case Hunter + Acceptance Auditor. 9 dismissed (hallucinations/false positives).

### Patches

- [ ] [Review][Patch] `create_entry` router hardcodes `"Section not found"` for all `ValueError` — service raises `"Profile {id} not found"` when profile absent, client receives wrong 404 detail [`app/apis/sections/projects.py:136-139`]
- [ ] [Review][Patch] `delete_entry` router hardcodes `"Entry not found"` for all `ValueError` — profile-not-found and section-not-found cases return misleading 404 detail; should use `str(exc)` like the other 5 entry/section endpoints [`app/apis/sections/projects.py:167-170`]

### Deferred

- [x] [Review][Defer] Two Alembic migrations for project tables (AC5 violation) — deferred, pre-existing per Re-Review findings; retroactive merge breaks checksums
- [x] [Review][Defer] TOCTOU race on count+create — deferred, systemic pre-existing issue (W2 this story)
- [x] [Review][Defer] `project_entries` timestamp migration adds `nullable=False` columns without server_default guarantee on old SQLite — deferred, pre-existing
- [x] [Review][Defer] `display_order` has no upper-bound constraint on any project schema — deferred, pre-existing pattern across all section schemas
