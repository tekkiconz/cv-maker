import pytest

from app.constants.enums import ContactType
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.services.contact_service import ContactService


class FakeContactRepository:
    def __init__(self) -> None:
        self._contacts: list[ContactRead] = []
        self._profiles: set[int] = {1, 2, 3}
        self._next_id: int = 1

    async def profile_exists(self, profile_id: int) -> bool:
        return profile_id in self._profiles

    async def create_contact(self, profile_id: int, data: ContactCreate) -> ContactRead:
        contact = ContactRead(
            id=self._next_id,
            profile_id=profile_id,
            type=data.type,
            value=data.value,
        )
        self._contacts.append(contact)
        self._next_id += 1
        return contact

    async def list_contacts(self, profile_id: int) -> list[ContactRead]:
        return [c for c in self._contacts if c.profile_id == profile_id]

    async def get_contact(self, profile_id: int, contact_id: int) -> ContactRead | None:
        return next(
            (c for c in self._contacts if c.id == contact_id and c.profile_id == profile_id),
            None,
        )

    async def update_contact(
        self, profile_id: int, contact_id: int, data: ContactUpdate
    ) -> ContactRead | None:
        for i, contact in enumerate(self._contacts):
            if contact.id == contact_id and contact.profile_id == profile_id:
                updates = data.model_dump(exclude_unset=True)
                updated = contact.model_copy(update=updates)
                self._contacts[i] = updated
                return updated
        return None

    async def delete_contact(self, profile_id: int, contact_id: int) -> bool:
        for i, contact in enumerate(self._contacts):
            if contact.id == contact_id and contact.profile_id == profile_id:
                self._contacts.pop(i)
                return True
        return False


@pytest.fixture
def fake_db() -> FakeContactRepository:
    return FakeContactRepository()


@pytest.fixture
def service(fake_db: FakeContactRepository) -> ContactService:
    return ContactService(fake_db)


async def test_create_contact_happy_path(service: ContactService) -> None:
    data = ContactCreate(type=ContactType.email, value="huy@example.com")
    result = await service.create_contact(1, data)
    assert result.id is not None
    assert result.profile_id == 1
    assert result.type == ContactType.email
    assert result.value == "huy@example.com"


async def test_create_contact_postcondition_profile_id_matches(service: ContactService) -> None:
    data = ContactCreate(type=ContactType.github, value="huy")
    result = await service.create_contact(2, data)
    assert result.profile_id == 2


async def test_list_contacts_returns_list(service: ContactService) -> None:
    await service.create_contact(1, ContactCreate(type=ContactType.email, value="a@b.com"))
    await service.create_contact(1, ContactCreate(type=ContactType.phone, value="123"))
    result = await service.list_contacts(1)
    assert isinstance(result, list)
    assert len(result) == 2


async def test_list_contacts_scoped_to_profile(service: ContactService) -> None:
    await service.create_contact(1, ContactCreate(type=ContactType.email, value="a@b.com"))
    await service.create_contact(2, ContactCreate(type=ContactType.email, value="c@d.com"))
    result = await service.list_contacts(1)
    assert len(result) == 1
    assert result[0].profile_id == 1


async def test_get_contact(service: ContactService) -> None:
    created = await service.create_contact(
        1, ContactCreate(type=ContactType.email, value="a@b.com")
    )
    result = await service.get_contact(1, created.id)
    assert result.id == created.id


async def test_get_contact_not_found_raises(service: ContactService) -> None:
    with pytest.raises(ValueError, match="Contact 999 not found"):
        await service.get_contact(1, 999)


async def test_update_contact(service: ContactService) -> None:
    created = await service.create_contact(
        1, ContactCreate(type=ContactType.email, value="old@example.com")
    )
    result = await service.update_contact(1, created.id, ContactUpdate(value="new@example.com"))
    assert result.value == "new@example.com"


async def test_update_contact_not_found_raises(service: ContactService) -> None:
    with pytest.raises(ValueError, match="Contact 999 not found"):
        await service.update_contact(1, 999, ContactUpdate(value="x@y.com"))


async def test_delete_contact(service: ContactService) -> None:
    created = await service.create_contact(
        1, ContactCreate(type=ContactType.email, value="a@b.com")
    )
    await service.delete_contact(1, created.id)
    with pytest.raises(ValueError, match=f"Contact {created.id} not found"):
        await service.get_contact(1, created.id)


async def test_delete_contact_not_found_raises(service: ContactService) -> None:
    with pytest.raises(ValueError, match="Contact 999 not found"):
        await service.delete_contact(1, 999)


async def test_create_contact_profile_not_found_raises(service: ContactService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.create_contact(99, ContactCreate(type=ContactType.email, value="a@b.com"))


async def test_list_contacts_profile_not_found_raises(service: ContactService) -> None:
    with pytest.raises(ValueError, match="Profile 99 not found"):
        await service.list_contacts(99)


async def test_tiger_style_create_profile_id_zero_raises(service: ContactService) -> None:
    with pytest.raises(AssertionError):
        await service.create_contact(0, ContactCreate(type=ContactType.email, value="a@b.com"))


async def test_tiger_style_get_contact_id_zero_raises(service: ContactService) -> None:
    with pytest.raises(AssertionError):
        await service.get_contact(1, 0)


async def test_tiger_style_delete_contact_id_zero_raises(service: ContactService) -> None:
    with pytest.raises(AssertionError):
        await service.delete_contact(1, 0)
