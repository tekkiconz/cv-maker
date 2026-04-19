import asyncio

import aiosqlite
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.apis.sections import sections_router
from app.configs.settings import settings

app = FastAPI(title="CVMaker")

app.include_router(sections_router)


@app.get("/health")
async def health(request: Request) -> JSONResponse:
    assert request.method == "GET", "health endpoint only accepts GET requests"

    db_path = settings.database_url.removeprefix("sqlite+aiosqlite:///")
    async with aiosqlite.connect(db_path) as db:
        cursor = await db.execute("SELECT 1")
        await cursor.fetchone()

    proc = await asyncio.create_subprocess_exec(
        "pdflatex",
        "--version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    await proc.communicate()
    assert proc.returncode == 0, "pdflatex is not available in this environment"

    result: dict[str, str] = {"status": "ok", "db": "ok", "latex": "ok"}
    assert result["status"] == "ok"
    return JSONResponse(content=result, status_code=200)
