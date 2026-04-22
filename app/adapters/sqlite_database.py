from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileRead


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
        return [ProfileRead.model_validate(p) for p in profiles]
