from app.constants.enums import ContactType
from app.interfaces.database import ContactRepositoryProtocol
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate


class ContactService:
    def __init__(self, db: ContactRepositoryProtocol) -> None:
        self._db = db

    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert data.type in ContactType.__members__.values(), f"invalid ContactType: {data.type}"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        result = await self._db.create_contact(profile_id, data)
        assert result.profile_id == profile_id, "returned contact profile_id must match request"
        return result

    async def list_contacts(self, profile_id: int) -> list[ContactRead]:
        assert profile_id > 0, "profile_id must be a positive integer"
        if not await self._db.profile_exists(profile_id):
            raise ValueError(f"Profile {profile_id} not found")
        result = await self._db.list_contacts(profile_id)
        assert isinstance(result, list), "list_contacts must return a list"
        return result

    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        result = await self._db.get_contact(profile_id, contact_id)
        if result is None:
            raise ValueError(f"Contact {contact_id} not found")
        return result

    async def update_contact(
        self, profile_id: int, contact_id: int, data: ContactUpdate
    ) -> ContactRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        result = await self._db.update_contact(profile_id, contact_id, data)
        if result is None:
            raise ValueError(f"Contact {contact_id} not found")
        return result

    async def delete_contact(self, profile_id: int, contact_id: int) -> None:
        assert profile_id > 0, "profile_id must be a positive integer"
        assert contact_id > 0, "contact_id must be a positive integer"
        deleted = await self._db.delete_contact(profile_id, contact_id)
        if not deleted:
            raise ValueError(f"Contact {contact_id} not found")
