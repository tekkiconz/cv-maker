from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LatexCompilerProtocol(Protocol):
    async def compile(self, template_path: str, context: dict[str, Any]) -> bytes: ...
