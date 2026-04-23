# CVMaker Project Overview

## Purpose
CV/resume builder web app. Users create profiles and generate PDF CVs from LaTeX templates.

## Tech Stack
- Python 3.14, FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, Jinja2, HTMX
- SQLite via aiosqlite
- Docker Compose as the only runtime
- Ruff (lint+format), mypy (strict), pytest

## Architecture (4-layer)
`apis/` → `controllers/` → `services/` → `adapters/` → DB / filesystem / subprocess

- Interfaces: `app/interfaces/` (typing.Protocol, not ABC)
- DI wiring: `app/apis/dependencies.py` (FastAPI Depends)
- Adapters: `app/adapters/`
- DB Base: `app/models/base.py` (never call declarative_base() elsewhere)
- Config: `app/configs/settings.py` (only place reading env vars)
- LaTeX sanitizer: `app/utils/sanitizer.py` (enforced at pdflatex_compiler boundary)
- Loop limits: `app/constants/limits.py` (no inline magic numbers)
- Enums: `app/constants/enums.py`

## HTMX Dual Response
Controllers check `HX-Request` header → return HTML partial or JSON.
Header check lives ONLY in `controllers/`, never in `apis/` or `services/`.

## Section Router Auto-discovery
`apis/sections/__init__.py` auto-registers all section routers. `main.py` includes only single `sections_router`.

## Test Locations
- Unit tests: co-located as `*.test.py` (e.g. `services/profile_service.test.py`)
- Integration/API tests: `tests/`
