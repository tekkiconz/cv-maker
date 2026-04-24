from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.constants.limits import MAX_ENTRIES_PER_SECTION, MAX_SECTIONS_PER_PROFILE
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.schemas.sections.experience import (
    ExperienceEntryCreate,
    ExperienceEntryRead,
    ExperienceEntryUpdate,
    ExperienceSectionCreate,
    ExperienceSectionRead,
    ExperienceSectionUpdate,
)
from app.services.sections.experience_service import ExperienceSectionService


def _now() -> datetime:
    return datetime.now(tz=UTC)


class FakeExperienceSectionRepository:
    def __init__(self) -> None:
        self._profiles: set[int] = {1, 2, 3}
        self._sections: list[ExperienceSectionRead] = []
        self._entries: list[ExperienceEntryRead] = []
        self._next_section_id: int = 1
        self._next_entry_id: int = 1

    async def profile_exists(self, profile_id: int) -> bool:
        return profile_id in self._profiles

    async def count_sections_for_profile(self, profile_id: int) -> int:
        return sum(1 for s in self._sections if s.profile_id == profile_id)

    async def create_experience_section(
        self, profile_id: int, data: ExperienceSectionCreate
    ) -> ExperienceSectionRead:
        section = ExperienceSectionRead(
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

    async def list_experience_sections(self, profile_id: int) -> list[ExperienceSectionRead]:
        return sorted(
            [s for s in self._sections if s.profile_id == profile_id],
            key=lambda s: s.display_order,
        )

    async def get_experience_section(
        self, profile_id: int, section_id: int
    ) -> ExperienceSectionRead | None:
        return next(
            (s for s in self._sections if s.id == section_id and s.profile_id == profile_id),
            None,
        )

    async def update_experience_section(
        self, profile_id: int, section_id: int, data: ExperienceSectionUpdate
    ) -> ExperienceSectionRead | None:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                updates = data.model_dump(exclude_unset=True)
                updated = section.model_copy(update=updates)
                self._sections[i] = updated
                return updated
        return None

    async def delete_experience_section(self, profile_id: int, section_id: int) -> bool:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                self._sections.pop(i)
                return True
        return False

    async def count_entries(self, section_id: int) -> int:
        return sum(1 for e in self._entries if e.section_id == section_id)

    async def create_entry(
        self, section_id: int, data: ExperienceEntryCreate
    ) -> ExperienceEntryRead:
        entry = ExperienceEntryRead(
            id=self._next_entry_id,
            section_id=section_id,
            content=data.content,
            display_order=data.display_order,
        )
        self._entries.append(entry)
        self._next_entry_id += 1
        return entry

    async def list_entries(self, section_id: int) -> list[ExperienceEntryRead]:
        return [e for e in self._entries if e.section_id == section_id]

    async def update_entry(
        self, section_id: int, entry_id: int, data: ExperienceEntryUpdate
    ) -> ExperienceEntryRead | None:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                updates = data.model_dump(exclude_unset=True)
                updated = entry.model_copy(update=updates)
                self._entries[i] = updated
                return updated
        return None

    async def delete_entry(self, section_id: int, entry_id: int) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                self._entries.pop(i)
                return True
        return False


@pytest.fixture
def fake_db() -> FakeExperienceSectionRepository:
    return FakeExperienceSectionRepository()


@pytest.fixture
def service(fake_db: FakeExperienceSectionRepository) -> ExperienceSectionService:
    return ExperienceSectionService(fake_db)


# --- Section happy paths ---

async def test_create_experience_section_happy_path(service: ExperienceSectionService) -> None:
    data = ExperienceSectionCreate(title="Software Engineer", organisation="Acme")
    result = await service.create_experience_section(1, data)
    assert result.id is not None
    assert result.profile_id == 1
    assert result.title == "Software Engineer"
    assert result.is_enabled is True


async def test_create_experience_section_postcondition_profile_id_matches(
    service: ExperienceSectionService,
) -> None:
    data = ExperienceSectionCreate(title="Dev")
    result = await service.create_experience_section(2, data)
    assert result.profile_id == 2


async def test_list_experience_sections_ordered_by_display_order(
    service: ExperienceSectionService,
) -> None:
    await service.create_experience_section(
        1, ExperienceSectionCreate(title="B", display_order=2)
    )
    await service.create_experience_section(
        1, ExperienceSectionCreate(title="A", display_order=1)
    )
    result = await service.list_experience_sections(1)
    assert [s.title for s in result] == ["A", "B"]


async def test_get_experience_section_happy_path(service: ExperienceSectionService) -> None:
    created = await service.create_experience_section(
        1, ExperienceSectionCreate(title="Engineer")
    )
    result = await service.get_experience_section(1, created.id)
    assert result.id == created.id
    assert result.title == "Engineer"


async def test_get_experience_section_not_found_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.get_experience_section(1, 999)


async def test_update_experience_section_happy_path(service: ExperienceSectionService) -> None:
    created = await service.create_experience_section(
        1, ExperienceSectionCreate(title="Old Title")
    )
    result = await service.update_experience_section(
        1, created.id, ExperienceSectionUpdate(title="New Title")
    )
    assert result.title == "New Title"


async def test_update_experience_section_not_found_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.update_experience_section(1, 999, ExperienceSectionUpdate(title="X"))


async def test_toggle_is_enabled_false(service: ExperienceSectionService) -> None:
    created = await service.create_experience_section(
        1, ExperienceSectionCreate(title="Dev")
    )
    result = await service.update_experience_section(
        1, created.id, ExperienceSectionUpdate(is_enabled=False)
    )
    assert result.is_enabled is False


async def test_toggle_is_enabled_back_to_true(service: ExperienceSectionService) -> None:
    created = await service.create_experience_section(
        1, ExperienceSectionCreate(title="Dev")
    )
    await service.update_experience_section(
        1, created.id, ExperienceSectionUpdate(is_enabled=False)
    )
    result = await service.update_experience_section(
        1, created.id, ExperienceSectionUpdate(is_enabled=True)
    )
    assert result.is_enabled is True


async def test_delete_experience_section(service: ExperienceSectionService) -> None:
    created = await service.create_experience_section(
        1, ExperienceSectionCreate(title="Dev")
    )
    await service.delete_experience_section(1, created.id)
    with pytest.raises(ValueError, match=f"Section {created.id} not found"):
        await service.get_experience_section(1, created.id)


async def test_delete_experience_section_not_found_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.delete_experience_section(1, 999)


# --- Entry happy paths ---

async def test_create_entry_happy_path(service: ExperienceSectionService) -> None:
    result = await service.create_entry(1, ExperienceEntryCreate(content="Led a team of 5"))
    assert result.id is not None
    assert result.section_id == 1
    assert result.content == "Led a team of 5"


async def test_create_entry_postcondition_section_id_matches(
    service: ExperienceSectionService,
) -> None:
    result = await service.create_entry(2, ExperienceEntryCreate(content="Built infra"))
    assert result.section_id == 2


async def test_create_entry_limit_exceeded_raises(
    service: ExperienceSectionService,
    fake_db: FakeExperienceSectionRepository,
) -> None:
    for i in range(MAX_ENTRIES_PER_SECTION):
        fake_db._entries.append(
            ExperienceEntryRead(id=i + 1, section_id=1, content=f"entry {i}", display_order=i)
        )
    fake_db._next_entry_id = MAX_ENTRIES_PER_SECTION + 1

    with pytest.raises(EntryLimitExceededError):
        await service.create_entry(1, ExperienceEntryCreate(content="overflow"))


async def test_create_section_limit_exceeded_raises(
    service: ExperienceSectionService,
    fake_db: FakeExperienceSectionRepository,
) -> None:
    for i in range(MAX_SECTIONS_PER_PROFILE):
        fake_db._sections.append(
            ExperienceSectionRead(
                id=i + 1,
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
    fake_db._next_section_id = MAX_SECTIONS_PER_PROFILE + 1

    with pytest.raises(SectionLimitExceededError):
        await service.create_experience_section(1, ExperienceSectionCreate(title="overflow"))


async def test_update_entry_happy_path(service: ExperienceSectionService) -> None:
    created = await service.create_entry(1, ExperienceEntryCreate(content="old content"))
    result = await service.update_entry(1, created.id, ExperienceEntryUpdate(content="new content"))
    assert result.content == "new content"


async def test_update_entry_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.update_entry(1, 999, ExperienceEntryUpdate(content="x"))


async def test_delete_entry(service: ExperienceSectionService) -> None:
    created = await service.create_entry(1, ExperienceEntryCreate(content="bullet"))
    await service.delete_entry(1, created.id)
    entries = await service.list_entries(1)
    assert all(e.id != created.id for e in entries)


async def test_delete_entry_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.delete_entry(1, 999)


# --- Profile-not-found raises ---

async def test_create_section_profile_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.create_experience_section(99, ExperienceSectionCreate(title="X"))


async def test_list_sections_profile_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.list_experience_sections(99)


async def test_get_section_profile_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.get_experience_section(99, 1)


async def test_update_section_profile_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.update_experience_section(99, 1, ExperienceSectionUpdate(title="X"))


async def test_delete_section_profile_not_found_raises(service: ExperienceSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.delete_experience_section(99, 1)


# --- Tiger Style assertion failures ---

async def test_tiger_create_section_profile_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_experience_section(0, ExperienceSectionCreate(title="X"))


async def test_tiger_get_section_section_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.get_experience_section(1, 0)


async def test_tiger_update_section_section_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.update_experience_section(1, 0, ExperienceSectionUpdate(title="X"))


async def test_tiger_delete_section_section_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.delete_experience_section(1, 0)


async def test_tiger_create_entry_section_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_entry(0, ExperienceEntryCreate(content="x"))


async def test_tiger_update_entry_entry_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.update_entry(1, 0, ExperienceEntryUpdate(content="x"))


async def test_tiger_delete_entry_entry_id_zero_raises(
    service: ExperienceSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.delete_entry(1, 0)
