.PHONY: install lint format typecheck test test-unit test-integration \
        clean build up down rebuild logs health readiness all precommit

VENV = .venv
UV = uv

install:
	$(UV) sync

lint:
	$(UV) run ruff check rag_system/ tests/

format:
	$(UV) run ruff format rag_system/ tests/

typecheck:
	$(UV) run mypy --strict --no-warn-unused-ignores -p rag_system

test:
	$(UV) run pytest tests/

test-unit:
	$(UV) run pytest tests/unit/ --cov=rag_system --cov-report=term-missing

test-integration:
	$(UV) run pytest tests/integration/

clean:
	rm -rf $(VENV) .pytest_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

precommit:
	$(UV) run pre-commit run --all-files

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

rebuild: down build up

logs:
	docker compose logs -f

health:
	curl -s http://localhost:8000/health | python3 -m json.tool

readiness:
	curl -s http://localhost:8000/readiness | python3 -m json.tool

all: lint typecheck test-unit
