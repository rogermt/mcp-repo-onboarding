.PHONY: test lint format dev

test:
	python -m pytest

lint:
	flake8 src tests

format:
	black src tests

dev:
	python src/app/main.py
