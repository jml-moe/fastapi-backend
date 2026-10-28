dev: migrate
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run pytest

lint:
	uv run ruff check .

migrate:
	uv run alembic upgrade head
