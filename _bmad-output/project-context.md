---
project_name: 'CVMaker'
user_name: 'Huy'
date: '2026-04-18'
sections_completed: ['technology_stack', 'language_rules', 'framework_rules', 'testing_rules', 'quality_rules', 'tiger_style_critical_rules']
status: 'complete'
optimized_for_llm: true
---

# Project Context for AI Agents

_This file contains critical rules and patterns that AI agents must follow when implementing code in this project. Focus on unobvious details that agents might otherwise miss._

---

## Technology Stack & Versions

- **Python** 3.14+
- **FastAPI** (latest stable) — async, OpenAPI auto-generated
- **SQLAlchemy** 2.x (async engine, `AsyncSession`)
- **Alembic** — schema-first migrations
- **Jinja2** — server-rendered HTML templates (not LaTeX templates)
- **HTMX** — no JS bundler, no SPA, no client-side state
- **SQLite** — default DB adapter (via aiosqlite)
- **pdflatex** / TeX Live — LaTeX compiler, runs inside Docker container
- **pytest** + **httpx** (async test client)
- **ruff** — linting + formatting
- **mypy** — static type checking
- **uv** or pip — dependency management
- **Docker Compose** — only supported runtime; no direct process execution

## Critical Implementation Rules

### Language-Specific Rules

- All functions must be `async def` in services, adapters, and routers — no sync blocking calls
- Never read `os.environ` directly — always import config values from `app/configs/settings.py` (Pydantic Settings)
- Use `typing.Protocol` for all abstraction layer interfaces — never `ABC`, never explicit inheritance on adapters
- Type hints are mandatory on all function signatures (mypy enforced)
- Dates are always ISO 8601 strings (`"2024-01"`, `"2024-01-15"`) — never Python `datetime` objects in API schemas
- Booleans in JSON are `true/false` — never `1/0`
- All imports are absolute (`from app.services.profile_service import ProfileService`) — no relative imports
- `Base = declarative_base()` exists only in `app/models/base.py` — all models import `Base` from there, never redefine it
- No `__all__` required — module boundaries are enforced by architecture, not export lists

### Framework-Specific Rules

**FastAPI / API Layer**
- Routers (`apis/`) handle routing and request parsing only — zero business logic
- All dependency wiring lives in `apis/dependencies.py` exclusively — routers declare `Depends()`, never instantiate services or adapters directly
- `HX-Request` header detection lives exclusively in `controllers/` — never in `apis/` or `services/`
- Controllers call services, then decide response format: `HX-Request` present → return Jinja2 HTML partial; absent → return JSON
- HTTP status codes: `200` success, `201` created, `204` no content, `404` not found, `422` validation error (FastAPI default), `500` compilation failure — never `200` with an error body
- Error response shape is always `{"error": "error_code", "message": "Human summary", "detail": "..."}` — no other error format
- OpenAPI spec is auto-generated — endpoint design IS the API contract; do not write manual OpenAPI YAML

**SQLAlchemy / Alembic**
- Use `AsyncSession` everywhere — no sync `Session`
- Each section type (experience, education, projects, skills, certifications, languages, publications, free_text) has its own `*_sections` table and (where applicable) `*_entries` table — no polymorphic tables, no type columns, no JSON fallback
- Each new table gets its own Alembic migration version — never bundle multiple unrelated tables into one migration
- `alembic.ini` lives at the project root — not inside `migrations/`

**HTMX / Jinja2**
- Jinja2 templates live in `app/views/` — NOT `app/templates/` (that name collides with LaTeX templates)
- LaTeX `.tex` files live in `assets/templates/` — entirely separate from Jinja2
- Templates are thin — no business logic, only rendering. All data comes from the controller
- HTMX compilation progress uses polling every 500ms against `/compile/status/{job_id}` — no SSE, no WebSocket
- Preview PDF is delivered as `<embed src="/preview/{job_id}">` — browser renders PDF natively

**Section auto-registration**
- `app/apis/sections/__init__.py` auto-registers all section routers — never register section routers individually in `main.py`

### Testing Rules

**Test organization**
- Unit tests are co-located next to the file they test using `*.test.py` naming: `profile_service.py` → `profile_service.test.py`
- pytest discovers `*.test.py` files via `pyproject.toml`: `python_files = ["*.test.py"]`
- Integration tests (cross-module, adapter, DB) go in `tests/integration/`
- API endpoint tests (httpx async client) go in `tests/api/`
- Shared fixtures live in `tests/conftest.py`

**Unit test rules**
- Services are tested against a test-double (in-memory fake or mock) implementation of the Protocol interface — never against the real SQLite adapter
- Test-doubles implement the same Protocol structurally — they do not inherit from the real adapter
- No `@patch` on internal service state — test via the Protocol boundary only

**Integration test rules**
- Integration tests that touch DB use a real SQLite in-memory database (`sqlite+aiosqlite:///:memory:`) — no mocking the DB adapter in integration tests
- Each integration test gets a fresh DB session via the `conftest.py` fixture — no shared state between tests
- LaTeX compilation integration tests require the Docker container to be running (TeX Live must be available)

