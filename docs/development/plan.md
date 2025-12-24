# Development Plan: Formatting Sync and Quality Enforcement

This plan addresses the recurring formatting inconsistencies between local development and CI checks (as seen with `tests/test_type_hints.py`).

## Goal
To synchronize the repository's formatting and ensure that automated checks (pre-commit) effectively block all non-compliant code from being pushed.

## Proposed Strategy

### 1. Immediate Correction (The "Sync" Phase)
- **Force Format**: Run `uv run ruff format .` and `uv run ruff check --fix .` locally to bring all files (including `tests/test_type_hints.py`) into 100% compliance.
- **Verification**: Run `uv run ruff format --check .` locally. If this passes, the CI check is guaranteed to pass.

### 2. Preventive Reinforcement (The "Enforce" Phase)
- **Pre-commit Re-install**: Run `uv run pre-commit install` to ensure Git hooks are active and correctly configured to intercept non-formatted commits.
- **Hook Trigger**: Manually run `uv run pre-commit run --all-files` to baseline the repository.

### 3. Workflow Standardization
- Every subsequent push will be preceded by a local `uv run ruff format --check .` validation.

## Verification Checklist
- [ ] `uv run ruff format --check .` returns exit code 0.
- [ ] `uv run pre-commit run --all-files` passes all checks.
- [ ] No regressions in `uv run pytest`.
