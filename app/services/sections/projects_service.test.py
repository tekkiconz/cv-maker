from __future__ import annotations

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from app.constants.limits import MAX_ENTRIES_PER_SECTION, MAX_SECTIONS_PER_PROFILE
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.schemas.sections.projects import (
    ProjectEntryCreate,
    ProjectEntryRead,
    ProjectEntryUpdate,
    ProjectSectionCreate,
    ProjectSectionRead,
    ProjectSectionUpdate,
)
from app.services.sections.projects_service import ProjectSectionService


def _now() -> datetime:
    return datetime.now(tz=UTC)


class FakeProjectSectionRepository:
    def __init__(self) -> None:
        self._profiles: set[int] = {1, 2, 3}
        self._sections: list[ProjectSectionRead] = []
        self._entries: list[ProjectEntryRead] = []
        self._next_section_id: int = 1
        self._next_entry_id: int = 1

    async def profile_exists(self, profile_id: int) -> bool:
        return profile_id in self._profiles

    async def count_project_sections_for_profile(self, profile_id: int) -> int:
        return sum(1 for s in self._sections if s.profile_id == profile_id)

    async def create_project_section(
        self, profile_id: int, data: ProjectSectionCreate
    ) -> ProjectSectionRead:
        section = ProjectSectionRead(
            id=self._next_section_id,
            profile_id=profile_id,
            title=data.title,
            organisation=data.organisation,
            start_date=data.start_date,
            end_date=data.end_date,
            is_enabled=data.is_enabled,
            display_order=data.display_order,
            created_at=_now(),
            updated_at=_now(),
            entries=[],
        )
        self._sections.append(section)
        self._next_section_id += 1
        return section

    async def list_project_sections(self, profile_id: int) -> list[ProjectSectionRead]:
        return sorted(
            [s for s in self._sections if s.profile_id == profile_id],
            key=lambda s: (s.display_order, s.id),
        )

    async def get_project_section(
        self, profile_id: int, section_id: int
    ) -> ProjectSectionRead | None:
        section = next(
            (s for s in self._sections if s.id == section_id and s.profile_id == profile_id),
            None,
        )
        if section is None:
            return None
        entries = [e for e in self._entries if e.section_id == section_id]
        return section.model_copy(update={"entries": entries})

    async def update_project_section(
        self, profile_id: int, section_id: int, data: ProjectSectionUpdate
    ) -> ProjectSectionRead | None:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                updates = data.model_dump(exclude_unset=True)
                updated = section.model_copy(update=updates)
                self._sections[i] = updated
                return updated
        return None

    async def delete_project_section(self, profile_id: int, section_id: int) -> bool:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                self._sections.pop(i)
                return True
        return False

    async def count_project_entries(self, section_id: int) -> int:
        return sum(1 for e in self._entries if e.section_id == section_id)

    async def create_project_entry(
        self, section_id: int, data: ProjectEntryCreate
    ) -> ProjectEntryRead:
        entry = ProjectEntryRead(
            id=self._next_entry_id,
            section_id=section_id,
            content=data.content,
            display_order=data.display_order,
            created_at=_now(),
            updated_at=_now(),
        )
        self._entries.append(entry)
        self._next_entry_id += 1
        return entry

    async def list_project_entries(self, section_id: int) -> list[ProjectEntryRead]:
        return sorted(
            [e for e in self._entries if e.section_id == section_id],
            key=lambda e: (e.display_order, e.id),
        )

    async def update_project_entry(
        self, section_id: int, entry_id: int, data: ProjectEntryUpdate
    ) -> ProjectEntryRead | None:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                updates = data.model_dump(exclude_unset=True)
                updated = entry.model_copy(update=updates)
                self._entries[i] = updated
                return updated
        return None

    async def delete_project_entry(self, section_id: int, entry_id: int) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                self._entries.pop(i)
                return True
        return False


@pytest.fixture
def fake_db() -> FakeProjectSectionRepository:
    return FakeProjectSectionRepository()


@pytest.fixture
def service(fake_db: FakeProjectSectionRepository) -> ProjectSectionService:
    return ProjectSectionService(fake_db)


# --- Section happy paths ---


async def test_create_project_section_happy_path(service: ProjectSectionService) -> None:
    data = ProjectSectionCreate(title="CVMaker", organisation="Personal")
    result = await service.create_project_section(1, data)
    assert result.id is not None
    assert result.profile_id == 1
    assert result.title == "CVMaker"
    assert result.is_enabled is True


async def test_create_project_section_postcondition_profile_id_matches(
    service: ProjectSectionService,
) -> None:
    data = ProjectSectionCreate(title="Side Project")
    result = await service.create_project_section(2, data)
    assert result.profile_id == 2


async def test_list_project_sections_ordered_by_display_order(
    service: ProjectSectionService,
) -> None:
    await service.create_project_section(1, ProjectSectionCreate(title="B", display_order=2))
    await service.create_project_section(1, ProjectSectionCreate(title="A", display_order=1))
    result = await service.list_project_sections(1)
    assert [s.title for s in result] == ["A", "B"]


