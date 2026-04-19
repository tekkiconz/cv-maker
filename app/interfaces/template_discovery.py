from typing import Protocol


class TemplateDiscoveryProtocol(Protocol):
    async def discover(self) -> list[str]: ...

    async def get_template(self, name: str) -> str: ...
