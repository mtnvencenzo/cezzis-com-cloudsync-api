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

coverage:
	poetry run pytest -v --cov=src/cezzis_com_cloudsync_api --cov-report=xml:coverage.xml --cov-report=term --junitxml=pytest-results.xml

all:
	@make install
	@make standards
	@make coverage
	@make build
