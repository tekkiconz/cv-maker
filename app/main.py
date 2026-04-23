import asyncio

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.factories import engine
from app.apis.profiles import router as profiles_router
from app.apis.sections import sections_router
from app.constants.limits import PDFLATEX_HEALTH_CHECK_TIMEOUT_SECONDS

app = FastAPI(title="CVMaker")

app.include_router(sections_router)
app.include_router(profiles_router)


@app.get("/health")
async def health() -> JSONResponse:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except SQLAlchemyError:
        return JSONResponse(
            content={"status": "error", "db": "unavailable"},
            status_code=503,
        )

    try:
        proc = await asyncio.create_subprocess_exec(
            "pdflatex",
            "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError:
        return JSONResponse(
            content={"status": "error", "latex": "not_found"},
            status_code=503,
        )
    try:
        await asyncio.wait_for(proc.communicate(), timeout=PDFLATEX_HEALTH_CHECK_TIMEOUT_SECONDS)
    except TimeoutError:
        proc.kill()
        await proc.communicate()  # drain to prevent zombie
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
