# Story 2.3: Projects Section CRUD

Status: ready-for-dev

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

- [ ] Task 1: Add projects string-length constants (AC: 4)
  - [ ] 1.1 In `app/constants/limits.py`, add: `PROJECT_TITLE_MAX_LEN: Final[int] = 255`, `PROJECT_ORGANISATION_MAX_LEN: Final[int] = 255`, `PROJECT_DATE_MAX_LEN: Final[int] = 20`, `PROJECT_ENTRY_CONTENT_MAX_LEN: Final[int] = 1000`

- [ ] Task 2: Add `ProjectSectionRepositoryProtocol` to `app/interfaces/database.py` (AC: 6)
  - [ ] 2.1 Add TYPE_CHECKING imports for all project schemas
  - [ ] 2.2 Add `ProjectSectionRepositoryProtocol(Protocol)` with methods: `profile_exists`, `create_project_section`, `list_project_sections`, `get_project_section`, `update_project_section`, `delete_project_section`, `create_entry`, `list_entries`, `update_entry`, `delete_entry`, `count_entries`, `count_sections_for_profile`

- [ ] Task 3: Create projects ORM models (AC: 4)
  - [ ] 3.1 `app/models/sections/__init__.py` **already exists** — skip creation
  - [ ] 3.2 Create `app/models/sections/projects.py` with `ProjectSection` and `ProjectEntry` classes
  - [ ] 3.3 Add `project_sections` relationship to `Profile` in `app/models/profile.py` (mirroring `experience_sections` and `education_sections` already there)

- [ ] Task 4: Create Alembic migration (AC: 5)
  - [ ] 4.1 Run: `docker compose run --rm app alembic revision --autogenerate -m "add project section tables"`
  - [ ] 4.2 Apply: `docker compose run --rm app alembic upgrade head`

- [ ] Task 5: Create Pydantic schemas (AC: 6)
  - [ ] 5.1 `app/schemas/sections/__init__.py` **already exists** — skip creation
  - [ ] 5.2 Create `app/schemas/sections/projects.py` with: `ProjectSectionCreate`, `ProjectSectionRead`, `ProjectSectionUpdate`, `ProjectEntryCreate`, `ProjectEntryRead`, `ProjectEntryUpdate`

- [ ] Task 6: Implement `ProjectSectionService` (AC: 6, 8)
  - [ ] 6.1 `app/services/sections/__init__.py` **already exists** — skip creation
  - [ ] 6.2 Create `app/services/sections/projects_service.py`

- [ ] Task 7: Add projects methods to `SQLiteDatabaseAdapter` (AC: 1, 2, 3)
  - [ ] 7.1 Add all `ProjectSectionRepositoryProtocol` method implementations to `app/adapters/sqlite_database.py`

- [ ] Task 8: Create unit tests (AC: 6)
  - [ ] 8.1 Create `app/services/sections/projects_service.test.py` with `FakeProjectSectionRepository` and full test coverage

- [ ] Task 9: Create router and wire DI (AC: 7)
  - [ ] 9.1 Create `app/apis/sections/projects.py`
  - [ ] 9.2 Add `from app.apis.sections.projects import router as projects_router` and `sections_router.include_router(projects_router)` to `app/apis/sections/__init__.py`
  - [ ] 9.3 Add `get_project_section_service` to `app/apis/dependencies.py`

- [ ] Task 10: Verify (AC: all)
  - [ ] 10.1 Run `make test-local` — all tests pass
  - [ ] 10.2 Run `make lint-local` — clean
  - [ ] 10.3 Run `make typecheck-local` — no errors

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

### Completion Notes List

### File List
