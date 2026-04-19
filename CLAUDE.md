# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start the app (Docker Compose is the only runtime)
docker compose up --build

# Run all tests
docker compose run --rm app pytest

# Run a single test file
docker compose run --rm app pytest app/services/profile_service.test.py

# Lint + format
docker compose run --rm app ruff check . && ruff format .

# Type check
docker compose run --rm app mypy app/

# Generate a migration after model changes
docker compose run --rm app alembic revision --autogenerate -m "description"

# Apply migrations
docker compose run --rm app alembic upgrade head
```

## Architecture

**Request flow:** `apis/` → `controllers/` → `services/` → `adapters/` → DB / filesystem / subprocess

**4-layer abstraction** — each layer has an interface in `interfaces/` (using `typing.Protocol`, not ABC), a concrete adapter in `adapters/`, wired together via factory functions in `adapters/factories.py`, and injected into services via FastAPI `Depends()` in `apis/dependencies.py`.

**HTMX dual response** — controllers check the `HX-Request` header and return either a Jinja2 HTML partial or JSON. This header check lives **exclusively** in `controllers/` — never in `apis/` or `services/`. HTML views (Jinja2 templates) live in `app/views/`; LaTeX templates live in `assets/templates/`.

**Sanitization invariant** — all user text passes through `utils/sanitizer.py` before reaching any LaTeX template. This is enforced at the `adapters/pdflatex_compiler.py` boundary. `LatexCompilerProtocol` accepts only pre-sanitized input.

**Config boundary** — `configs/settings.py` is the **only** place that reads environment variables. All other modules import `Settings` from there.

**SQLAlchemy Base** — defined once in `models/base.py`. Never call `declarative_base()` anywhere else.

**Section router auto-discovery** — `apis/sections/__init__.py` auto-registers all section routers. `main.py` includes only the single `sections_router`.

**Test locations** — unit tests are co-located with source files as `*.test.py` (e.g. `services/profile_service.test.py`). Integration and API tests live in `tests/`.

## Tiger Style

Assertions enforce programmer invariants; exceptions handle expected failures. Every function should have at minimum one input precondition assertion and one output postcondition assertion. Assertions remain enabled in production — a crash on bad state beats silent corruption.

All loop bounds must reference a named constant from `constants/limits.py` — never inline magic numbers.

## Enforcement Rules

- Never read `os.environ` directly — always import from `configs/`
- Never put business logic in `apis/` or `views/`
- Never put HTTP/response logic in `services/`
- Never call the LaTeX adapter without sanitizing input first
- Never create `BaseService` or `BaseAdapter` — standalone classes only
- Never swallow exceptions — log and re-raise or convert to a structured error
- `HX-Request` check lives only in `controllers/`

## Key Files

| Concern | File |
|---|---|
| Interfaces | `app/interfaces/{database,storage,latex_compiler,template_discovery}.py` |
| DI wiring | `app/apis/dependencies.py` |
| Env config | `app/configs/settings.py` |
| LaTeX sanitizer | `app/utils/sanitizer.py` |
| Loop limits | `app/constants/limits.py` |
| Enums | `app/constants/enums.py` |
| DB Base | `app/models/base.py` |
| Auth stub | `app/middleware/auth.py` |
| Architecture | `_bmad-output/planning/architecture.md` |
| Data model | `_bmad-output/planning/architecture.md` § Data Architecture |
