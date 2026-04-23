from datetime import UTC, datetime

import pytest

from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate
from app.services.profile_service import ProfileService


class FakeProfileRepository:
    def __init__(self) -> None:
        self._profiles: list[ProfileRead] = []
        self._next_id: int = 1

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        now = datetime.now(tz=UTC)
        profile = ProfileRead(
            id=self._next_id,
            name=data.name,
            description=data.description,
            created_at=now,
            updated_at=now,
        )
        self._profiles.append(profile)
        self._next_id += 1
        return profile

    async def list_profiles(self) -> list[ProfileRead]:
        return list(self._profiles)

    async def get_profile(self, profile_id: int) -> ProfileRead | None:
        return next((p for p in self._profiles if p.id == profile_id), None)

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None:
        for i, profile in enumerate(self._profiles):
            if profile.id == profile_id:
                updates = data.model_dump(exclude_unset=True)
                now = datetime.now(tz=UTC)
                updated = profile.model_copy(update={**updates, "updated_at": now})
                self._profiles[i] = updated
                return updated
        return None


@pytest.fixture
def fake_db() -> FakeProfileRepository:
    return FakeProfileRepository()


@pytest.fixture
def service(fake_db: FakeProfileRepository) -> ProfileService:
    return ProfileService(fake_db)


async def test_create_profile_returns_profile_with_id(service: ProfileService) -> None:
    data = ProfileCreate(name="Alice", description="Engineer")
    result = await service.create_profile(data)
    assert result.id is not None
    assert result.name == "Alice"
    assert result.description == "Engineer"


async def test_create_profile_description_optional(service: ProfileService) -> None:
    data = ProfileCreate(name="Bob", description=None)
    result = await service.create_profile(data)
    assert result.id is not None
    assert result.description is None


async def test_list_profiles_empty(service: ProfileService) -> None:
    results = await service.list_profiles()
    assert results == []


async def test_create_profile_empty_name_raises(service: ProfileService) -> None:
    data = ProfileCreate.model_construct(
        name=""
    )  # bypass Pydantic validation to hit service assertion
    with pytest.raises(AssertionError, match="profile name must not be empty"):
        await service.create_profile(data)


async def test_list_profiles_returns_all_created(service: ProfileService) -> None:
    await service.create_profile(ProfileCreate(name="Alice", description=None))
    await service.create_profile(ProfileCreate(name="Bob", description=None))
    results = await service.list_profiles()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"Alice", "Bob"}


async def test_get_profile_found(service: ProfileService) -> None:
    created = await service.create_profile(ProfileCreate(name="Alice", description="Eng"))
    result = await service.get_profile(created.id)
    assert result.id == created.id
    assert result.name == "Alice"


async def test_get_profile_not_found_raises(service: ProfileService) -> None:
    with pytest.raises(ValueError, match="Profile 999 not found"):
        await service.get_profile(999)


async def test_update_profile_name_only(service: ProfileService) -> None:
    created = await service.create_profile(ProfileCreate(name="Alice", description="Eng"))
    result = await service.update_profile(created.id, ProfileUpdate(name="Alicia"))
    assert result.name == "Alicia"
    assert result.description == "Eng"


async def test_update_profile_description_only(service: ProfileService) -> None:
    created = await service.create_profile(ProfileCreate(name="Alice", description="Eng"))
    result = await service.update_profile(created.id, ProfileUpdate(description="Dev"))
    assert result.name == "Alice"
    assert result.description == "Dev"


async def test_update_profile_both_fields(service: ProfileService) -> None:
    created = await service.create_profile(ProfileCreate(name="Alice", description="Eng"))
    result = await service.update_profile(created.id, ProfileUpdate(name="Bob", description="Dev"))
    assert result.name == "Bob"
    assert result.description == "Dev"


async def test_update_profile_not_found_raises(service: ProfileService) -> None:
    with pytest.raises(ValueError, match="Profile 999 not found"):
        await service.update_profile(999, ProfileUpdate(name="Ghost"))


async def test_update_profile_zero_id_raises_assertion(service: ProfileService) -> None:
    with pytest.raises(AssertionError):
        await service.update_profile(0, ProfileUpdate(name="Bad"))


async def test_get_profile_zero_id_raises_assertion(service: ProfileService) -> None:
    with pytest.raises(AssertionError):
        await service.get_profile(0)
