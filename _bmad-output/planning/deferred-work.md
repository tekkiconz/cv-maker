# Deferred Work

## Deferred from: code review of 1-2-create-and-list-profiles (2026-04-21)

- **De1: Global engine instantiated at import time** [`app/apis/dependencies.py:11-12`] — `_engine = create_async_engine(settings.database_url, ...)` executes at module import; if env not set, import fails. Known design tradeoff; tests bypass via dependency overrides.
- **De2: `MAX_PROFILES` limit not enforced** [`app/services/profile_service.py`, `app/adapters/sqlite_database.py`] — `MAX_PROFILES = 1000` constant defined in `limits.py` but never checked before insert or in list; unbounded profile creation possible. No story has specified enforcement yet.
- **De3: `OperationalError` propagates as unstructured 500** [`app/adapters/sqlite_database.py:20-27`] — Raw SQLAlchemy `OperationalError` (e.g. DB locked) propagates to client with no structured error response. Cross-cutting error handling concern; needs a global exception handler story.

## Deferred from: code review of 1-2-create-and-list-profiles (2026-04-23)

- **De1: Dead `DatabaseProtocol` generic methods** [`app/adapters/sqlite_database.py:14-29`, `app/interfaces/database.py:11-19`] — `connect`, `disconnect`, `execute`, `fetch_one`, `fetch_all` implemented in adapter but never called by any service. `ProfileService` uses `ProfileRepositoryProtocol` only. Remove or use in a future story that needs raw query access.
