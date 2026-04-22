from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.adapters.sqlite_database import SQLiteDatabaseAdapter
from app.configs.settings import settings

engine = create_async_engine(settings.database_url, echo=False)
session_factory = async_sessionmaker(engine, expire_on_commit=False)


def make_sqlite_adapter(session: AsyncSession) -> SQLiteDatabaseAdapter:
    return SQLiteDatabaseAdapter(session)
