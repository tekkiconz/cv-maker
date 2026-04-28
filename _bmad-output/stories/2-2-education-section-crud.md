# Story 2.2: Education Section CRUD

Status: ready-for-dev

## Story

As a user,
I want to add, view, edit, delete, and toggle education entries on a profile,
so that I can capture my academic background in a structured format.

## Acceptance Criteria

1. Full CRUD for education sections via `POST/GET/PATCH/DELETE /api/profiles/{profile_id}/sections/education` and `/{section_id}`.
2. Entry sub-resource for bullet points: `POST/PATCH/DELETE .../education/{section_id}/entries`.
3. `is_enabled` toggle works (PATCH with `{"is_enabled": false/true}`).
4. `EducationSection` and `EducationEntry` SQLAlchemy models exist in `app/models/sections/education.py`, with `Base` imported from `app/models/base.py`.
5. Alembic migration creates `education_sections` and `education_entries` tables (one migration version for both).
6. `EducationSectionService` in `app/services/sections/education_service.py` with unit tests in `education_service.test.py`.
7. Router `app/apis/sections/education.py` auto-registered via `app/apis/sections/__init__.py`.
8. Tiger Style assertions mirroring Story 2.1 pattern: `assert profile_id > 0` on all service methods, `assert section_id > 0` where applicable, postcondition `assert result.profile_id == profile_id` on create.

## Tasks / Subtasks

- [ ] Task 1: Add education string-length constants (AC: 4)
  - [ ] 1.1 In `app/constants/limits.py`, add: `EDUCATION_TITLE_MAX_LEN: Final[int] = 255`, `EDUCATION_ORGANISATION_MAX_LEN: Final[int] = 255`, `EDUCATION_DATE_MAX_LEN: Final[int] = 20`, `EDUCATION_ENTRY_CONTENT_MAX_LEN: Final[int] = 1000`

- [ ] Task 2: Add `EducationSectionRepositoryProtocol` to `app/interfaces/database.py` (AC: 6)
  - [ ] 2.1 Add TYPE_CHECKING imports for all education schemas
  - [ ] 2.2 Add `EducationSectionRepositoryProtocol(Protocol)` with methods: `profile_exists`, `create_education_section`, `list_education_sections`, `get_education_section`, `update_education_section`, `delete_education_section`, `create_entry`, `list_entries`, `update_entry`, `delete_entry`, `count_entries`, `count_sections_for_profile`

- [ ] Task 3: Create education ORM models (AC: 4)
  - [ ] 3.1 Create `app/models/sections/__init__.py` if not present (may already exist from story 2.1)
  - [ ] 3.2 Create `app/models/sections/education.py` with `EducationSection` and `EducationEntry` classes
  - [ ] 3.3 Add `education_sections` relationship to `Profile` in `app/models/profile.py` (mirroring how `experience_sections` was added)

- [ ] Task 4: Create Alembic migration (AC: 5)
  - [ ] 4.1 Run: `docker compose run --rm app alembic revision --autogenerate -m "add education section tables"`
  - [ ] 4.2 Apply: `docker compose run --rm app alembic upgrade head`

- [ ] Task 5: Create Pydantic schemas (AC: 6)
  - [ ] 5.1 Create `app/schemas/sections/__init__.py` if not present
  - [ ] 5.2 Create `app/schemas/sections/education.py` with: `EducationSectionCreate`, `EducationSectionRead`, `EducationSectionUpdate`, `EducationEntryCreate`, `EducationEntryRead`, `EducationEntryUpdate`

- [ ] Task 6: Implement `EducationSectionService` (AC: 6, 8)
  - [ ] 6.1 Create `app/services/sections/__init__.py` if not present
  - [ ] 6.2 Create `app/services/sections/education_service.py`

- [ ] Task 7: Add education methods to `SQLiteDatabaseAdapter` (AC: 1, 2, 3)
  - [ ] 7.1 Add all `EducationSectionRepositoryProtocol` method implementations to `app/adapters/sqlite_database.py`

- [ ] Task 8: Create unit tests (AC: 6)
  - [ ] 8.1 Create `app/services/sections/education_service.test.py` with `FakeEducationSectionRepository` and full test coverage

- [ ] Task 9: Create router and wire DI (AC: 7)
  - [ ] 9.1 Create `app/apis/sections/education.py`
  - [ ] 9.2 Add `from app.apis.sections.education import router as education_router` and `sections_router.include_router(education_router)` to `app/apis/sections/__init__.py`
  - [ ] 9.3 Add `get_education_section_service` to `app/apis/dependencies.py`

