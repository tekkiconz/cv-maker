# Story 1.5: Manage Profile Contacts

Status: done

## Story

As a user,
I want to add, update, and remove contact information on a profile (email, phone, GitHub, LinkedIn, website, Twitter),
so that my CV can include my contact details through the standard profile structure.

## Acceptance Criteria

1. `POST /api/profiles/{profile_id}/contacts` with `{"type": "email", "value": "huy@example.com"}` creates a contact linked to the profile and returns the created contact with its `id`, `type`, `value`, `profile_id`.
2. `GET /api/profiles/{profile_id}/contacts` returns all contacts for the profile.
3. `PATCH /api/profiles/{profile_id}/contacts/{contact_id}` with `{"value": "new@example.com"}` updates the contact value and returns the updated contact.
4. `DELETE /api/profiles/{profile_id}/contacts/{contact_id}` removes the contact and returns HTTP 204.
5. `POST` with an invalid `type` (not in `ContactType` enum) returns HTTP 422.
6. `POST` with a missing `value` returns HTTP 422.
7. Operations on a non-existent `profile_id` return HTTP 404.
8. The `ProfileContact` SQLAlchemy model is defined in `app/models/profile.py` (alongside `Profile`), with a foreign key to `profiles.id` and `cascade="all, delete-orphan"` on the `Profile.contacts` relationship.
9. An Alembic migration version exists that creates the `profile_contacts` table (separate migration revision, chained after profiles migration `996822aeacfb`).
10. `ContactType` enum is imported from `app/constants/enums.py` — do NOT redefine it.
11. Contact CRUD is implemented in a dedicated `ContactService` in `app/services/contact_service.py` and unit-tested in `app/services/contact_service.test.py`.
12. Tiger Style: contact creation asserts `type` is a valid `ContactType` member on input, and asserts the returned contact's `profile_id` matches the request's `profile_id` on output.

## Tasks / Subtasks

- [x] Task 1: Add `ProfileContact` model to `app/models/profile.py` (AC: 8)
  - [x] 1.1 Add `ProfileContact` class with columns: `id`, `profile_id` (FK → `profiles.id`), `type` (String, not nullable), `value` (String, not nullable).
  - [x] 1.2 Add `contacts` relationship to `Profile`: `relationship("ProfileContact", cascade="all, delete-orphan", back_populates="profile")`. Remove the TODO comment about cascade (the contacts relationship satisfies cascade delete for this model — section relationships added in Epic 2 separately).
  - [x] 1.3 Add `profile` back-reference on `ProfileContact`: `relationship("Profile", back_populates="contacts")`.

- [x] Task 2: Add `ContactRepositoryProtocol` to `app/interfaces/database.py` (AC: 11)
  - [x] 2.1 Define `ContactRepositoryProtocol(Protocol)` with methods: `create_contact`, `list_contacts`, `get_contact`, `update_contact`, `delete_contact`.
  - [x] 2.2 Also add `profile_exists(self, profile_id: int) -> bool` to `ContactRepositoryProtocol` — used by service to validate profile before contact ops.

- [x] Task 3: Add contact schemas to `app/schemas/contact.py` (AC: 1–4)
  - [x] 3.1 `ContactCreate(BaseModel)`: `type: ContactType`, `value: str` (non-empty, strip whitespace).
  - [x] 3.2 `ContactRead(BaseModel)`: `model_config = ConfigDict(from_attributes=True)`, fields: `id: int`, `profile_id: int`, `type: ContactType`, `value: str`.
  - [x] 3.3 `ContactUpdate(BaseModel)`: `value: str | None = None` (same strip/min_length constraints as create).

- [x] Task 4: Implement contact methods in `SQLiteDatabaseAdapter` (AC: 1–4, 7)
  - [x] 4.1 `profile_exists(self, profile_id: int) -> bool` — `session.get(Profile, profile_id) is not None`.
  - [x] 4.2 `create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead` — check contact count ≤ `MAX_CONTACTS_PER_PROFILE` before insert; insert `ProfileContact`; commit/rollback; refresh; return `ContactRead.model_validate(contact)`.
  - [x] 4.3 `list_contacts(self, profile_id: int) -> list[ContactRead]` — `select(ProfileContact).where(ProfileContact.profile_id == profile_id)`.
  - [x] 4.4 `get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None` — fetch by `id` AND `profile_id` (prevent cross-profile access).
  - [x] 4.5 `update_contact(self, profile_id: int, contact_id: int, data: ContactUpdate) -> ContactRead | None` — fetch by `id AND profile_id`; apply `data.model_dump(exclude_unset=True)`; commit; refresh; return.
  - [x] 4.6 `delete_contact(self, profile_id: int, contact_id: int) -> bool` — fetch by `id AND profile_id`; delete; commit; return `True`/`False`.

