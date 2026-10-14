.PHONY: run test lint fmt check hooks

run:
	uv run uvicorn app.main:app --reload

test:
	uv run pytest --cov

lint:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

fmt:
	uv run ruff format .
	uv run ruff check --fix .

check: lint test

hooks:
	uv run pre-commit install
