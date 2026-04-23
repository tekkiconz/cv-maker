# CVMaker

> Slop app. Generates CVs as PDFs via LaTeX.

FastAPI + HTMX + SQLite + pdflatex. Docker Compose runtime.

## Stack

- **FastAPI** — REST + HTMX endpoints
- **SQLAlchemy** — async SQLite via aiosqlite
- **Alembic** — migrations
- **Jinja2** — HTML partials + LaTeX templates
- **pdflatex** — PDF compilation

## Quick start

```bash
docker compose up --build
```

App runs at `http://localhost:8000`.

## Dev

```bash
# Bootstrap venv
make install

# Tests (local, no Docker)
make test-local

# Tests (Docker)
make test

# Lint / format
make lint-local
make fmt-local

# Type check
make typecheck-local

# Generate + apply migration after model changes
docker compose run --rm app alembic revision --autogenerate -m "description"
docker compose run --rm app alembic upgrade head
```

## Architecture

```
apis/ → controllers/ → services/ → adapters/ → DB / filesystem / pdflatex
```

- `app/interfaces/` — protocols (no ABC)
- `app/adapters/` — concrete implementations
- `app/adapters/factories.py` — wiring
- `app/apis/dependencies.py` — FastAPI `Depends()` injection
- `app/configs/settings.py` — sole reader of env vars
- `app/utils/sanitizer.py` — all user text sanitized before LaTeX

## License

MIT