- [x] Task 5: Implement `ContactService` in `app/services/contact_service.py` (AC: 7, 11, 12)
  - [x] 5.1 Constructor: `def __init__(self, db: ContactRepositoryProtocol) -> None`.
  - [x] 5.2 `create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead` — precondition: `profile_id > 0`; validate `profile_exists`; call adapter; postcondition: `result.profile_id == profile_id`.
  - [x] 5.3 `list_contacts(self, profile_id: int) -> list[ContactRead]` — precondition: `profile_id > 0`; validate `profile_exists`; call adapter; postcondition: `isinstance(result, list)`.
  - [x] 5.4 `get_contact(self, profile_id: int, contact_id: int) -> ContactRead` — preconditions: both > 0; raise `ValueError("Contact {contact_id} not found")` if `None`.
  - [x] 5.5 `update_contact(self, profile_id: int, contact_id: int, data: ContactUpdate) -> ContactRead` — same not-found handling.
  - [x] 5.6 `delete_contact(self, profile_id: int, contact_id: int) -> None` — preconditions: both > 0; raise `ValueError` if adapter returns `False`.

- [x] Task 6: Create `app/apis/contacts.py` router (AC: 1–7)
  - [x] 6.1 `router = APIRouter(prefix="/api/profiles/{profile_id}/contacts", tags=["contacts"])`.
  - [x] 6.2 POST `/` → 201; GET `/` → 200; PATCH `/{contact_id}` → 200; DELETE `/{contact_id}` → 204.
  - [x] 6.3 `profile_id` path param: `Path(ge=1)`. `contact_id` path param: `Path(ge=1)`.
  - [x] 6.4 `ValueError` from service → `HTTPException(404)` with `from None`.

- [x] Task 7: Wire DI and register router (AC: all)
  - [x] 7.1 Add `get_contact_service(session: ...) -> ContactService` to `app/apis/dependencies.py`.
  - [x] 7.2 Add `from app.apis.contacts import router as contacts_router` and `app.include_router(contacts_router)` in `app/main.py`.

- [x] Task 8: Generate and verify Alembic migration (AC: 9)
  - [x] 8.1 Run `docker compose run --rm app alembic revision --autogenerate -m "create profile_contacts table"` — review the generated migration for correctness.
  - [x] 8.2 Verify `down_revision = "996822aeacfb"` (chains after profiles migration).
  - [x] 8.3 Expected columns: `id INTEGER PK`, `profile_id INTEGER NOT NULL FK→profiles.id`, `type VARCHAR NOT NULL`, `value VARCHAR NOT NULL`.
  - [x] 8.4 Run `docker compose run --rm app alembic upgrade head` — confirms migration applies cleanly.

- [x] Task 9: Unit tests in `app/services/contact_service.test.py` (AC: 11, 12)
  - [x] 9.1 `FakeContactRepository` implementing `ContactRepositoryProtocol` — in-memory list, honors `profile_id` scoping.
  - [x] 9.2 Tests: create contact happy path; list contacts; get contact; update contact; delete contact; profile not found → `ValueError`; contact not found → `ValueError`; Tiger Style precondition (`profile_id=0` → `AssertionError`); Tiger Style postcondition (`result.profile_id == profile_id`).

- [x] Task 10: Integration tests in `tests/api/test_contacts.py` (AC: 1–7)
  - [x] 10.1 `POST` happy path → 201; `GET` all → 200; `PATCH` → 200; `DELETE` → 204.
  - [x] 10.2 Invalid `type` → 422; missing `value` → 422.
  - [x] 10.3 Non-existent `profile_id` → 404.
  - [x] 10.4 Non-existent `contact_id` → 404.
  - [x] 10.5 Update `conftest.py` `http_client` fixture to also override `get_contact_service`.

- [x] Task 11: Full validation (AC: all)
  - [x] 11.1 `make test-local` — all tests pass, no regressions.
  - [x] 11.2 `ruff check . && ruff format --check .` — clean.
  - [x] 11.3 `make typecheck-local` — no errors.

## Dev Notes

### New Files

