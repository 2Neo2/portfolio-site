.PHONY: run test lint fmt check hooks docker-build docker-up docker-down

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

docker-build:
	docker compose build

docker-up:
	docker compose up --build -d

docker-down:
	docker compose down
