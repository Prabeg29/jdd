.DEFAULT_GOAL := help
.PHONY: help sync lint format test db-up db-down validate-config

help: ## List targets
	@grep -E '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "} {printf "  %-16s %s\n", $$1, $$2}'

sync: ## Install dependencies into .venv
	uv sync

lint: ## Ruff lint and format check
	uv run ruff check .
	uv run ruff format --check .

format: ## Apply ruff fixes and formatting
	uv run ruff check --fix .
	uv run ruff format .

db-up: ## Start local Postgres and wait until healthy
	docker compose up -d --wait

db-down: ## Stop local Postgres
	docker compose down

test: db-up ## Run the test suite (starts local Postgres)
	uv run pytest

validate-config: ## Validate config/pipeline.yaml and the example files
	uv run python scripts/validate_config.py
