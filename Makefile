.PHONY: run test lint fmt

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy app

fmt:
	uv run ruff format .
	uv run ruff check --fix .
