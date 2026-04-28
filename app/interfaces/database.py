from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
    from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
    from app.schemas.sections.experience import (
        ExperienceEntryCreate,
        ExperienceEntryRead,
        ExperienceEntryUpdate,
        ExperienceSectionCreate,
        ExperienceSectionRead,
        ExperienceSectionUpdate,
    )


@runtime_checkable
class DatabaseProtocol(Protocol):
    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    async def execute(self, statement: Any) -> Any: ...

    async def fetch_one(self, statement: Any) -> Any | None: ...

    async def fetch_all(self, statement: Any) -> list[Any]: ...


@runtime_checkable
class ProfileRepositoryProtocol(Protocol):
    async def create_profile(self, data: ProfileCreate) -> ProfileRead: ...

    async def list_profiles(self) -> list[ProfileRead]: ...

    async def get_profile(self, profile_id: int) -> ProfileRead | None: ...

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None: ...

    async def delete_profile(self, profile_id: int) -> bool: ...


@runtime_checkable
class ContactRepositoryProtocol(Protocol):
    async def profile_exists(self, profile_id: int) -> bool: ...

    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead: ...

    async def list_contacts(self, profile_id: int) -> list[ContactRead]: ...

    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None: ...

    async def update_contact(
        self, profile_id: int, contact_id: int, data: ContactUpdate
    ) -> ContactRead | None: ...

    async def delete_contact(self, profile_id: int, contact_id: int) -> bool: ...


@runtime_checkable
class ExperienceSectionRepositoryProtocol(Protocol):
    async def profile_exists(self, profile_id: int) -> bool: ...

    async def create_experience_section(
        self, profile_id: int, data: ExperienceSectionCreate
    ) -> ExperienceSectionRead: ...

    async def list_experience_sections(self, profile_id: int) -> list[ExperienceSectionRead]: ...

    async def get_experience_section(
        self, profile_id: int, section_id: int
    ) -> ExperienceSectionRead | None: ...

    async def update_experience_section(
        self, profile_id: int, section_id: int, data: ExperienceSectionUpdate
    ) -> ExperienceSectionRead | None: ...

    async def delete_experience_section(self, profile_id: int, section_id: int) -> bool: ...

    async def create_entry(
        self, section_id: int, data: ExperienceEntryCreate
    ) -> ExperienceEntryRead: ...

    async def list_entries(self, section_id: int) -> list[ExperienceEntryRead]: ...

    async def update_entry(
        self, section_id: int, entry_id: int, data: ExperienceEntryUpdate
    ) -> ExperienceEntryRead | None: ...

    async def delete_entry(self, section_id: int, entry_id: int) -> bool: ...

    async def count_entries(self, section_id: int) -> int: ...

    async def count_sections_for_profile(self, profile_id: int) -> int: ...