- `app/models/profile.py` — add `ProfileContact` model and `Profile.contacts` relationship (modifying existing)
- `app/interfaces/database.py` — add `ContactRepositoryProtocol` (modifying existing)
- `app/schemas/contact.py` — **new file**
- `app/services/contact_service.py` — **new file**
- `app/services/contact_service.test.py` — **new file**
- `app/apis/contacts.py` — **new file**
- `app/apis/dependencies.py` — add `get_contact_service` (modifying existing)
- `app/main.py` — add `contacts_router` include (modifying existing)
- `migrations/versions/<hash>_create_profile_contacts_table.py` — **new file** (generated by alembic)
- `tests/api/test_contacts.py` — **new file**
- `tests/conftest.py` — update `http_client` fixture (modifying existing)

### ContactType Is Already Defined

`ContactType` is a `StrEnum` in `app/constants/enums.py`:
```python
class ContactType(StrEnum):
    email = "email"
    phone = "phone"
    github = "github"
    linkedin = "linkedin"
    website = "website"
    twitter = "twitter"
```
Import from there. Do NOT redefine.

### MAX_CONTACTS_PER_PROFILE Is Already Defined

`MAX_CONTACTS_PER_PROFILE = 20` in `app/constants/limits.py`. Use this constant in the adapter's `create_contact` to enforce the limit before insert.

### ProfileContact Model Pattern

```python
# app/models/profile.py — add alongside Profile class
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import relationship

class ProfileContact(Base):
    __tablename__ = "profile_contacts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    value: Mapped[str] = mapped_column(String(500), nullable=False)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="contacts")
```

Add to `Profile` class (replaces the TODO comment):
```python
contacts: Mapped[list["ProfileContact"]] = relationship(
    "ProfileContact", cascade="all, delete-orphan", back_populates="profile"
)
```

**Do NOT use SQLAlchemy `Enum` type for the `type` column** — use `String(50)`. SQLite has no native enum type; `ContactType` (StrEnum) stores as plain string. Pydantic validates the enum on the way in/out.

### ContactRepositoryProtocol Pattern

```python
# app/interfaces/database.py — append new Protocol
@runtime_checkable
class ContactRepositoryProtocol(Protocol):
    async def profile_exists(self, profile_id: int) -> bool: ...
    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead: ...
    async def list_contacts(self, profile_id: int) -> list[ContactRead]: ...
    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None: ...
    async def update_contact(self, profile_id: int, contact_id: int, data: ContactUpdate) -> ContactRead | None: ...
    async def delete_contact(self, profile_id: int, contact_id: int) -> bool: ...
```

Add `ContactCreate`, `ContactRead`, `ContactUpdate` to `TYPE_CHECKING` imports.

### ContactService Tiger Style

```python
async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead:
    assert profile_id > 0, "profile_id must be a positive integer"
    assert data.type in ContactType.__members__.values(), f"invalid ContactType: {data.type}"
    if not await self._db.profile_exists(profile_id):
        raise ValueError(f"Profile {profile_id} not found")
    result = await self._db.create_contact(profile_id, data)
    assert result.profile_id == profile_id, "returned contact profile_id must match request"
    return result
```

### Router Pattern (mirrors `app/apis/profiles.py`)

```python
router = APIRouter(prefix="/api/profiles/{profile_id}/contacts", tags=["contacts"])

@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(
    profile_id: Annotated[int, Path(ge=1)],
    data: ContactCreate,
    service: Annotated[ContactService, Depends(get_contact_service)],
) -> ContactRead:
    try:
        return await service.create_contact(profile_id, data)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found") from None
```

### DI Wiring

```python
# app/apis/dependencies.py
from app.services.contact_service import ContactService

async def get_contact_service(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> ContactService:
    adapter = make_sqlite_adapter(session)
    return ContactService(adapter)
```

Note: `SQLiteDatabaseAdapter` will need to implement `ContactRepositoryProtocol` methods — add them directly to the existing class. The adapter currently satisfies `ProfileRepositoryProtocol`; it will also satisfy `ContactRepositoryProtocol` after this story.

### conftest.py Update (Critical)

The `http_client` fixture in `tests/conftest.py` overrides `get_profile_service`. Add `get_contact_service` override too, or integration tests will fail with real DB wiring:

```python
from app.apis.dependencies import get_contact_service, get_profile_service
from app.services.contact_service import ContactService

@pytest.fixture
async def http_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient]:
    async def override_profile_service() -> ProfileService:
        adapter = SQLiteDatabaseAdapter(db_session)
        return ProfileService(adapter)

    async def override_contact_service() -> ContactService:
        adapter = SQLiteDatabaseAdapter(db_session)
        return ContactService(adapter)

    app.dependency_overrides[get_profile_service] = override_profile_service
    app.dependency_overrides[get_contact_service] = override_contact_service
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client
    finally:
        app.dependency_overrides.clear()
```