- [ ] Task 10: Verify (AC: all)
  - [ ] 10.1 Run `make test-local` — all tests pass
  - [ ] 10.2 Run `make lint-local` — clean
  - [ ] 10.3 Run `make typecheck-local` — no errors

## Dev Notes

### Dependency on Story 2.1

**Story 2.2 depends on Story 2.1 being merged first.** Story 2.1 establishes:
- `app/models/sections/` directory and `__init__.py`
- `app/services/sections/` directory and `__init__.py`
- `app/schemas/sections/` directory and `__init__.py`
- `SectionLimitExceededError` and `EntryLimitExceededError` in `app/exceptions.py`
- `experience_sections` relationship on `Profile` (and the back_populates pattern to follow)

If story 2.1 is not yet merged, check the `story-2-1-experience-crud` worktree at `.worktrees/story-2-1-experience-crud/` for reference implementations.

### Exact File Paths

| File | Action |
|------|--------|
| `app/constants/limits.py` | Add 4 new constants |
| `app/interfaces/database.py` | Add `EducationSectionRepositoryProtocol` |
| `app/models/sections/education.py` | Create — `EducationSection`, `EducationEntry` |
| `app/models/profile.py` | Add `education_sections` relationship |
| `app/schemas/sections/education.py` | Create — 6 schema classes |
| `app/services/sections/education_service.py` | Create — `EducationSectionService` |
| `app/services/sections/education_service.test.py` | Create — full test suite |
| `app/adapters/sqlite_database.py` | Add education CRUD methods |
| `app/apis/sections/education.py` | Create — FastAPI router |
| `app/apis/sections/__init__.py` | Register `education_router` |
| `app/apis/dependencies.py` | Add `get_education_section_service` |
| `alembic/versions/<hash>_add_education_section_tables.py` | Generated by alembic |

### Model Schema

**`education_sections` table columns:**
- `id` — int, PK, autoincrement
- `profile_id` — int, FK → `profiles.id`, not nullable
- `title` — str (degree name, e.g. "Bachelor of Computer Science"), max `EDUCATION_TITLE_MAX_LEN`, not nullable
- `organisation` — str | None (institution name, e.g. "MIT"), max `EDUCATION_ORGANISATION_MAX_LEN`, nullable
- `start_date` — str | None (text, e.g. "2018"), max `EDUCATION_DATE_MAX_LEN`, nullable
- `end_date` — str | None (text, nullable — use None for "Present"), max `EDUCATION_DATE_MAX_LEN`, nullable
- `is_enabled` — bool, default True, not nullable
- `display_order` — int, default 0, not nullable
- `created_at` — DateTime(timezone=True), default `_utcnow`
- `updated_at` — DateTime(timezone=True), default `_utcnow`, onupdate `_utcnow`

**`education_entries` table columns:**
- `id` — int, PK, autoincrement
- `section_id` — int, FK → `education_sections.id`, not nullable
- `content` — str (bullet point text), max `EDUCATION_ENTRY_CONTENT_MAX_LEN`, not nullable
- `display_order` — int, default 0, not nullable

Note: `education_sections` and `experience_sections` columns are identical (same unified schema). `title` = degree, `organisation` = institution.

### ORM Pattern (follow exactly from story 2.1)

```python
# app/models/sections/education.py
from __future__ import annotations
from datetime import UTC, datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.constants.limits import (
    EDUCATION_DATE_MAX_LEN,
    EDUCATION_ENTRY_CONTENT_MAX_LEN,
    EDUCATION_ORGANISATION_MAX_LEN,
    EDUCATION_TITLE_MAX_LEN,
)
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.profile import Profile

def _utcnow() -> datetime:
    return datetime.now(tz=UTC)

class EducationSection(Base):
    __tablename__ = "education_sections"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(EDUCATION_TITLE_MAX_LEN), nullable=False)
    organisation: Mapped[str | None] = mapped_column(String(EDUCATION_ORGANISATION_MAX_LEN), nullable=True)
    start_date: Mapped[str | None] = mapped_column(String(EDUCATION_DATE_MAX_LEN), nullable=True)
    end_date: Mapped[str | None] = mapped_column(String(EDUCATION_DATE_MAX_LEN), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False)
    entries: Mapped[list[EducationEntry]] = relationship("EducationEntry", cascade="all, delete-orphan")
    profile: Mapped[Profile] = relationship("Profile", back_populates="education_sections")

class EducationEntry(Base):
    __tablename__ = "education_entries"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("education_sections.id"), nullable=False)
    content: Mapped[str] = mapped_column(String(EDUCATION_ENTRY_CONTENT_MAX_LEN), nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
```

