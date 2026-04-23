# Suggested Commands

## Run App
```bash
docker compose up --build
```

## Tests
```bash
docker compose run --rm app pytest
docker compose run --rm app pytest app/services/profile_service.test.py
```

## Lint + Format
```bash
docker compose run --rm app ruff check . && ruff format .
```

## Type Check
```bash
docker compose run --rm app mypy app/
```

## Migrations
```bash
# Generate after model changes
docker compose run --rm app alembic revision --autogenerate -m "description"
# Apply
docker compose run --rm app alembic upgrade head
```
