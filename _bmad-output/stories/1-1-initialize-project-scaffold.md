# Story 1.1: Initialize Project Scaffold & Docker Compose

Status: in-progress

## Story

As a developer,
I want a running Docker Compose environment with a healthy FastAPI app, working SQLite connection, verified LaTeX compilation, and all four abstraction layer interfaces defined,
so that every subsequent story can be implemented against a stable, testable foundation.

## Acceptance Criteria

1. `docker compose up` starts without errors and `/health` returns `{"status": "ok"}` with HTTP 200.
2. The health endpoint performs a real SQLite query (e.g. `SELECT 1`) and includes `{"db": "ok"}` in the response — no mock.
3. The health endpoint invokes `pdflatex --version` inside the container and includes `{"latex": "ok"}` in the response — proving TeX Live is available.
4. The four interface files exist and are importable with no errors:
   - `app/interfaces/database.py` — `DatabaseProtocol` (Python Protocol)
   - `app/interfaces/storage.py` — `StorageProtocol` (Python Protocol)
   - `app/interfaces/latex_compiler.py` — `LatexCompilerProtocol` (Python Protocol)
   - `app/interfaces/template_discovery.py` — `TemplateDiscoveryProtocol` (Python Protocol)
5. `app/models/base.py` exists and is the sole source of `Base = declarative_base()`.
6. `app/middleware/auth.py` exists as an empty stub (no logic, no imports beyond what's needed to mount it).
7. `app/constants/limits.py` exists with at least one placeholder constant (e.g. `MAX_PROFILES = 1000`).
8. `app/constants/enums.py` exists with `ContactType` enum (`email`, `phone`, `github`, `linkedin`, `website`, `twitter`).
9. `app/configs/settings.py` exists and uses Pydantic Settings to read `DATABASE_URL`, `STORAGE_PATH`, `OUTPUT_PATH`, `TEMPLATES_PATH` from environment.
10. `pyproject.toml` is present with dependencies, pytest configured, and ruff configured.
11. `.env.example` documents all required environment variables.
12. `apis/dependencies.py` exists (may be mostly empty stubs at this stage).
13. Tiger Style: health endpoint contains at minimum one input assertion (method is GET) and one output assertion (response status is 200 before returning).

## Tasks / Subtasks

- [ ] Task 1: Create pyproject.toml, Dockerfile, docker-compose.yml, .env.example (AC: 1, 10, 11)
  - [ ] 1.1 Write pyproject.toml with FastAPI, SQLAlchemy, Alembic, Pydantic-Settings, pytest, ruff, mypy deps
  - [ ] 1.2 Write Dockerfile (Python 3.12 slim + TeX Live texlive-latex-base)
  - [ ] 1.3 Write docker-compose.yml with app service + volume mounts for assets/
  - [ ] 1.4 Write .env.example documenting DATABASE_URL, STORAGE_PATH, OUTPUT_PATH, TEMPLATES_PATH
- [ ] Task 2: Create app package structure and config/constants (AC: 7, 8, 9)
  - [ ] 2.1 Create app/configs/settings.py with Pydantic Settings reading all 4 env vars
  - [ ] 2.2 Create app/constants/limits.py with MAX_PROFILES and other loop-bound constants
  - [ ] 2.3 Create app/constants/enums.py with ContactType enum
- [ ] Task 3: Create all 4 interface files (AC: 4)
  - [ ] 3.1 Create app/interfaces/database.py — DatabaseProtocol
  - [ ] 3.2 Create app/interfaces/storage.py — StorageProtocol
  - [ ] 3.3 Create app/interfaces/latex_compiler.py — LatexCompilerProtocol
  - [ ] 3.4 Create app/interfaces/template_discovery.py — TemplateDiscoveryProtocol
- [ ] Task 4: Create models/base.py, middleware stub, and apis/dependencies.py stub (AC: 5, 6, 12)
  - [ ] 4.1 Create app/models/base.py as sole source of SQLAlchemy Base
  - [ ] 4.2 Create app/middleware/auth.py as empty stub
  - [ ] 4.3 Create app/apis/dependencies.py stub
- [ ] Task 5: Create app/main.py with FastAPI app and /health endpoint (AC: 1, 2, 3, 13)
  - [ ] 5.1 Create app/main.py with FastAPI app instance and lifespan
  - [ ] 5.2 Implement /health endpoint with DB check (SELECT 1 via SQLite) and LaTeX check (pdflatex --version)
  - [ ] 5.3 Add Tiger Style assertions: assert request.method == "GET" on input, assert response is 200 on output
- [ ] Task 6: Write tests for health endpoint (AC: 1, 2, 3, 13)
  - [ ] 6.1 Create tests/api/test_health.py with tests for /health returning 200, db ok, latex ok

## Dev Notes

- Architecture: Python 3.12 + FastAPI + SQLAlchemy 2.x async + Alembic + HTMX + Jinja2 + pdflatex in Docker
- Interfaces use `typing.Protocol` (structural typing), NOT ABC — no explicit inheritance needed
- No business logic in this story — scaffold only. Adapters may be stubbed (raise NotImplementedError)
- Tiger Style: assertions at every boundary. Health endpoint uses `assert` (programmer invariants), not try/except
- `app/configs/settings.py` is the ONLY place that reads env vars — all other modules import Settings
- `app/models/base.py` is the ONLY source of `Base = declarative_base()` — never call declarative_base() elsewhere
- `HX-Request` header checks belong in controllers/ only — not needed in this story
- Test framework: pytest + httpx async test client, unit tests co-located as `*.test.py`
- Pytest configured in pyproject.toml: `python_files = ["*.test.py", "test_*.py"]`
- TeX Live: use `texlive-latex-base` in Dockerfile for pdflatex availability

### Project Structure Notes

- Root of project is `/Users/tekkiconz/Code/CVMaker` — all files created relative to here
- Structure follows architecture.md exactly: app/, tests/, assets/, migrations/, pyproject.toml, Dockerfile, docker-compose.yml
- `app/apis/sections/__init__.py` auto-registers section routers (stub for now)

### References

- [Source: _bmad-output/planning/architecture.md#Project Structure]
- [Source: _bmad-output/planning/architecture.md#Implementation Patterns]
- [Source: _bmad-output/planning/epics.md#Story 1.1]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

### Change Log