### Profile Model Update

Add `education_sections` relationship to `Profile` in `app/models/profile.py`, mirroring the `experience_sections` pattern added in story 2.1:

```python
# In Profile class, inside profile.py
if TYPE_CHECKING:
    from app.models.sections.education import EducationSection  # add to TYPE_CHECKING block
    # (experience import is already there from story 2.1)

education_sections: Mapped[list[EducationSection]] = relationship(
    "EducationSection", cascade="all, delete-orphan", back_populates="profile"
)
```

### Protocol Interface Pattern

Add `EducationSectionRepositoryProtocol` to `app/interfaces/database.py`. Same shape as `ExperienceSectionRepositoryProtocol` — just swap type names:

```python
@runtime_checkable
class EducationSectionRepositoryProtocol(Protocol):
    async def profile_exists(self, profile_id: int) -> bool: ...
    async def create_education_section(self, profile_id: int, data: EducationSectionCreate) -> EducationSectionRead: ...
    async def list_education_sections(self, profile_id: int) -> list[EducationSectionRead]: ...
    async def get_education_section(self, profile_id: int, section_id: int) -> EducationSectionRead | None: ...
    async def update_education_section(self, profile_id: int, section_id: int, data: EducationSectionUpdate) -> EducationSectionRead | None: ...
    async def delete_education_section(self, profile_id: int, section_id: int) -> bool: ...
    async def create_entry(self, section_id: int, data: EducationEntryCreate) -> EducationEntryRead: ...
    async def list_entries(self, section_id: int) -> list[EducationEntryRead]: ...
    async def update_entry(self, section_id: int, entry_id: int, data: EducationEntryUpdate) -> EducationEntryRead | None: ...
    async def delete_entry(self, section_id: int, entry_id: int) -> bool: ...
    async def count_entries(self, section_id: int) -> int: ...
    async def count_sections_for_profile(self, profile_id: int) -> int: ...
```

Note: `count_sections_for_profile` counts ALL section types combined (not just education) to enforce `MAX_SECTIONS_PER_PROFILE`. The experience adapter implementation queries `experience_sections` — the education implementation must query across all section tables, or share the same counter. Simplest approach: the education adapter's `count_sections_for_profile` also counts only education sections for now (this is acceptable in v1 where each section type has its own limit check; the global limit is a future concern). Match whatever story 2.1 implemented.

### Service Pattern

`EducationSectionService` is a direct rename of `ExperienceSectionService`. All method names change `experience` → `education`. Take `EducationSectionRepositoryProtocol` in `__init__`. Same limits, same assertion patterns, same error types.

### SQLiteDatabaseAdapter Pattern

Add education methods to `SQLiteDatabaseAdapter` in `app/adapters/sqlite_database.py`. Follow the exact same pattern as experience methods:
- `assert profile_id > 0` / `assert section_id > 0` at entry
- `logger.exception(...)` before `raise` in every `except Exception` block
- `await self._session.rollback()` in except blocks
- `await self._session.refresh(obj)` after commit
- `assert obj.id is not None` after insert

Import `EducationSection`, `EducationEntry` models and education schemas at top of file.

### Router Pattern

`app/apis/sections/education.py` — identical to `experience.py`, replace experience with education:
- Prefix: `/api/profiles/{profile_id}/sections/education`
- Tags: `["education"]`
- Type aliases: reuse `ProfileId = Annotated[int, Path(ge=1)]` etc.
- `SectionLimitExceededError` → HTTP 422; `ValueError` → HTTP 404

### Auto-Registration

`app/apis/sections/__init__.py` after story 2.1 contains:
```python
from app.apis.sections.experience import router as experience_router
sections_router.include_router(experience_router)
```

Add:
```python
from app.apis.sections.education import router as education_router
sections_router.include_router(education_router)
```

### DI Wiring

`app/apis/dependencies.py` — add:
```python
from app.services.sections.education_service import EducationSectionService

async def get_education_section_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> EducationSectionService:
    adapter = make_sqlite_adapter(session)
    return EducationSectionService(adapter)
```

