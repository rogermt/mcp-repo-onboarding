# ONBOARDING.md

## Overview
Repo path: /home/rogermt/mcp-repo-onboarding

## Environment setup
Python version: 3.11

## Install dependencies
* `pip install .` (Install the project package.)

## Run / develop locally
* `bash scripts/create_issues.sh` (Script to create GitHub issues for mcp-repo-onboarding.)
* `bash scripts/eval_assertions.sh` (Run repo script entrypoint.)
* `bash scripts/run_headless_evaluation.sh` (Run repo script entrypoint.)
* `bash scripts/run_specific_repos.sh` (Run repo script entrypoint.)
* `bash scripts/setup_evaluation_repos.sh` (Run repo script entrypoint.)
* `bash scripts/teardown_and_clone_repos.sh` (Run repo script entrypoint.)
* `bash scripts/validate_onboarding_list.sh` (Run repo script entrypoint.)

## Run tests
No explicit commands detected.

## Lint / format
No explicit commands detected.

## Analyzer notes
* Primary tooling: Python (pyproject.toml present).
* docs list truncated to 10 entries (total=31)

## Dependency files detected
* pyproject.toml (Project configuration and dependency management (PEP 518/621).)

## Useful configuration files
* .pre-commit-config.yaml (Pre-commit hooks configuration (code quality automation).)
* .github/workflows/ci.yml (CI/CD automation workflow.)

## Useful docs
* LICENSE
* README.md
* docs/design/AGENT_ARCHITECTURE_DESIGN.md
* docs/design/AGENT_SCHEMA.md
* docs/design/EXTRACT_OUTPUT_RULES.md
* docs/design/GITHUB_ISSUES_AGENT_ARCHITECTURE.md
* docs/design/SOFTWARE_DESIGN_GUIDE.md
* docs/design/STATIC_ANALYSIS_EXTRACTION_METHODS.md
* docs/design/TEST_DESIGN_AGENT_ARCHITECTURE.md
* docs/design/ignore-handling.md
