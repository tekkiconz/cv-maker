from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.schemas.profile import ProfileCreate, ProfileRead, ProfileUpdate


@runtime_checkable
class DatabaseProtocol(Protocol):
    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...

    async def execute(self, statement: Any) -> Any: ...

    async def fetch_one(self, statement: Any) -> Any | None: ...

    async def fetch_all(self, statement: Any) -> list[Any]: ...


@runtime_checkable
class ProfileRepositoryProtocol(Protocol):
    async def create_profile(self, data: ProfileCreate) -> ProfileRead: ...

    async def list_profiles(self) -> list[ProfileRead]: ...

    async def get_profile(self, profile_id: int) -> ProfileRead | None: ...

    async def update_profile(self, profile_id: int, data: ProfileUpdate) -> ProfileRead | None: ...
