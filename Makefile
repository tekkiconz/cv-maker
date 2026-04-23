.PHONY: venv install dev up down test test-local lint lint-local fmt fmt-local typecheck typecheck-local migrate shell

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

venv:
	python3.14 -m venv $(VENV)
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

test-local: install
	$(VENV)/bin/pytest $(ARGS)

lint:
	docker compose run --rm app ruff check . && docker compose run --rm app ruff format --check .

lint-local: install
	$(VENV)/bin/ruff check . && $(VENV)/bin/ruff format --check .

fmt:
	docker compose run --rm app ruff format .

fmt-local: install
	$(VENV)/bin/ruff format .

typecheck:
	docker compose run --rm app mypy app/

typecheck-local: install
	$(VENV)/bin/mypy app/

migrate:
	docker compose run --rm app alembic upgrade head

shell:
	docker compose run --rm app bash
