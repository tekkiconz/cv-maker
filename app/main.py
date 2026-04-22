import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.adapters.factories import engine
from app.apis.profiles import router as profiles_router
from app.apis.sections import sections_router

app = FastAPI(title="CVMaker")

app.include_router(sections_router)
app.include_router(profiles_router)

_PDFLATEX_TIMEOUT_SECONDS = 5.0


@app.get("/health")
async def health(request: Request) -> JSONResponse:
    assert request.method == "GET", "health endpoint only accepts GET requests"

    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    proc = await asyncio.create_subprocess_exec(
        "pdflatex",
        "--version",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        await asyncio.wait_for(proc.communicate(), timeout=_PDFLATEX_TIMEOUT_SECONDS)
    except TimeoutError:
        return JSONResponse(
            content={"status": "error", "latex": "timeout"},
            status_code=503,
        )

    if proc.returncode != 0:
        return JSONResponse(
            content={"status": "error", "latex": "unavailable"},
            status_code=503,
        )

    result: dict[str, str] = {"status": "ok", "db": "ok", "latex": "ok"}
    assert result["status"] == "ok"
    return JSONResponse(content=result, status_code=200)
