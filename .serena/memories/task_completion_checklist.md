# Task Completion Checklist

After implementing any feature or fix:

1. Run lint: `docker compose run --rm app ruff check . && ruff format .`
2. Run type check: `docker compose run --rm app mypy app/`
3. Run tests: `docker compose run --rm app pytest`
4. If models changed: generate + apply migration
   ```bash
   docker compose run --rm app alembic revision --autogenerate -m "description"
   docker compose run --rm app alembic upgrade head
   ```
5. Verify Tiger Style invariants:
   - Precondition + postcondition assertions in new functions
   - Loop bounds use constants from `constants/limits.py`
   - No raw `os.environ` reads
