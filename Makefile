.PHONY: venv install dev up down test lint fmt typecheck migrate shell

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3.12 -m venv $(VENV)
	$(PIP) install --upgrade pip

install: venv
	$(PIP) install -e ".[dev]"

dev:
	docker compose up --build

up:
	docker compose up --build -d

down:
	docker compose down

test:
	docker compose run --rm app pytest $(ARGS)

lint:
	docker compose run --rm app ruff check . && docker compose run --rm app ruff format --check .

fmt:
	docker compose run --rm app ruff format .

typecheck:
	docker compose run --rm app mypy app/

migrate:
	docker compose run --rm app alembic upgrade head

shell:
	docker compose run --rm app bash
