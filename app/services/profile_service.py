from app.interfaces.database import ProfileRepositoryProtocol
from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate


class ProfileService:
    def __init__(self, db: ProfileRepositoryProtocol) -> None:
        self._db = db

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        assert data.name.strip(), "profile name must not be empty"
        result = await self._db.create_profile(data)
        assert result.id is not None, "inserted profile has no id"
        return result

    async def list_profiles(self) -> list[ProfileRead]:
        results = await self._db.list_profiles()
        assert isinstance(results, list), "list_profiles must return a list"
        return results

    async def get_profile(self, profile_id: int) -> ProfileRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._db.get_profile(profile_id)
        if result is None:
            raise ValueError(f"Profile {profile_id} not found")
        assert result.id == profile_id, "returned profile id must match requested id"
        return result

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead:
        assert profile_id > 0, "profile_id must be a positive integer"
        result = await self._db.update_profile(profile_id, data)
        if result is None:
            raise ValueError(f"Profile {profile_id} not found")
        assert result.updated_at >= result.created_at, "updated_at must not precede created_at"
        return result
