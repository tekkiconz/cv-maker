from app.interfaces.database import ProfileRepositoryProtocol
from app.schemas.profile import ProfileCreate, ProfileRead


class ProfileService:
    def __init__(self, db: ProfileRepositoryProtocol) -> None:
        self._db = db

    async def create_profile(self, data: ProfileCreate) -> ProfileRead:
        assert data.name, "profile name must not be empty"
        result = await self._db.create_profile(data)
        assert result.id is not None, "inserted profile has no id"
        return result

    async def list_profiles(self) -> list[ProfileRead]:
        results = await self._db.list_profiles()
        assert isinstance(results, list), "list_profiles must return a list"
        return results
