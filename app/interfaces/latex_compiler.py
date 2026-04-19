from typing import Any, Protocol


class LatexCompilerProtocol(Protocol):
    async def compile(self, template_path: str, context: dict[str, Any]) -> bytes: ...
