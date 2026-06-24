# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`aiohttp-docs` is a Python library that auto-generates OpenAPI 3.1 / Swagger UI documentation for aiohttp web servers. Routes are annotated via a `@docs(...)` decorator; a single `setup_docs(app, ...)` call wires in the spec endpoint and Swagger UI.

**Python >=3.13** required. Uses `uv` as the package manager.

## Commands

```bash
# Setup
uv venv && make deps       # Create venv and install all dependencies
make pre-commit            # Install pre-commit hooks (ruff format + check)

# Development
make lint                  # ruff format + ruff check --fix
make test                  # uv run pytest
make test-ci               # pytest with coverage (no warnings)
make test-report           # pytest with HTML coverage report
make lock                  # uv lock --upgrade

# Run a single test
uv run pytest tests/test_file.py::test_name    # by name
uv run pytest -k 'pattern'                     # by keyword

# Run example server
uv run example/

# Update bundled Swagger UI assets
uv run tools/update_swagger_ui/
```

## Architecture

### Public API

`__init__.py` re-exports the intentional public surface. All implementation lives in `_`-prefixed private modules.

### Core Flow

1. **`@docs(...)` decorator** (`_decorator.py`) — attaches an `ApiEndpoint` TypedDict as `_openapi_docs` attribute on the original function; `@wraps` copies `__dict__` to the wrapper so the attribute is visible to the spec builder
2. **`build_openapi_spec(app, info)`** (`_spec_builder.py`) — at startup, iterates `app.router.routes()`, finds handlers with `_openapi_docs`, and builds the full OpenAPI 3.1 spec. Supports both function handlers and class-based views (iterates HTTP methods on classes). Falls back to handler docstrings for descriptions, `__deprecated__` for deprecation, and `request_body` parameter annotations for body models
3. **`SchemaCollector`** (`_spec_builder.py`) — accumulates Pydantic model schemas for `components/schemas`. Rewrites `$defs` refs to `#/components/schemas/` so nested models produce valid OpenAPI `$ref`s. Two entry points: `add_schema_model` (body/response models → full schema + ref) and `process_parameter` (parameter models → field-level schemas only, model itself not added to components)
4. **View factories** (`_views.py`) — `get_json_spec_view` and `get_swagger_view` return closures that capture the built spec, so it's computed once at startup
5. **`setup_docs(app, ...)`** (`_setup.py`) — registers three named routes (names defined in `_constants.py`): static files (`docs.swagger.static`), JSON spec endpoint (`docs.openapi.spec`), and Swagger UI HTML page (`docs.swagger.ui`). The view factories look up these route names to resolve URLs

### Key Design Decisions

- **TypedDicts for OpenAPI structures** (`_spec_models.py`, `_doc_models.py`) — lightweight and directly JSON-serializable, not Pydantic models
- **Pydantic for user schemas** — `model_json_schema()` generates requestBody/response schemas; `model_fields` with alias awareness generates parameters
- **Template substitution** — Swagger UI `index.html` uses `string.Template` with `$path`, `$static`, `$layout` placeholders
- **Bundled Swagger UI** — static assets live in `aiohttp_docs/swagger/`; `tools/update_swagger_ui/` automates downloading new versions from GitHub

### Testing

Tests use `pytest-aiohttp` for async handler testing.

## Code Style

- **Ruff** is the sole linter/formatter: line length 120, single quotes, spaces, Google docstring convention
- All ruff rules enabled except Q000, Q003, COM812
- Pre-commit hooks enforce formatting on commit