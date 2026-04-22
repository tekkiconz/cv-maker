from unittest.mock import MagicMock

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.adapters.factories import engine, make_sqlite_adapter
from app.adapters.sqlite_database import SQLiteDatabaseAdapter


def test_make_sqlite_adapter_returns_correct_type() -> None:
    mock_session = MagicMock(spec=AsyncSession)
    adapter = make_sqlite_adapter(mock_session)
    assert isinstance(adapter, SQLiteDatabaseAdapter)


def test_engine_is_async_engine() -> None:
    assert isinstance(engine, AsyncEngine)
