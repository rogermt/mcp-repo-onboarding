# ONBOARDING.md

## Overview
Repo path: /home/rogermt/mcp-repo-onboarding

## Environment setup
Python version: 3.11
(Generic suggestion)
* `python3 -m venv .venv` (Create virtual environment.)
* `source .venv/bin/activate` (Activate virtual environment.)

## Install dependencies
* `pip install -e .` (Install the project in editable mode.)

## Run / develop locally
No explicit commands detected.

## Run tests
* `tox` (Run tests via tox)

## Lint / format
* `tox -e flake8` (Run flake8 linting via tox)

## Analyzer notes
* docs list truncated to 10 entries (total=29)

## Dependency files detected
* pyproject.toml
* tests/fixtures/excessive-docs-configs/pyproject.toml
* tests/fixtures/excessive-docs-configs/requirements{1..60}.txt
* tests/fixtures/ignore_handling/repo_basic_gitignore/requirements.txt
* tests/fixtures/ignore_handling/repo_no_gitignore/requirements.txt
* tests/fixtures/ignore_handling/repo_safety_override/pyproject.toml
* tests/fixtures/imgix-python-config-priority/setup.py
* tests/fixtures/imgix-python-tox-lint/setup.py
* tests/fixtures/phase3-2-tox-nox-make/pyproject.toml
* tests/fixtures/phase3-2-tox-nox-make/requirements.txt
* tests/fixtures/pyproject-rich/pyproject.toml
* tests/fixtures/python-pin-range/pyproject.toml
* tests/fixtures/setuptools-only-no-install/setup.py

## Useful configuration files
* tests/fixtures/excessive-docs-configs/Makefile (Primary task runner for development and build orchestration.)
* tests/fixtures/imgix-python-config-priority/Makefile (Primary task runner for development and build orchestration.)
* tests/fixtures/makefile-with-recipes/Makefile (Primary task runner for development and build orchestration.)
* tests/fixtures/phase3-2-tox-nox-make/Makefile (Primary task runner for development and build orchestration.)
* tests/fixtures/imgix-python-config-priority/tox.ini (Test environment orchestrator (tox).)
* tests/fixtures/imgix-python-tox-lint/tox.ini (Test environment orchestrator (tox).)
* tests/fixtures/phase3-2-tox-nox-make/noxfile.py (Test automation sessions (nox).)
* tests/fixtures/phase3-2-tox-nox-make/tox.ini (Test environment orchestrator (tox).)
* .pre-commit-config.yaml (Pre-commit hooks configuration (code quality automation).)
* tests/fixtures/imgix-python-config-priority/.pre-commit-config.yaml (Pre-commit hooks configuration (code quality automation).)
* .github/workflows/ci.yml (CI/CD automation workflow.)
* .github/workflows/security.yml (CI/CD automation workflow.)
* tests/fixtures/phase3-2-tox-nox-make/pytest.ini

## Useful docs
* README.md
* docs/development/CONTRIBUTING.md
* tests/fixtures/docs-with-binaries/README.md
* tests/fixtures/excessive-docs-configs/README.md
* tests/fixtures/setuptools-only-no-install/README.md
* docs/design/SOFTWARE_DESIGN_GUIDE.md
* docs/design/ignore-handling.md
* docs/development/DEPENDENCIES.md
* docs/development/DEV Phase 6.md
* docs/development/PR_DESCRIPTION.md
