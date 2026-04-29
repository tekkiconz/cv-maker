from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.constants.limits import MAX_ENTRIES_PER_SECTION, MAX_SECTIONS_PER_PROFILE
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.schemas.sections.education import (
    EducationEntryCreate,
    EducationEntryRead,
    EducationEntryUpdate,
    EducationSectionCreate,
    EducationSectionRead,
    EducationSectionUpdate,
)
from app.services.sections.education_service import EducationSectionService


def _now() -> datetime:
    return datetime.now(tz=UTC)


class FakeEducationSectionRepository:
    def __init__(self) -> None:
        self._profiles: set[int] = {1, 2, 3}
        self._sections: list[EducationSectionRead] = []
        self._entries: list[EducationEntryRead] = []
        self._next_section_id: int = 1
        self._next_entry_id: int = 1

    async def profile_exists(self, profile_id: int) -> bool:
        return profile_id in self._profiles

    async def count_education_sections_for_profile(self, profile_id: int) -> int:
        return sum(1 for s in self._sections if s.profile_id == profile_id)

    async def create_education_section(
        self, profile_id: int, data: EducationSectionCreate
    ) -> EducationSectionRead:
        section = EducationSectionRead(
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

    async def list_education_sections(self, profile_id: int) -> list[EducationSectionRead]:
        return sorted(
            [s for s in self._sections if s.profile_id == profile_id],
            key=lambda s: s.display_order,
        )

    async def get_education_section(
        self, profile_id: int, section_id: int
    ) -> EducationSectionRead | None:
        section = next(
            (s for s in self._sections if s.id == section_id and s.profile_id == profile_id),
            None,
        )
        if section is None:
            return None
        entries = [e for e in self._entries if e.section_id == section_id]
        return section.model_copy(update={"entries": entries})

    async def update_education_section(
        self, profile_id: int, section_id: int, data: EducationSectionUpdate
    ) -> EducationSectionRead | None:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                updates = data.model_dump(exclude_unset=True)
                updated = section.model_copy(update=updates)
                self._sections[i] = updated
                return updated
        return None

    async def delete_education_section(self, profile_id: int, section_id: int) -> bool:
        for i, section in enumerate(self._sections):
            if section.id == section_id and section.profile_id == profile_id:
                self._sections.pop(i)
                return True
        return False

    async def count_education_entries(self, section_id: int) -> int:
        return sum(1 for e in self._entries if e.section_id == section_id)

    async def create_education_entry(
        self, section_id: int, data: EducationEntryCreate
    ) -> EducationEntryRead:
        entry = EducationEntryRead(
            id=self._next_entry_id,
            section_id=section_id,
            content=data.content,
            display_order=data.display_order,
        )
        self._entries.append(entry)
        self._next_entry_id += 1
        return entry

    async def list_education_entries(self, section_id: int) -> list[EducationEntryRead]:
        return [e for e in self._entries if e.section_id == section_id]

    async def update_education_entry(
        self, section_id: int, entry_id: int, data: EducationEntryUpdate
    ) -> EducationEntryRead | None:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                updates = data.model_dump(exclude_unset=True)
                updated = entry.model_copy(update=updates)
                self._entries[i] = updated
                return updated
        return None

    async def delete_education_entry(self, section_id: int, entry_id: int) -> bool:
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id and entry.section_id == section_id:
                self._entries.pop(i)
                return True
        return False


@pytest.fixture
def fake_db() -> FakeEducationSectionRepository:
    return FakeEducationSectionRepository()


@pytest.fixture
def service(fake_db: FakeEducationSectionRepository) -> EducationSectionService:
    return EducationSectionService(fake_db)


# --- Section happy paths ---


async def test_create_education_section_happy_path(service: EducationSectionService) -> None:
    data = EducationSectionCreate(title="Bachelor of Computer Science", organisation="MIT")
    result = await service.create_education_section(1, data)
    assert result.id is not None
    assert result.profile_id == 1
    assert result.title == "Bachelor of Computer Science"
    assert result.is_enabled is True


async def test_create_education_section_postcondition_profile_id_matches(
    service: EducationSectionService,
) -> None:
    data = EducationSectionCreate(title="MSc Data Science")
    result = await service.create_education_section(2, data)
    assert result.profile_id == 2


async def test_list_education_sections_ordered_by_display_order(
    service: EducationSectionService,
) -> None:
    await service.create_education_section(
        1, EducationSectionCreate(title="B", display_order=2)
    )
    await service.create_education_section(
        1, EducationSectionCreate(title="A", display_order=1)
    )
    result = await service.list_education_sections(1)
    assert [s.title for s in result] == ["A", "B"]


async def test_get_education_section_happy_path(service: EducationSectionService) -> None:
    created = await service.create_education_section(
        1, EducationSectionCreate(title="BSc Engineering")
    )
    result = await service.get_education_section(1, created.id)
    assert result.id == created.id
    assert result.title == "BSc Engineering"


async def test_get_education_section_not_found_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.get_education_section(1, 999)


async def test_update_education_section_happy_path(service: EducationSectionService) -> None:
    created = await service.create_education_section(
        1, EducationSectionCreate(title="Old Title")
    )
    result = await service.update_education_section(
        1, created.id, EducationSectionUpdate(title="New Title")
    )
    assert result.title == "New Title"


async def test_update_education_section_not_found_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.update_education_section(1, 999, EducationSectionUpdate(title="X"))


async def test_toggle_is_enabled_false(service: EducationSectionService) -> None:
    created = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    result = await service.update_education_section(
        1, created.id, EducationSectionUpdate(is_enabled=False)
    )
    assert result.is_enabled is False


async def test_toggle_is_enabled_back_to_true(service: EducationSectionService) -> None:
    created = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    await service.update_education_section(
        1, created.id, EducationSectionUpdate(is_enabled=False)
    )
    result = await service.update_education_section(
        1, created.id, EducationSectionUpdate(is_enabled=True)
    )
    assert result.is_enabled is True


async def test_delete_education_section(service: EducationSectionService) -> None:
    created = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    await service.delete_education_section(1, created.id)
    with pytest.raises(ValueError, match=f"Section {created.id} not found"):
        await service.get_education_section(1, created.id)


async def test_delete_education_section_not_found_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(ValueError, match="Section 999 not found"):
        await service.delete_education_section(1, 999)


# --- Entry happy paths ---


async def test_create_entry_happy_path(service: EducationSectionService) -> None:
    section = await service.create_education_section(
        1, EducationSectionCreate(title="BSc Computing")
    )
    result = await service.create_entry(
        1, section.id, EducationEntryCreate(content="Graduated with distinction")
    )
    assert result.id is not None
    assert result.section_id == section.id
    assert result.content == "Graduated with distinction"


async def test_create_entry_postcondition_section_id_matches(
    service: EducationSectionService,
) -> None:
    section = await service.create_education_section(2, EducationSectionCreate(title="BSc"))
    result = await service.create_entry(
        2, section.id, EducationEntryCreate(content="Dean's list")
    )
    assert result.section_id == section.id


async def test_create_entry_limit_exceeded_raises(
    service: EducationSectionService,
    fake_db: FakeEducationSectionRepository,
) -> None:
    section = await service.create_education_section(
        1, EducationSectionCreate(title="BSc")
    )
    for i in range(MAX_ENTRIES_PER_SECTION):
        fake_db._entries.append(
            EducationEntryRead(
                id=i + 1, section_id=section.id, content=f"entry {i}", display_order=i
            )
        )
    fake_db._next_entry_id = MAX_ENTRIES_PER_SECTION + 1

    with pytest.raises(EntryLimitExceededError):
        await service.create_entry(1, section.id, EducationEntryCreate(content="overflow"))


async def test_create_section_limit_exceeded_raises(
    service: EducationSectionService,
    fake_db: FakeEducationSectionRepository,
) -> None:
    for i in range(MAX_SECTIONS_PER_PROFILE):
        fake_db._sections.append(
            EducationSectionRead(
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
        await service.create_education_section(1, EducationSectionCreate(title="overflow"))


async def test_update_entry_happy_path(service: EducationSectionService) -> None:
    section = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    created = await service.create_entry(
        1, section.id, EducationEntryCreate(content="old content")
    )
    result = await service.update_entry(
        1, section.id, created.id, EducationEntryUpdate(content="new content")
    )
    assert result.content == "new content"


async def test_update_entry_not_found_raises(service: EducationSectionService) -> None:
    section = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.update_entry(1, section.id, 999, EducationEntryUpdate(content="x"))


async def test_delete_entry(service: EducationSectionService) -> None:
    section = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    created = await service.create_entry(
        1, section.id, EducationEntryCreate(content="bullet")
    )
    await service.delete_entry(1, section.id, created.id)
    entries = await service.list_entries(section.id)
    assert all(e.id != created.id for e in entries)


async def test_delete_entry_not_found_raises(service: EducationSectionService) -> None:
    section = await service.create_education_section(1, EducationSectionCreate(title="BSc"))
    with pytest.raises(ValueError, match="Entry 999 not found"):
        await service.delete_entry(1, section.id, 999)


# --- Cross-profile access prevention ---


async def test_create_entry_section_not_found_raises() -> None:
    fake_db = FakeEducationSectionRepository()
    svc = EducationSectionService(fake_db)

    with pytest.raises(ValueError, match="Section 999 not found"):
        await svc.create_entry(1, 999, EducationEntryCreate(content="bullet"))


async def test_create_entry_cross_profile_raises() -> None:
    """Section belongs to profile 1 — profile 2 must not create entries on it."""
    fake_db = FakeEducationSectionRepository()
    svc = EducationSectionService(fake_db)

    section = await svc.create_education_section(1, EducationSectionCreate(title="BSc"))

    with pytest.raises(ValueError, match="Section"):
        await svc.create_entry(2, section.id, EducationEntryCreate(content="bullet"))


async def test_update_entry_cross_profile_raises() -> None:
    fake_db = FakeEducationSectionRepository()
    svc = EducationSectionService(fake_db)

    section = await svc.create_education_section(1, EducationSectionCreate(title="BSc"))
    entry = await svc.create_entry(1, section.id, EducationEntryCreate(content="bullet"))

    with pytest.raises(ValueError, match="Section"):
        await svc.update_entry(2, section.id, entry.id, EducationEntryUpdate(content="new"))


async def test_delete_entry_cross_profile_raises() -> None:
    fake_db = FakeEducationSectionRepository()
    svc = EducationSectionService(fake_db)

    section = await svc.create_education_section(1, EducationSectionCreate(title="BSc"))
    entry = await svc.create_entry(1, section.id, EducationEntryCreate(content="bullet"))

    with pytest.raises(ValueError, match="Section"):
        await svc.delete_entry(2, section.id, entry.id)


# --- Profile-not-found raises ---


async def test_create_section_profile_not_found_raises(service: EducationSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.create_education_section(99, EducationSectionCreate(title="X"))


async def test_list_sections_profile_not_found_raises(service: EducationSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.list_education_sections(99)


async def test_get_section_profile_not_found_raises(service: EducationSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.get_education_section(99, 1)


async def test_update_section_profile_not_found_raises(service: EducationSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.update_education_section(99, 1, EducationSectionUpdate(title="X"))


async def test_delete_section_profile_not_found_raises(service: EducationSectionService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.delete_education_section(99, 1)


# --- Tiger Style assertion failures ---


async def test_tiger_create_section_profile_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_education_section(0, EducationSectionCreate(title="X"))


async def test_tiger_get_section_section_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.get_education_section(1, 0)


async def test_tiger_update_section_section_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.update_education_section(1, 0, EducationSectionUpdate(title="X"))


async def test_tiger_delete_section_section_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.delete_education_section(1, 0)


async def test_tiger_create_entry_section_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_entry(1, 0, EducationEntryCreate(content="x"))


async def test_tiger_update_entry_entry_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.update_entry(1, 1, 0, EducationEntryUpdate(content="x"))


async def test_tiger_delete_entry_entry_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.delete_entry(1, 1, 0)


async def test_tiger_create_entry_profile_id_zero_raises(
    service: EducationSectionService,
) -> None:
    with pytest.raises(AssertionError):
        await service.create_entry(0, 1, EducationEntryCreate(content="x"))


async def test_get_education_section_returns_populated_entries(
    service: EducationSectionService,
) -> None:
    section = await service.create_education_section(
        1, EducationSectionCreate(title="BSc Computing")
    )
    await service.create_entry(
        1, section.id, EducationEntryCreate(content="Graduated with distinction")
    )
    result = await service.get_education_section(1, section.id)
    assert len(result.entries) == 1
    assert result.entries[0].content == "Graduated with distinction"


async def test_list_education_sections_entries_not_populated() -> None:
    """list endpoint must return entries=[] (not eagerly loaded)."""
    fake_db = FakeEducationSectionRepository()
    fake_db._profiles.add(1)
    svc = EducationSectionService(fake_db)

    await svc.create_education_section(1, EducationSectionCreate(title="BSc A"))
    sections = await svc.list_education_sections(1)

    assert sections[0].entries == []
