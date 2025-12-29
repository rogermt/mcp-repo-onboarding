# Guide to Evaluation and Automation Scripts

This document describes the purpose and usage of the shell and Python scripts located in the `/scripts` directory. These scripts are used for repository setup, evaluation, validation, and issue management.

---

## Evaluation & Validation

### `validate_onboarding.py`
- **Purpose**: A deterministic validator to check if a given `ONBOARDING.md` file conforms to the project's strict formatting and content rules (V1-V8). It is the source of truth for "correctness."
- **Usage**: `python scripts/validate_onboarding.py <path_to_ONBOARDING.md>`
- **Exits** with code `0` on success and `1` on failure, printing all validation errors.

### `run_headless_evaluation.sh`
- **Purpose**: Runs the full, end-to-end evaluation suite across a predefined set of target repositories (`searxng`, `Paper2Code`, etc.).
- **Usage**: `bash scripts/run_headless_evaluation.sh`
- **Process**:
    1. Calls `setup_evaluation_repos.sh` to configure the target repos.
    2. Runs `gemini` in headless (`--yolo`) mode against each repo using the `/generate_onboarding` prompt.
    3. After generation, it runs `validate_onboarding.py` against each resulting `ONBOARDING.md` file.
    4. Logs all output to `evaluation_results.log` and exits with an error if any validation fails.

### `run_specific_repos.sh`
- **Purpose**: Runs the same evaluation process as the headless script, but only for a specified list of 1-3 repositories. Useful for targeted testing.
- **Usage**: `bash scripts/run_specific_repos.sh repo1 repo2`

---

## Repository & Environment Management

### `setup_evaluation_repos.sh`
- **Purpose**: Configures the target evaluation repositories by creating a `.gemini/settings.json` file in each one. This file points the `repo-onboarding` MCP server to the correct local instance and sets the `REPO_ROOT` for analysis.
- **Usage**: This script is typically called by `run_headless_evaluation.sh` and does not need to be run manually.

### `teardown_and_clone_repos.sh`
- **Purpose**: Deletes and re-clones the target evaluation repositories to ensure they are in a clean, known-good state before an evaluation run.
- **Usage**: `bash scripts/teardown_and_clone_repos.sh`

---

## Project Management

### `create_issues.sh`
- **Purpose**: A utility script to bulk-create GitHub issues from a predefined list. This was used for initial project setup.
- **Usage**: `bash scripts/create_issues.sh`
- **Note**: This script requires the GitHub CLI (`gh`) to be installed and authenticated.