### Migration Chain

Existing migration: `996822aeacfb` (profiles table).
New migration `down_revision` must be `"996822aeacfb"`.
Generate via Docker: `docker compose run --rm app alembic revision --autogenerate -m "create profile_contacts table"`.
Review the generated file before applying — confirm FK to `profiles.id` is present.

### 404 vs 422 Disambiguation

- Non-existent `profile_id`: service raises `ValueError("Profile {id} not found")` → router catches → HTTP 404.
- Non-existent `contact_id`: service raises `ValueError("Contact {id} not found")` → router catches → HTTP 404.
- Invalid `type` enum value: Pydantic validation rejects before hitting service → HTTP 422 (FastAPI automatic).
- Missing `value`: Pydantic validation → HTTP 422 (FastAPI automatic).

### Existing Code Patterns (Do Not Deviate)

- All service and adapter methods: `async def`
- All `profile_id`/`contact_id` path params: `Path(ge=1)` — returns 422 before service assertions
- `raise HTTPException(...) from None` — not `raise HTTPException(...)` — prevents B904 ruff error
- `from __future__ import annotations` at top of `interfaces/database.py` — already present
- `model_dump(exclude_unset=True)` for partial PATCH in adapter update methods
- Commit/rollback pattern in adapter:
  ```python
  try:
      await self._session.commit()
  except Exception:
      await self._session.rollback()
      raise
  ```

### Architecture Rules (Non-Negotiable)

- No business logic in `apis/contacts.py`
- No HTTP imports (`HTTPException`, `status`) in `app/services/`
- No `os.environ` reads — import from `app/configs/settings.py` if needed
- HX-Request check lives only in `controllers/` — not relevant here (API-only story)
- Type hints on all signatures (mypy enforced)
- Absolute imports only (no relative imports)

### Project Structure Notes

Contacts are a sub-resource of profiles — URL nesting `/api/profiles/{id}/contacts` is correct per AC and architecture.
No new top-level resource. Router prefix uses `profile_id` path variable — FastAPI handles path param extraction from prefix correctly.

### References

- [Source: _bmad-output/planning/epics.md — Story 1.5 Acceptance Criteria]
- [Source: app/constants/enums.py — ContactType already defined]
- [Source: app/constants/limits.py — MAX_CONTACTS_PER_PROFILE = 20]
- [Source: app/models/profile.py — Profile model, TODO for cascade relationship]
- [Source: app/interfaces/database.py — ProfileRepositoryProtocol pattern to mirror]
- [Source: app/adapters/sqlite_database.py — commit/rollback, ORM patterns]
- [Source: app/services/profile_service.py — Tiger Style assertion patterns]
- [Source: app/apis/profiles.py — Router pattern, Path(ge=1), from None]
- [Source: app/apis/dependencies.py — DI wiring pattern]
- [Source: app/main.py — Router registration pattern]
- [Source: tests/conftest.py — http_client fixture to extend]
- [Source: migrations/versions/996822aeacfb_create_profiles_table.py — migration chain parent]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

N/A

### Completion Notes List

- All 10 tasks + final validation complete on branch `feature/manage-profile-contacts`
- 76 tests passing (15 unit + 13 API integration + remainder existing)
- Lint clean (`ruff check` + `ruff format --check`)
- Alembic migration `a0726fa39315` chains after `996822aeacfb` (profiles table)
- Tiger Style assertions on all service methods (pre + postconditions)
- `ProfileContact` model co-located in `app/models/profile.py` with cascade delete

### File List

- `app/models/profile.py` — added `ProfileContact` model and `Profile.contacts` relationship
- `app/interfaces/database.py` — added `ContactRepositoryProtocol`
- `app/schemas/contact.py` — new: `ContactCreate`, `ContactRead`, `ContactUpdate`
- `app/services/contact_service.py` — new: `ContactService` with Tiger Style assertions
- `app/services/contact_service.test.py` — new: 15 unit tests with `FakeContactRepository`
- `app/adapters/sqlite_database.py` — added `profile_exists` + 5 contact CRUD methods
- `app/apis/contacts.py` — new: router POST/GET/PATCH/DELETE
- `app/apis/dependencies.py` — added `get_contact_service`
- `app/main.py` — registered `contacts_router`
- `migrations/versions/a0726fa39315_create_profile_contacts_table.py` — new migration
- `tests/api/test_contacts.py` — new: 13 integration tests
- `tests/conftest.py` — added `override_contact_service` to `http_client` fixture