**General**
- Test file for every service method — no untested public methods
- Tests assert both the happy path and at least one failure/error path per method
- Never test implementation details — test the contract (inputs → outputs via the Protocol)

### Code Quality & Style Rules

**Naming conventions**
| Context | Convention | Example |
|---|---|---|
| DB tables | `plural_snake_case` | `experience_sections`, `profile_contacts` |
| DB columns | `snake_case` | `profile_id`, `order_index`, `is_enabled` |
| Foreign keys | `{table_singular}_id` | `section_id`, `profile_id` |
| API endpoints | `plural_snake_case` | `/profiles`, `/profiles/{id}/sections/experience` |
| Python functions | `snake_case` | `get_profile()`, `create_experience_section()` |
| Python classes | `PascalCase` | `ProfileService`, `ExperienceSectionSchema` |
| Python files | `snake_case` | `profile_service.py`, `experience_section.py` |
| Jinja2 templates | `snake_case` | `profile_list.html`, `experience_section.html` |
| JSON fields | `snake_case` | `{"profile_id": 1, "is_enabled": true}` |

**Linting & formatting**
- ruff handles both linting and formatting — run `ruff check` and `ruff format` before committing
- mypy runs on the full `app/` directory — no `# type: ignore` without a comment explaining why
- No inline `pylint: disable` or `noqa` without explanation

**Comments**
- Default: no comments. Only add one when the WHY is non-obvious (a hidden constraint, a workaround, an invariant that would surprise a reader)
- Never explain WHAT the code does — well-named identifiers do that
- No docstrings on internal functions; one-line docstrings only on public service methods if the purpose isn't obvious from the name

**Response shapes**
- Success: direct object, no wrapper — `{"id": 1, "name": "..."}`
- List: direct array — `[{"id": 1}, ...]`
- Error: always `{"error": "snake_case_code", "message": "Human summary", "detail": "..."}`
- Never wrap success responses in `{"data": {...}}` or `{"result": {...}}`

### Tiger Style & Critical Don't-Miss Rules

**Assertions (Tiger Style)**
- Minimum 2 assertions per function: one input precondition, one output postcondition
- Assertions stay enabled in production — never disable with `-O` or `PYTHONOPTIMIZE`
- Assert one condition per `assert` — never `assert a and b`
- Assert both what SHOULD be true AND what should NOT be true (negative space)
- Assertions catch programmer bugs — they are NOT error handling for expected failures
- A crash on bad state (`AssertionError`) is always better than silent data corruption

```python
async def create_profile(self, data: CreateProfileSchema) -> Profile:
    assert data.name, "profile name must not be empty"           # precondition
    result = await self._db.create_profile(data)
    assert result.id is not None, "inserted profile has no id"  # postcondition
    return result
```

**Loop safety**
- Every loop requires a `MAX_*` constant from `app/constants/limits.py` — never hardcode bounds inline
- Exceeding the bound is an `assert` failure, not a `raise`

```python
for i, path in enumerate(template_dir.iterdir()):
    assert i < MAX_TEMPLATE_DISCOVERY_ITERATIONS, "template discovery exceeded max"
```

**Hard architectural invariants — never violate**
- Never call the LaTeX compiler adapter without passing user text through `sanitizer.sanitize_for_latex()` first
- Never read `os.environ` directly — always import from `app/configs/settings.py`
- Never put business logic in `apis/` routers or `app/views/` templates
- Never put HTTP/response formatting in `services/`
- Never put `HX-Request` header checks outside `controllers/`
- Never create `BaseService` or `BaseAdapter` — all classes are standalone
- Never swallow exceptions — log and re-raise, or convert to a structured error response
- Never register section routers in `main.py` — use `apis/sections/__init__.py` auto-registration
- `app/models/base.py` is the only place `Base = declarative_base()` is defined

**LaTeX sanitization**
- `sanitize_for_latex()` escapes: `& % $ # _ { } ~ ^ \`
- `\write18` and `\immediate\write18` in user input → raise `ValueError`, never silently strip
- The sanitizer lives in `app/utils/sanitizer.py` and is called only inside the compiler adapter

**Compilation reliability**
- LaTeX subprocess uses `asyncio.create_subprocess_exec` — never `subprocess.run` (blocking)
- A compilation failure must never produce a partial output file at the output path
- The app must remain fully usable after any compilation failure — no unhandled 500s for LaTeX errors
- All LaTeX errors are caught at the adapter level and surfaced as structured `CompilationError` objects

---

## Usage Guidelines

**For AI Agents:** Read this file before implementing any code in this project. Follow ALL rules exactly. When in doubt, prefer the more restrictive option. These rules exist because they prevent real mistakes — not as suggestions.

**For Humans:** Keep this lean. Update when the stack or patterns change. Remove rules that become obvious over time.

_Last Updated: 2026-04-21_
