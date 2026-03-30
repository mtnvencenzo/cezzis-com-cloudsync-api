.PHONY: install update build test lint format standards test coverage models

# -------------------------------------------------------
# General commands
#--------------------------------------------------------
install:
	poetry install --with dev

update:
	poetry update

build:
	poetry build

lint:
	poetry run ruff check --fix . --config .ruff.toml

format:
	poetry run ruff format . --config .ruff.toml

standards:
	@make lint
	@echo "Code standards check complete."
	@make format
	@echo "Code formatting complete."

test:
	poetry run pytest

run:
	cd src/cezzis_com_cloudsync_api && uvicorn app:api --reload

coverage:
	poetry run pytest -v --cov=src/cezzis_com_cloudsync_api --cov-report=xml:coverage.xml --cov-report=term --junitxml=pytest-results.xml

all:
	@make install
	@make standards
	@make coverage
	@make build


# -------------------------------------------------------
# SQL Alchemy Alembic database migration commands
#--------------------------------------------------------


# example: make db-revision MSG="initial-migration"
db-revision:
	@SLUG=$$(echo "$(MSG)" | tr '[:upper:]' '[:lower:]' | tr ' ' '_' | tr -cd '[:alnum:]_-') && \
	REV_ID=$$(date +%Y%m%d_%H%M%S)_$$SLUG && \
	ENV=loc poetry run alembic revision --autogenerate -m "$(MSG)" --rev-id=$$REV_ID

db-upgrade:
	ENV=loc poetry run alembic upgrade head

db-downgrade:
	ENV=loc poetry run alembic downgrade -1

# CI/CD: Show current migration status
db-current:
	ENV=loc poetry run alembic current

# CI/CD: Check if there are pending migrations (exits non-zero if pending)
db-check:
	ENV=loc poetry run alembic check

# CI/CD: Generate SQL script for all migrations (offline, no DB required)
# make db-sql > migrations.sql
db-sql:
	ENV=loc poetry run alembic upgrade head --sql

# CI/CD: Show migration history
db-history:
	ENV=loc poetry run alembic history
