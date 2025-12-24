# Implementation Plan: Fix Remaining Code Quality Issues

## Issue Description

After adding Ruff linting configuration, there are remaining code quality issues that need to be addressed following TDD methodology.

## Current State

- ✅ Pre-commit hooks configured (`.pre-commit-config.yaml`)
- ✅ CI/CD enhanced with coverage and type checking
- ✅ Tool configurations added to `pyproject.toml`
- ⚠️ All tests passing but linting may have minor issues

## Proposed Changes

### 1. Ensure All Code Passes Ruff Checks

**Files to Update:**
- `src/mcp_repo_onboarding/server.py` - Already simplified with ternary operators
- `src/mcp_repo_onboarding/analysis.py` - May need minor formatting fixes
- `tests/*.py` - Import sorting and whitespace cleanup

**Approach:**
1. Write tests to verify code quality standards
2. Run Ruff with auto-fix
3. Verify all tests still pass
4. Commit changes

### 2. Add Type Hints to Missing Functions

**Files to Update:**
- `src/mcp_repo_onboarding/analysis.py`:
  - `extract_shell_scripts()` - Change return type from `dict` to `Dict[str, List[CommandInfo]]`
  - `extract_tox_commands()` - Change return type from `dict` to `Dict[str, List[CommandInfo]]`
  - `extract_makefile_commands()` - Already has correct type hint

**Test Strategy:**
1. Write test to verify type hints exist using `typing.get_type_hints()`
2. Add proper type hints
3. Run mypy to verify
4. Ensure all tests pass

### 3. Verify Pre-commit Hooks Work

**Test Strategy:**
1. Make a small intentional formatting error
2. Attempt to commit
3. Verify pre-commit hooks catch and fix it
4. Document the workflow

## Verification Plan

### Automated Tests
```bash
# Run all tests with coverage
uv run pytest --cov=src/mcp_repo_onboarding --cov-report=term-missing

# Run linting
uv run ruff check .

# Run formatting check
uv run ruff format --check .

# Run type checking
uv run mypy src/mcp_repo_onboarding --ignore-missing-imports
```

### Manual Verification
1. Verify pre-commit hooks are installed: `pre-commit run --all-files`
2. Check CI workflow runs successfully
3. Verify code coverage meets 80% threshold

## Success Criteria

- [ ] All Ruff checks pass
- [ ] All tests pass with >80% coverage
- [ ] Type hints added to all public functions
- [ ] Pre-commit hooks installed and working
- [ ] CI/CD pipeline runs successfully
- [ ] Documentation updated

## Notes

- Following TDD: Test first, then implementation
- All changes must maintain or improve code coverage
- No breaking changes to existing API
