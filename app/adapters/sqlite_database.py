from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.limits import MAX_CONTACTS_PER_PROFILE
from app.exceptions import ContactLimitExceededError
from app.models.profile import Profile, ProfileContact
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate


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
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None
        return ProfileRead.model_validate(profile)

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None:
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return None
        update_dict = data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(profile, key, value)
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
        await self._session.refresh(profile)
        return ProfileRead.model_validate(profile)

    async def delete_profile(self, profile_id: int) -> bool:
        profile = await self._session.get(Profile, profile_id)
        if profile is None:
            return False
        await self._session.delete(profile)
        try:
            await self._session.commit()
        except Exception:
            await self._session.rollback()
            raise
        return True

    async def profile_exists(self, profile_id: int) -> bool:
        return await self._session.get(Profile, profile_id) is not None

    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead:
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
            await self._session.rollback()
            raise
        await self._session.refresh(contact)
        assert contact.id is not None, "DB did not assign an id after insert"
        return ContactRead.model_validate(contact)

    async def list_contacts(self, profile_id: int) -> list[ContactRead]:
        result = await self._session.execute(
            select(ProfileContact).where(ProfileContact.profile_id == profile_id)
        )
        contacts = list(result.scalars().all())
        return [ContactRead.model_validate(c) for c in contacts]

    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None:
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
            await self._session.rollback()
            raise
        await self._session.refresh(contact)
        return ContactRead.model_validate(contact)

    async def delete_contact(self, profile_id: int, contact_id: int) -> bool:
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
            await self._session.rollback()
            raise
        return True
