.PHONY: venv deps lock lint test test-ci test-report pre-commit

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
