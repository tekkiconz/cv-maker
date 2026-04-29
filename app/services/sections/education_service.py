from __future__ import annotations

from app.constants.limits import MAX_ENTRIES_PER_SECTION, MAX_SECTIONS_PER_PROFILE
from app.exceptions import EntryLimitExceededError, SectionLimitExceededError
from app.interfaces.database import EducationSectionRepositoryProtocol
from app.schemas.sections.education import (
    EducationEntryCreate,
    EducationEntryRead,
    EducationEntryUpdate,
    EducationSectionCreate,
    EducationSectionRead,
    EducationSectionUpdate,
)


class EducationSectionService:
    def __init__(self, db: EducationSectionRepositoryProtocol) -> None:
        self._db = db

    async def create_education_section(
        self, profile_id: int, data: EducationSectionCreate
    ) -> EducationSectionRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        count = await self._db.count_sections_for_profile(profile_id)
        if count >= MAX_SECTIONS_PER_PROFILE:
            raise SectionLimitExceededError(
                f"profile {profile_id} has {count} sections; max {MAX_SECTIONS_PER_PROFILE}"
            )
        result = await self._db.create_education_section(profile_id, data)
        assert result.profile_id == profile_id, "returned section profile_id must match request"
        return result

    async def list_education_sections(self, profile_id: int) -> list[EducationSectionRead]:
        assert profile_id > 0, "profile_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        result = await self._db.list_education_sections(profile_id)
        assert isinstance(result, list), "list_education_sections must return a list"
        return result

    async def get_education_section(
        self, profile_id: int, section_id: int
    ) -> EducationSectionRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        result = await self._db.get_education_section(profile_id, section_id)
        if result is None:
            raise ValueError(f"Section {section_id} not found")
        return result

    async def update_education_section(
        self, profile_id: int, section_id: int, data: EducationSectionUpdate
    ) -> EducationSectionRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        result = await self._db.update_education_section(profile_id, section_id, data)
        if result is None:
            raise ValueError(f"Section {section_id} not found")
        return result

    async def delete_education_section(self, profile_id: int, section_id: int) -> None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        deleted = await self._db.delete_education_section(profile_id, section_id)
        if not deleted:
            raise ValueError(f"Section {section_id} not found")

    async def create_entry(
        self, profile_id: int, section_id: int, data: EducationEntryCreate
    ) -> EducationEntryRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        section = await self._db.get_education_section(profile_id, section_id)
        if section is None:
            raise ValueError(f"Section {section_id} not found")
        count = await self._db.count_education_entries(section_id)
        if count >= MAX_ENTRIES_PER_SECTION:
            raise EntryLimitExceededError(
                f"section {section_id} has {count} entries; max {MAX_ENTRIES_PER_SECTION}"
            )
        result = await self._db.create_education_entry(section_id, data)
        assert result.section_id == section_id, "returned entry section_id must match request"
        return result

    async def list_entries(self, section_id: int) -> list[EducationEntryRead]:
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._db.list_education_entries(section_id)
        assert isinstance(result, list), "list_entries must return a list"
        return result

    async def update_entry(
        self, profile_id: int, section_id: int, entry_id: int, data: EducationEntryUpdate
    ) -> EducationEntryRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        section = await self._db.get_education_section(profile_id, section_id)
        if section is None:
            raise ValueError(f"Section {section_id} not found")
        result = await self._db.update_education_entry(section_id, entry_id, data)
        if result is None:
            raise ValueError(f"Entry {entry_id} not found")
        return result

    async def delete_entry(self, profile_id: int, section_id: int, entry_id: int) -> None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        section = await self._db.get_education_section(profile_id, section_id)
        if section is None:
            raise ValueError(f"Section {section_id} not found")
        deleted = await self._db.delete_education_entry(section_id, entry_id)
        if not deleted:
            raise ValueError(f"Entry {entry_id} not found")
