.PHONY: venv deps lock lint test test-ci test-report pre-commit update-swagger example

venv:
	uv venv

deps:
	uv sync --frozen --all-extras --dev

lock:
	uv lock --upgrade

lint:
	uv run ruff format
	uv run ruff check --fix

test:
	uv run pytest

test-ci:
	uv run pytest -p no:warnings --cov=aiohttp_docs

test-report:
	uv run pytest -p no:warnings --cov=aiohttp_docs --cov-report=html

pre-commit:
	pre-commit install

update-swagger:
	uv run -m tools.update_swagger_ui

example:
	uv run -m example