async def test_get_project_section_happy_path(service: ProjectSectionService) -> None:
    created = await service.create_project_section(1, ProjectSectionCreate(title="My App"))
    result = await service.get_project_section(1, created.id)
    assert result.id == created.id
    assert result.title == "My App"


async def test_get_project_section_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.get_project_section(1, 999)


async def test_update_project_section_happy_path(service: ProjectSectionService) -> None:
    created = await service.create_project_section(1, ProjectSectionCreate(title="Old Title"))
    result = await service.update_project_section(
        1, created.id, ProjectSectionUpdate(title="New Title")
    )
    assert result.title == "New Title"


async def test_update_project_section_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.update_project_section(1, 999, ProjectSectionUpdate(title="X"))


async def test_toggle_is_enabled_false(service: ProjectSectionService) -> None:
    created = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    result = await service.update_project_section(
        1, created.id, ProjectSectionUpdate(is_enabled=False)
    )
    assert result.is_enabled is False


async def test_toggle_is_enabled_back_to_true(service: ProjectSectionService) -> None:
    created = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    await service.update_project_section(1, created.id, ProjectSectionUpdate(is_enabled=False))
    result = await service.update_project_section(
        1, created.id, ProjectSectionUpdate(is_enabled=True)
    )
    assert result.is_enabled is True


async def test_delete_project_section(service: ProjectSectionService) -> None:
    created = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    await service.delete_project_section(1, created.id)
    with pytest.raises(ValueError, match=f"Section {created.id} not found"):
        await service.get_project_section(1, created.id)


async def test_delete_project_section_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.delete_project_section(1, 999)


# --- Entry happy paths ---


async def test_create_entry_happy_path(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="CVMaker"))
    result = await service.create_entry(
        1, section.id, ProjectEntryCreate(content="Built with FastAPI")
    )
    assert result.id is not None
    assert result.section_id == section.id
    assert result.content == "Built with FastAPI"


async def test_create_entry_postcondition_section_id_matches(
    service: ProjectSectionService,
) -> None:
    section = await service.create_project_section(2, ProjectSectionCreate(title="App"))
    result = await service.create_entry(2, section.id, ProjectEntryCreate(content="bullet"))
    assert result.section_id == section.id


async def test_create_entry_limit_exceeded_raises(
    service: ProjectSectionService,
    fake_db: FakeProjectSectionRepository,
) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    base_id = fake_db._next_entry_id
    for i in range(MAX_ENTRIES_PER_SECTION):
        fake_db._entries.append(
            ProjectEntryRead(
                id=base_id + i,
                section_id=section.id,
                content=f"entry {i}",
                display_order=i,
                created_at=_now(),
                updated_at=_now(),
            )
        )
    fake_db._next_entry_id = base_id + MAX_ENTRIES_PER_SECTION

    with pytest.raises(EntryLimitExceededError):
        await service.create_entry(1, section.id, ProjectEntryCreate(content="overflow"))


async def test_create_section_limit_exceeded_raises(
    service: ProjectSectionService,
    fake_db: FakeProjectSectionRepository,
) -> None:
    base_id = fake_db._next_section_id
    for i in range(MAX_SECTIONS_PER_PROFILE):
        fake_db._sections.append(
            ProjectSectionRead(
                id=base_id + i,
                profile_id=1,
                title=f"section {i}",
                organisation=None,
                start_date=None,
                end_date=None,
                is_enabled=True,
                display_order=i,
                created_at=_now(),
                updated_at=_now(),
                entries=[],
            )
        )
    fake_db._next_section_id = base_id + MAX_SECTIONS_PER_PROFILE

    with pytest.raises(SectionLimitExceededError):
        await service.create_project_section(1, ProjectSectionCreate(title="overflow"))


