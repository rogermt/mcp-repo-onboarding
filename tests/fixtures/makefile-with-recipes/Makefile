# A makefile to test noisy recipe extraction
SHELL := /bin/bash
VENV := .venv

test: ## Run tests
	@echo "Running tests..."
	$(VENV)/bin/pytest \
		--cov=src \
		--cov-report=term-missing

lint:
	@flake8 src
