from sqlalchemy.ext.asyncio import AsyncEngine

from app.adapters.factories import engine, session_factory, make_sqlite_adapter
from app.adapters.sqlite_database import SQLiteDatabaseAdapter
import inspect


def test_make_sqlite_adapter_returns_correct_type() -> None:
    sig = inspect.signature(make_sqlite_adapter)
    assert sig.return_annotation is SQLiteDatabaseAdapter


def test_engine_is_async_engine() -> None:
    assert isinstance(engine, AsyncEngine)
