import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


async def test_health_returns_200() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200


async def test_health_body_status_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json()["status"] == "ok"


async def test_health_db_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json()["db"] == "ok"


async def test_health_latex_ok() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.json()["latex"] == "ok"


async def test_health_latex_timeout_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio
    from unittest.mock import MagicMock

    async def fake_wait_for(coro: object, timeout: float) -> None:
        import inspect

        if inspect.iscoroutine(coro):
            coro.close()
        raise TimeoutError

    mock_proc = MagicMock()
    mock_proc.kill = MagicMock()

    async def fake_communicate() -> tuple[bytes, bytes]:
        return b"", b""

    mock_proc.communicate = fake_communicate

    async def fake_create_subprocess(*args: object, **kwargs: object) -> MagicMock:
        return mock_proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess)
    monkeypatch.setattr(asyncio, "wait_for", fake_wait_for)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 503
    assert response.json()["latex"] == "timeout"


async def test_health_latex_unavailable_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio
    from unittest.mock import MagicMock

    mock_proc = MagicMock()
    mock_proc.returncode = 1

    async def fake_communicate() -> tuple[bytes, bytes]:
        return b"", b"not found"

    mock_proc.communicate = fake_communicate

    async def fake_create_subprocess(*args: object, **kwargs: object) -> MagicMock:
        return mock_proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_create_subprocess)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 503
