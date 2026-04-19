import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.sqlite_database import SQLiteDatabaseAdapter
from app.models.base import Base
from app.schemas.profile import ProfileCreate


@pytest.fixture
async def session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        yield s
    await engine.dispose()


async def test_create_profile_returns_id(session: AsyncSession) -> None:
    adapter = SQLiteDatabaseAdapter(session)
    result = await adapter.create_profile(ProfileCreate(name="Alice", description="Engineer"))
    assert result.id is not None
    assert result.name == "Alice"


async def test_list_profiles_empty(session: AsyncSession) -> None:
    adapter = SQLiteDatabaseAdapter(session)
    results = await adapter.list_profiles()
    assert results == []


async def test_list_profiles_returns_all(session: AsyncSession) -> None:
    adapter = SQLiteDatabaseAdapter(session)
    await adapter.create_profile(ProfileCreate(name="Alice"))
    await adapter.create_profile(ProfileCreate(name="Bob"))
    results = await adapter.list_profiles()
    assert len(results) == 2
