.PHONY: help install lint typecheck test run webapp docker clean

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:  ## Install package with dev dependencies
	pip install -e ".[dev]"

lint:  ## Run ruff linter and formatter check
	ruff check src/ tests/
	ruff format --check src/ tests/

typecheck:  ## Run mypy type checker
	mypy src/ --ignore-missing-imports

test:  ## Run pytest with coverage
	pytest tests/ -v --tb=short --cov=src --cov-report=term-missing

run:  ## Run the full analysis pipeline
	python -m src.cli

webapp:  ## Launch the Streamlit dashboard
	streamlit run src/webapp/app.py

docker:  ## Build and run with Docker Compose
	docker compose up --build

clean:  ## Remove generated artifacts
	rm -rf outputs/ __pycache__ .pytest_cache .mypy_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
