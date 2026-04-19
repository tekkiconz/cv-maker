from typing import Protocol, runtime_checkable


@runtime_checkable
class TemplateDiscoveryProtocol(Protocol):
    async def discover(self) -> list[str]: ...

    async def get_template(self, name: str) -> str: ...
