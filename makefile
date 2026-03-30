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

gen-cocktails-api:
	poetry run datamodel-codegen \
		--url "http://cezzis-cocktailsapi.127.0.0.1.sslip.io/scalar/v1/openapi.json" \
		--input-file-type openapi --output src/cezzis_com_cloudsync_api/infrastructure/clients/cocktails_api/cocktail_api.py \
		--output-model-type pydantic_v2.BaseModel \
		--field-constraints --use-default \
		--use-schema-description \
		--target-python-version 3.12

all:
	@make install
	@make standards
	@make coverage
	@make build