### Schema Pattern

`app/schemas/sections/education.py` — mirror `experience.py` exactly. Key difference: field names are identical (title, organisation, start_date, end_date) — just the class names change. Use `EDUCATION_*` constants. `ExperienceSectionRead.entries` becomes `EducationSectionRead.entries: list[EducationEntryRead] = []`.

### Unit Test Pattern

`app/services/sections/education_service.test.py` — `FakeEducationSectionRepository` mirrors `FakeExperienceSectionRepository`. Test suite must cover:
- Section CRUD happy paths
- Section limit exceeded raises `SectionLimitExceededError`
- Entry CRUD happy paths
- Entry limit exceeded raises `EntryLimitExceededError`
- Profile-not-found raises `ValueError` on every service method
- Cross-profile access prevention (section belongs to profile 1; profile 2 cannot create/update/delete entries on it)
- Tiger Style assertion failures (zero ids)
- `get_education_section` returns populated entries; `list_education_sections` returns `entries=[]`

### Tiger Style Requirements

Every service method:
- Precondition: `assert profile_id > 0` (all), `assert section_id > 0` (section ops), `assert entry_id > 0` (entry ops)
- Postcondition on create: `assert result.profile_id == profile_id` (section create), `assert result.section_id == section_id` (entry create)

Every adapter method:
- Precondition: same assertions
- Error handling: `logger.exception("...")` before every `raise` in `except` blocks

### Existing Errors to Reuse

`app/exceptions.py` after story 2.1 contains:
```python
class ContactLimitExceededError(ValueError): pass
class SectionLimitExceededError(ValueError): pass
class EntryLimitExceededError(ValueError): pass
```

Do NOT create new exception classes — reuse `SectionLimitExceededError` and `EntryLimitExceededError`.

### Alembic Migration

Run AFTER models are created:
```bash
docker compose run --rm app alembic revision --autogenerate -m "add education section tables"
docker compose run --rm app alembic upgrade head
```

The migration must create both `education_sections` and `education_entries` in one revision. Verify the generated file references `profiles.id` as FK target for `education_sections.profile_id`.

### Common Mistakes to Avoid

1. **Do NOT call `declarative_base()` in the model file** — import `Base` from `app/models/base.py` only.
2. **Do NOT add `education_sections` to Profile without `if TYPE_CHECKING` guard** for the import — circular import risk.
3. **Do NOT register the router directly in `main.py`** — only in `apis/sections/__init__.py`.
4. **Do NOT use `os.environ` in any new file** — all config via `app/configs/settings.py`.
5. **Do NOT forget `model_config = ConfigDict(from_attributes=True)`** on `EducationSectionRead` and `EducationEntryRead`.
6. **Do NOT omit `list_entries` endpoint from router** — it was not in story 2.2 AC but the service implements it and tests call it; omitting the GET endpoint is fine for now but ensure the service method exists.
7. **Do NOT swallow exceptions** — every `except Exception` block must `logger.exception(...)` then `raise`.

### Project Structure Notes

After story 2.1, the following directories exist:
- `app/models/sections/` — contains `__init__.py`, `experience.py`
- `app/services/sections/` — contains `__init__.py`, `experience_service.py`, `experience_service.test.py`
- `app/schemas/sections/` — contains `__init__.py`, `experience.py`
- `app/apis/sections/` — contains `__init__.py`, `experience.py`

This story adds parallel `education.py` files to each directory. No new directories needed.

### References

- [Source: _bmad-output/planning/epics.md § Story 2.2]
- [Source: _bmad-output/planning/epics.md § Story 2.1 — canonical pattern for all section stories]
- [Source: .worktrees/story-2-1-experience-crud/app/models/sections/experience.py — ORM model pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/services/sections/experience_service.py — service pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/services/sections/experience_service.test.py — test pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/apis/sections/experience.py — router pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/apis/sections/__init__.py — auto-registration pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/apis/dependencies.py — DI wiring pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/interfaces/database.py — protocol pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/schemas/sections/experience.py — schema pattern]
- [Source: .worktrees/story-2-1-experience-crud/app/constants/limits.py — constants pattern]
- [Source: app/adapters/sqlite_database.py — adapter conventions (logging, assert, rollback)]
- [Source: app/constants/limits.py — existing constants (MAX_ENTRIES_PER_SECTION, MAX_SECTIONS_PER_PROFILE)]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
