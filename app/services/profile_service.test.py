from datetime import datetime, timezone

import pytest

from app.schemas.profile import ProfileCreate, ProfileRead
from app.services.profile_service import ProfileService


class FakeProfileRepository:
    def __init__(self) -> None:
        self._profiles: list[ProfileRead] = []
        self._next_id: int = 1

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        now = datetime.now(tz=timezone.utc)
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


@pytest.fixture
def fake_db() -> FakeProfileRepository:
    return FakeProfileRepository()


@pytest.fixture
def service(fake_db: FakeProfileRepository) -> ProfileService:
    return ProfileService(fake_db)  # type: ignore[arg-type]  # TYPE_CHECKING guard on ProfileRepositoryProtocol prevents mypy from resolving structural match


async def test_create_profile_returns_profile_with_id(service: ProfileService) -> None:
    data = ProfileCreate(name="Alice", description="Engineer")
    result = await service.create_profile(data)
    assert result.id is not None
    assert result.name == "Alice"
    assert result.description == "Engineer"


async def test_create_profile_description_optional(service: ProfileService) -> None:
    data = ProfileCreate(name="Bob")
    result = await service.create_profile(data)
    assert result.id is not None
    assert result.description is None


async def test_list_profiles_empty(service: ProfileService) -> None:
    results = await service.list_profiles()
    assert results == []


async def test_create_profile_empty_name_raises(service: ProfileService) -> None:
    data = ProfileCreate.model_construct(name="")  # bypass Pydantic validation to hit service assertion
    with pytest.raises(AssertionError, match="profile name must not be empty"):
        await service.create_profile(data)


async def test_list_profiles_returns_all_created(service: ProfileService) -> None:
    await service.create_profile(ProfileCreate(name="Alice"))
    await service.create_profile(ProfileCreate(name="Bob"))
    results = await service.list_profiles()
    assert len(results) == 2
    names = {r.name for r in results}
    assert names == {"Alice", "Bob"}
