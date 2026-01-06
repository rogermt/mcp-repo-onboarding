# ONBOARDING.md

## Overview
Repo path: /home/rogermt/mcp-repo-onboarding

## Environment setup
Python version: 3.11

## Install dependencies
* `pip install .` (Install the project package.)

## Run / develop locally
* `bash scripts/create_issues.sh` (Script to create GitHub issues for mcp-repo-onboarding.)
* `bash scripts/run_headless_evaluation.sh` (Run repo script entrypoint.)
* `bash scripts/run_specific_repos.sh` (Run repo script entrypoint.)
* `bash scripts/setup_evaluation_repos.sh` (Source B-prompt.txt path from the current working directory.)
* `bash scripts/teardown_and_clone_repos.sh` (Run repo script entrypoint.)

## Run tests
No explicit commands detected.

## Lint / format
No explicit commands detected.

## Analyzer notes
* Primary tooling: Python (pyproject.toml present).
* docs list truncated to 10 entries (total=26)

## Dependency files detected
* pyproject.toml (Project configuration and dependency management (PEP 518/621).)

## Useful configuration files
* .pre-commit-config.yaml (Pre-commit hooks configuration (code quality automation).)
* .github/workflows/ci.yml (CI/CD automation workflow.)

## Useful docs
* LICENSE
* README.md
* docs/design/EXTRACT_OUTPUT_RULES.md
* docs/design/SOFTWARE_DESIGN_GUIDE.md
* docs/design/ignore-handling.md
* docs/development/CONTRIBUTING.md
* docs/development/DEPENDENCIES.md
* docs/development/DEV_Phase_10.md
* docs/development/DEV_Phase_9.md
* docs/development/REQUIREMENTS.md