async def test_update_entry_happy_path(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    created = await service.create_entry(1, section.id, ProjectEntryCreate(content="old content"))
    result = await service.update_entry(
        1, section.id, created.id, ProjectEntryUpdate(content="new content")
    )
    assert result.content == "new content"


async def test_update_entry_not_found_raises(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.update_entry(1, section.id, 999, ProjectEntryUpdate(content="x"))


async def test_delete_entry(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    created = await service.create_entry(1, section.id, ProjectEntryCreate(content="bullet"))
    await service.delete_entry(1, section.id, created.id)
    entries = await service.list_entries(1, section.id)
    assert all(e.id != created.id for e in entries)


async def test_delete_entry_not_found_raises(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.delete_entry(1, section.id, 999)


# --- Cross-profile access prevention ---


async def test_create_entry_section_not_found_raises() -> None:
    fake_db = FakeProjectSectionRepository()
    svc = ProjectSectionService(fake_db)

    with pytest.raises(ValueError, match="Section 999 not found"):
        await svc.create_entry(1, 999, ProjectEntryCreate(content="bullet"))


async def test_create_entry_cross_profile_raises() -> None:
    """Section belongs to profile 1 — profile 2 must not create entries on it."""
    fake_db = FakeProjectSectionRepository()
    svc = ProjectSectionService(fake_db)

    section = await svc.create_project_section(1, ProjectSectionCreate(title="App"))

    with pytest.raises(ValueError, match="Section"):
        await svc.create_entry(2, section.id, ProjectEntryCreate(content="bullet"))


async def test_update_entry_cross_profile_raises() -> None:
    fake_db = FakeProjectSectionRepository()
    svc = ProjectSectionService(fake_db)

    section = await svc.create_project_section(1, ProjectSectionCreate(title="App"))
    entry = await svc.create_entry(1, section.id, ProjectEntryCreate(content="bullet"))

    with pytest.raises(ValueError, match="Section"):
        await svc.update_entry(2, section.id, entry.id, ProjectEntryUpdate(content="new"))


async def test_delete_entry_cross_profile_raises() -> None:
    fake_db = FakeProjectSectionRepository()
    svc = ProjectSectionService(fake_db)

    section = await svc.create_project_section(1, ProjectSectionCreate(title="App"))
    entry = await svc.create_entry(1, section.id, ProjectEntryCreate(content="bullet"))

    with pytest.raises(ValueError, match="Section"):
        await svc.delete_entry(2, section.id, entry.id)


# --- Profile-not-found raises ---


async def test_create_section_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.create_project_section(99, ProjectSectionCreate(title="X"))


async def test_list_sections_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.list_project_sections(99)


async def test_get_section_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.get_project_section(99, 1)


async def test_update_section_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.update_project_section(99, 1, ProjectSectionUpdate(title="X"))


async def test_delete_section_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.delete_project_section(99, 1)


async def test_create_entry_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.create_entry(99, 1, ProjectEntryCreate(content="x"))


async def test_list_entries_profile_not_found_raises(service: ProjectSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.list_entries(99, 1)


# --- Tiger Style assertion failures ---


async def test_tiger_create_section_profile_id_zero_raises(
    service: ProjectSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_project_section(0, ProjectSectionCreate(title="X"))


async def test_tiger_get_section_section_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.get_project_section(1, 0)


async def test_tiger_update_section_section_id_zero_raises(
    service: ProjectSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.update_project_section(1, 0, ProjectSectionUpdate(title="X"))


async def test_tiger_delete_section_section_id_zero_raises(
    service: ProjectSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.delete_project_section(1, 0)


async def test_tiger_create_entry_section_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.create_entry(1, 0, ProjectEntryCreate(content="x"))


async def test_tiger_update_entry_entry_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.update_entry(1, 1, 0, ProjectEntryUpdate(content="x"))


async def test_tiger_delete_entry_entry_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.delete_entry(1, 1, 0)


async def test_tiger_create_entry_profile_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.create_entry(0, 1, ProjectEntryCreate(content="x"))


async def test_tiger_list_sections_profile_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.list_project_sections(0)


async def test_tiger_list_entries_section_id_zero_raises(service: ProjectSectionService) -> None:
    with pytest.raises(AssertionError):
        await service.list_entries(1, 0)


async def test_get_project_section_returns_populated_entries(
    service: ProjectSectionService,
) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="CVMaker"))
    await service.create_entry(1, section.id, ProjectEntryCreate(content="Built with FastAPI"))
    result = await service.get_project_section(1, section.id)
    assert len(result.entries) == 1
    assert result.entries[0].content == "Built with FastAPI"


async def test_list_project_sections_entries_not_populated() -> None:
    """list endpoint must return entries=[] (not eagerly loaded)."""
    fake_db = FakeProjectSectionRepository()
    svc = ProjectSectionService(fake_db)

    await svc.create_project_section(1, ProjectSectionCreate(title="App A"))
    sections = await svc.list_project_sections(1)

    assert sections[0].entries == []


# --- Schema validation smoke tests ---


def test_schema_organisation_empty_string_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionCreate(title="App", organisation="")


def test_schema_start_date_empty_string_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionCreate(title="App", start_date="")


def test_schema_end_date_empty_string_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionCreate(title="App", end_date="")


def test_schema_display_order_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionCreate(title="App", display_order=-1)


def test_schema_entry_display_order_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectEntryCreate(content="bullet", display_order=-1)


def test_schema_update_title_null_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionUpdate.model_validate({"title": None})


def test_schema_update_display_order_negative_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionUpdate(display_order=-1)


def test_schema_update_display_order_null_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectSectionUpdate.model_validate({"display_order": None})


async def test_update_entry_profile_not_found_raises(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    entry = await service.create_entry(1, section.id, ProjectEntryCreate(content="bullet"))
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.update_entry(99, section.id, entry.id, ProjectEntryUpdate(content="new"))


async def test_delete_entry_profile_not_found_raises(service: ProjectSectionService) -> None:
    section = await service.create_project_section(1, ProjectSectionCreate(title="App"))
    entry = await service.create_entry(1, section.id, ProjectEntryCreate(content="bullet"))
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.delete_entry(99, section.id, entry.id)


def test_schema_update_entry_content_null_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectEntryUpdate.model_validate({"content": None})


def test_schema_update_entry_display_order_null_rejected() -> None:
    with pytest.raises(ValidationError):
        ProjectEntryUpdate.model_validate({"display_order": None})
