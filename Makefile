.PHONY: deploy lint test test-cov format install-dev install-git-hooks
	
deploy:
	@echo "exporting requirements.txt..."
	uv export --format requirements-txt --output-file requirements.txt --no-hashes --no-emit-project

	@echo "Deploying Lambda function..."
	bash deploy_scripts/deploy.sh

	@echo "cleaning up..."
	rm -rf requirements.txt

lint:
	@echo "Running linter..."
	ruff format . && ruff check --fix .

test:
	@echo "Running tests..."
	uv run pytest

test-cov:
	@echo "Running tests with coverage..."
	uv run pytest --cov=app --cov-report=term-missing --cov-report=html

install-dev:
	@echo "Installing development dependencies..."
	uv pip install -e ".[dev]"

start_dev:
	@echo "Starting development server..."
	uv run uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload

create_migration:
	@echo "Creating migration: $(msg)"
	uv run alembic revision --autogenerate -m "$(msg)"

migrate:
	@echo "Running migrations..."
	uv run alembic upgrade head

migrate_down:
	@echo "Rolling back migration..."
	uv run alembic downgrade -1

migrate_history:
	@echo "Migration history..."
	uv run alembic history

seed:
	@echo "Running all seeders..."
	uv run python -m app.db.seeders.run_seeders

install-git-hooks:
	@echo "Installing repository git hooks..."
	chmod +x .githooks/pre-commit
	git config core.hooksPath .githooks
	@echo "Git hooks installed. pre-commit will run startup checks before commit."