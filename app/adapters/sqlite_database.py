import logging
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.constants.limits import MAX_CONTACTS_PER_PROFILE
from app.exceptions import ContactLimitExceededError
from app.models.profile import Profile, ProfileContact
from app.models.sections.education import EducationEntry, EducationSection
from app.models.sections.experience import ExperienceEntry, ExperienceSection
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.schemas.sections.education import (
    EducationEntryCreate,
    EducationEntryRead,
    EducationEntryUpdate,
    EducationSectionCreate,
    EducationSectionRead,
    EducationSectionUpdate,
)
from app.schemas.sections.experience import (
    ExperienceEntryCreate,
    ExperienceEntryRead,
    ExperienceEntryUpdate,
    ExperienceSectionCreate,
    ExperienceSectionRead,
    ExperienceSectionUpdate,
)

logger = logging.getLogger(__name__)


class SQLiteDatabaseAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def execute(self, statement: Any) -> Any:
        return await self._session.execute(statement)

    async def fetch_one(self, statement: Any) -> Any | None:
        result = await self._session.execute(statement)
        return result.scalar_one_or_none()

    async def fetch_all(self, statement: Any) -> list[Any]:
        result = await self._session.execute(statement)
        return list(result.scalars().all())

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        profile = Profile(name=data.name, description=data.description)
        self._session.add(profile)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_profile failed")
            await self._session.rollback()
            raise
        await self._session.refresh(profile)
        assert profile.id is not None, "DB did not assign an id after insert"
        return ProfileRead.model_validate(profile)

    async def list_profiles(self) -> list[ProfileRead]:
        result = await self._session.execute(select(Profile))
        profiles = list(result.scalars().all())
        validated = [ProfileRead.model_validate(p) for p in profiles]
        assert isinstance(validated, list), "list_profiles must return a list"
        return validated

    async def get_profile(self, profile_id: int) -> ProfileRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None
        return ProfileRead.model_validate(profile)

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("update_profile failed for profile_id=%s", profile_id)
            await self._session.rollback()
            raise
        await self._session.refresh(profile)
        return ProfileRead.model_validate(profile)

    async def delete_profile(self, profile_id: int) -> bool:
        assert profile_id > 0, "profile_id must be a positive integer"
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return False
        await self._session.delete(profile)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("delete_profile failed for profile_id=%s", profile_id)
            await self._session.rollback()
            raise
        return True

    async def profile_exists(self, profile_id: int) -> bool:
        assert profile_id > 0, "profile_id must be a positive integer"
        return await self._session.get(Profile, profile_id) is not None

    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        existing = await self._session.execute(
            select(ProfileContact).where(ProfileContact.profile_id == profile_id)
        )
        count = len(list(existing.scalars().all()))
        if count >= MAX_CONTACTS_PER_PROFILE:
            raise ContactLimitExceededError(
                f"profile {profile_id} has {count} contacts; max {MAX_CONTACTS_PER_PROFILE} allowed"
            )
        contact = ProfileContact(
            profile_id=profile_id,
            type=data.type,
            value=data.value,
        )
        self._session.add(contact)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_contact failed for profile_id=%s", profile_id)
            await self._session.rollback()
            raise
        await self._session.refresh(contact)
        assert contact.id is not None, "DB did not assign an id after insert"
        return ContactRead.model_validate(contact)

    async def list_contacts(self, profile_id: int) -> list[ContactRead]:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._session.execute(
            select(ProfileContact).where(ProfileContact.profile_id == profile_id)
        )
        contacts = list(result.scalars().all())
        return [ContactRead.model_validate(c) for c in contacts]

    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        result = await self._session.execute(
            select(ProfileContact).where(
                ProfileContact.id == contact_id,
                ProfileContact.profile_id == profile_id,
            )
        )
        contact = result.scalar_one_or_none()
        if contact is None:
            return None
        return ContactRead.model_validate(contact)

    async def update_contact(
        self, profile_id: int, contact_id: int, data: ContactUpdate
    ) -> ContactRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        result = await self._session.execute(
            select(ProfileContact).where(
                ProfileContact.id == contact_id,
                ProfileContact.profile_id == profile_id,
            )
        )
        contact = result.scalar_one_or_none()
        if contact is None:
            return None
        update_dict = {
            k: v for k, v in data.model_dump(exclude_unset=True).items() if v is not None
        }
        for key, value in update_dict.items():
            setattr(contact, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "update_contact failed for profile_id=%s contact_id=%s",
                profile_id,
                contact_id,
            )
            await self._session.rollback()
            raise
        await self._session.refresh(contact)
        return ContactRead.model_validate(contact)

    async def delete_contact(self, profile_id: int, contact_id: int) -> bool:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        result = await self._session.execute(
            select(ProfileContact).where(
                ProfileContact.id == contact_id,
                ProfileContact.profile_id == profile_id,
            )
        )
        contact = result.scalar_one_or_none()
        if contact is None:
            return False
        await self._session.delete(contact)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "delete_contact failed for profile_id=%s contact_id=%s",
                profile_id,
                contact_id,
            )
            await self._session.rollback()
            raise
        return True

    async def count_sections_for_profile(self, profile_id: int) -> int:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._session.execute(
            select(func.count())
            .select_from(ExperienceSection)
            .where(ExperienceSection.profile_id == profile_id)
        )
        count = result.scalar() or 0
        assert count >= 0, "count_sections_for_profile must return non-negative"
        return count

    async def create_experience_section(
        self, profile_id: int, data: ExperienceSectionCreate
    ) -> ExperienceSectionRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        section = ExperienceSection(
            profile_id=profile_id,
            title=data.title,
            organisation=data.organisation,
            start_date=data.start_date,
            end_date=data.end_date,
            is_enabled=data.is_enabled,
            display_order=data.display_order,
        )
        self._session.add(section)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_experience_section failed for profile_id=%s", profile_id)
            await self._session.rollback()
            raise
        await self._session.refresh(section)
        assert section.id is not None, "DB did not assign an id after insert"
        result = self._section_to_read(section)
        assert result.profile_id == profile_id, "returned section profile_id must match request"
        assert result.entries == [], "create must return section with empty entries"
        return result

    @staticmethod
    def _section_to_read(section: ExperienceSection) -> ExperienceSectionRead:
        return ExperienceSectionRead.model_validate(
            {
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
            }
        )

    async def list_experience_sections(self, profile_id: int) -> list[ExperienceSectionRead]:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceSection)
            .where(ExperienceSection.profile_id == profile_id)
            .order_by(ExperienceSection.display_order)
        )
        sections = list(result.scalars().all())
        validated = [self._section_to_read(s) for s in sections]
        assert isinstance(validated, list), "list_experience_sections must return a list"
        return validated

    async def get_experience_section(
        self, profile_id: int, section_id: int
    ) -> ExperienceSectionRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        stmt = (
            select(ExperienceSection)
            .options(selectinload(ExperienceSection.entries))
            .where(
                ExperienceSection.id == section_id,
                ExperienceSection.profile_id == profile_id,
            )
        )
        result = await self._session.execute(stmt)
        section = result.scalar_one_or_none()
        if section is None:
            return None
        return ExperienceSectionRead.model_validate(section)

    async def update_experience_section(
        self, profile_id: int, section_id: int, data: ExperienceSectionUpdate
    ) -> ExperienceSectionRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceSection).where(
                ExperienceSection.id == section_id,
                ExperienceSection.profile_id == profile_id,
            )
        )
        section = result.scalar_one_or_none()
        if section is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(section, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "update_experience_section failed for profile_id=%s section_id=%s",
                profile_id,
                section_id,
            )
            await self._session.rollback()
            raise
        refreshed = await self._session.execute(
            select(ExperienceSection)
            .options(selectinload(ExperienceSection.entries))
            .where(ExperienceSection.id == section.id)
        )
        return ExperienceSectionRead.model_validate(refreshed.scalar_one())

    async def delete_experience_section(self, profile_id: int, section_id: int) -> bool:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceSection).where(
                ExperienceSection.id == section_id,
                ExperienceSection.profile_id == profile_id,
            )
        )
        section = result.scalar_one_or_none()
        if section is None:
            return False
        await self._session.delete(section)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "delete_experience_section failed for profile_id=%s section_id=%s",
                profile_id,
                section_id,
            )
            await self._session.rollback()
            raise
        return True

    async def count_entries(self, section_id: int) -> int:
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(func.count())
            .select_from(ExperienceEntry)
            .where(ExperienceEntry.section_id == section_id)
        )
        count = result.scalar() or 0
        assert count >= 0, "count_entries must return non-negative"
        return count

    async def create_entry(
        self, section_id: int, data: ExperienceEntryCreate
    ) -> ExperienceEntryRead:
        assert section_id > 0, "section_id must be a positive integer"
        entry = ExperienceEntry(
            section_id=section_id,
            content=data.content,
            display_order=data.display_order,
        )
        self._session.add(entry)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_entry failed for section_id=%s", section_id)
            await self._session.rollback()
            raise
        await self._session.refresh(entry)
        assert entry.id is not None, "DB did not assign an id after insert"
        return ExperienceEntryRead.model_validate(entry)

    async def list_entries(self, section_id: int) -> list[ExperienceEntryRead]:
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceEntry)
            .where(ExperienceEntry.section_id == section_id)
            .order_by(ExperienceEntry.display_order)
        )
        entries = list(result.scalars().all())
        validated = [ExperienceEntryRead.model_validate(e) for e in entries]
        assert isinstance(validated, list), "list_entries must return a list"
        return validated

    async def update_entry(
        self, section_id: int, entry_id: int, data: ExperienceEntryUpdate
    ) -> ExperienceEntryRead | None:
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceEntry).where(
                ExperienceEntry.id == entry_id,
                ExperienceEntry.section_id == section_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(entry, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "update_entry failed for section_id=%s entry_id=%s", section_id, entry_id
            )
            await self._session.rollback()
            raise
        await self._session.refresh(entry)
        return ExperienceEntryRead.model_validate(entry)

    async def delete_entry(self, section_id: int, entry_id: int) -> bool:
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        result = await self._session.execute(
            select(ExperienceEntry).where(
                ExperienceEntry.id == entry_id,
                ExperienceEntry.section_id == section_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            return False
        await self._session.delete(entry)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "delete_entry failed for section_id=%s entry_id=%s", section_id, entry_id
            )
            await self._session.rollback()
            raise
        return True

    @staticmethod
    def _education_section_to_read(section: EducationSection) -> EducationSectionRead:
        return EducationSectionRead.model_validate(
            {
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
            }
        )

    async def count_education_sections_for_profile(self, profile_id: int) -> int:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._session.execute(
            select(func.count())
            .select_from(EducationSection)
            .where(EducationSection.profile_id == profile_id)
        )
        count = result.scalar() or 0
        assert count >= 0, "count_education_sections_for_profile must return non-negative"
        return count

    async def create_education_section(
        self, profile_id: int, data: EducationSectionCreate
    ) -> EducationSectionRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        section = EducationSection(
            profile_id=profile_id,
            title=data.title,
            organisation=data.organisation,
            start_date=data.start_date,
            end_date=data.end_date,
            is_enabled=data.is_enabled,
            display_order=data.display_order,
        )
        self._session.add(section)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_education_section failed for profile_id=%s", profile_id)
            await self._session.rollback()
            raise
        await self._session.refresh(section)
        assert section.id is not None, "DB did not assign an id after insert"
        result = self._education_section_to_read(section)
        assert result.profile_id == profile_id, "returned section profile_id must match request"
        assert result.entries == [], "create must return section with empty entries"
        return result

    async def list_education_sections(self, profile_id: int) -> list[EducationSectionRead]:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._session.execute(
            select(EducationSection)
            .where(EducationSection.profile_id == profile_id)
            .order_by(EducationSection.display_order)
        )
        sections = list(result.scalars().all())
        validated = [self._education_section_to_read(s) for s in sections]
        assert isinstance(validated, list), "list_education_sections must return a list"
        return validated

    async def get_education_section(
        self, profile_id: int, section_id: int
    ) -> EducationSectionRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        stmt = (
            select(EducationSection)
            .options(selectinload(EducationSection.entries))
            .where(
                EducationSection.id == section_id,
                EducationSection.profile_id == profile_id,
            )
        )
        result = await self._session.execute(stmt)
        section = result.scalar_one_or_none()
        if section is None:
            return None
        return EducationSectionRead.model_validate(section)

    async def update_education_section(
        self, profile_id: int, section_id: int, data: EducationSectionUpdate
    ) -> EducationSectionRead | None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(EducationSection).where(
                EducationSection.id == section_id,
                EducationSection.profile_id == profile_id,
            )
        )
        section = result.scalar_one_or_none()
        if section is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(section, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "update_education_section failed for profile_id=%s section_id=%s",
                profile_id,
                section_id,
            )
            await self._session.rollback()
            raise
        refreshed = await self._session.execute(
            select(EducationSection)
            .options(selectinload(EducationSection.entries))
            .where(EducationSection.id == section.id, EducationSection.profile_id == profile_id)
        )
        return EducationSectionRead.model_validate(refreshed.scalar_one())

    async def delete_education_section(self, profile_id: int, section_id: int) -> bool:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(EducationSection).where(
                EducationSection.id == section_id,
                EducationSection.profile_id == profile_id,
            )
        )
        section = result.scalar_one_or_none()
        if section is None:
            return False
        await self._session.delete(section)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "delete_education_section failed for profile_id=%s section_id=%s",
                profile_id,
                section_id,
            )
            await self._session.rollback()
            raise
        return True

    async def count_education_entries(self, section_id: int) -> int:
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(func.count())
            .select_from(EducationEntry)
            .where(EducationEntry.section_id == section_id)
        )
        count = result.scalar() or 0
        assert count >= 0, "count_entries must return non-negative"
        return count

    async def create_education_entry(
        self, section_id: int, data: EducationEntryCreate
    ) -> EducationEntryRead:
        assert section_id > 0, "section_id must be a positive integer"
        entry = EducationEntry(
            section_id=section_id,
            content=data.content,
            display_order=data.display_order,
        )
        self._session.add(entry)
        try:
            await self._session.commit()
        except Exception:
            logger.exception("create_education_entry failed for section_id=%s", section_id)
            await self._session.rollback()
            raise
        await self._session.refresh(entry)
        assert entry.id is not None, "DB did not assign an id after insert"
        return EducationEntryRead.model_validate(entry)

    async def list_education_entries(self, section_id: int) -> list[EducationEntryRead]:
        assert section_id > 0, "section_id must be a positive integer"
        result = await self._session.execute(
            select(EducationEntry)
            .where(EducationEntry.section_id == section_id)
            .order_by(EducationEntry.display_order)
        )
        entries = list(result.scalars().all())
        validated = [EducationEntryRead.model_validate(e) for e in entries]
        assert isinstance(validated, list), "list_education_entries must return a list"
        return validated

    async def update_education_entry(
        self, section_id: int, entry_id: int, data: EducationEntryUpdate
    ) -> EducationEntryRead | None:
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        result = await self._session.execute(
            select(EducationEntry).where(
                EducationEntry.id == entry_id,
                EducationEntry.section_id == section_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(entry, key, value)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "update_education_entry failed for section_id=%s entry_id=%s",
                section_id,
                entry_id,
            )
            await self._session.rollback()
            raise
        await self._session.refresh(entry)
        return EducationEntryRead.model_validate(entry)

    async def delete_education_entry(self, section_id: int, entry_id: int) -> bool:
        assert section_id > 0, "section_id must be a positive integer"
        assert entry_id > 0, "entry_id must be a positive integer"
        result = await self._session.execute(
            select(EducationEntry).where(
                EducationEntry.id == entry_id,
                EducationEntry.section_id == section_id,
            )
        )
        entry = result.scalar_one_or_none()
        if entry is None:
            return False
        await self._session.delete(entry)
        try:
            await self._session.commit()
        except Exception:
            logger.exception(
                "delete_education_entry failed for section_id=%s entry_id=%s",
                section_id,
                entry_id,
            )
            await self._session.rollback()
            raise
        return True
