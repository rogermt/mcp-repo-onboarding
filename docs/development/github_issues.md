# GitHub Issues for mcp-repo-onboarding Code Quality Improvements

This file contains GitHub issues that can be created manually. Each issue is formatted in Markdown and ready to copy-paste into GitHub's issue creation interface.

---

## Proposed Issue: Fix Remaining Code Quality Issues and Add Complete Type Hints

**Title:** Fix remaining code quality issues and add complete type hints

**Labels:** `enhancement`, `priority: high`, `type-safety`, `quality`

**Description:**

After adding Ruff and mypy configuration, we need to ensure all code passes quality checks and has complete type hints.

### Problem
- `extract_shell_scripts()` returns `dict` instead of `Dict[str, List[CommandInfo]]`
- `extract_tox_commands()` returns `dict` instead of `Dict[str, List[CommandInfo]]`
- Need to verify all code passes Ruff checks
- Need to verify pre-commit hooks work correctly

### Proposed Solution (TDD Approach)

**Step 1: Write Failing Tests**
```python
# tests/test_type_hints.py
import typing
from mcp_repo_onboarding.analysis import (
    extract_shell_scripts,
    extract_tox_commands,
    extract_makefile_commands,
)

def test_extract_shell_scripts_has_proper_type_hints():
    """Verify extract_shell_scripts has proper return type hint."""
    hints = typing.get_type_hints(extract_shell_scripts)
    assert 'return' in hints
    # Should be Dict[str, List[CommandInfo]]
    assert hints['return'].__origin__ == dict

def test_extract_tox_commands_has_proper_type_hints():
    """Verify extract_tox_commands has proper return type hint."""
    hints = typing.get_type_hints(extract_tox_commands)
    assert 'return' in hints
    assert hints['return'].__origin__ == dict
```

**Step 2: Implement Fixes**
- Add proper type hints to functions
- Run `uv run ruff check --fix .`
- Run `uv run ruff format .`

**Step 3: Verify**
- All tests pass
- Ruff checks pass
- mypy checks pass
- Coverage remains >80%

### Files to Update
- `src/mcp_repo_onboarding/analysis/extractors.py`
- `tests/test_type_hints.py` (create new)

### Acceptance Criteria
- [ ] New test file created with type hint verification tests
- [ ] Tests fail initially (TDD red phase)
- [ ] Type hints added to all functions
- [ ] All tests pass (TDD green phase)
- [ ] All Ruff checks pass
- [ ] Code coverage >80%
- [ ] Pre-commit hooks verified working

---

## Issue #32: Add Comprehensive Error Logging

**Title:** Add comprehensive error logging throughout the codebase

**Labels:** `enhancement`, `priority: high`, `quality`

**Description:**

Currently, the codebase has silent exception catching with no logging, making debugging production issues difficult.

### Problem
- Silent `except OSError` blocks in `analysis.py` (lines 133-134, 162-163)
- Broad `except Exception` in `onboarding.py` (line 38-40)
- No logging infrastructure for debugging

### Proposed Solution
1. Add Python's `logging` module throughout the codebase
2. Replace broad exception handlers with specific exception types
3. Log errors with context (file paths, operation attempted)
4. Add structured logging with appropriate log levels

### Files to Update
- `src/mcp_repo_onboarding/analysis.py`
- `src/mcp_repo_onboarding/onboarding.py`
- `src/mcp_repo_onboarding/server.py`

### Example
```python
import logging

logger = logging.getLogger(__name__)

try:
    content = (root / makefile_path).read_text(encoding="utf-8", errors="ignore")
except OSError as e:
    logger.error(f"Failed to read Makefile at {makefile_path}: {e}")
    return {}
```

### Acceptance Criteria
- [x] Logging configured in all modules
- [x] All exception handlers log errors with context
- [x] No silent failures in production code
- [x] Tests verify logging behavior

---

## Issue #33: Add Complete Type Hints and Enable mypy Strict Mode

**Title:** Add complete type hints and enable mypy strict mode

**Labels:** `enhancement`, `priority: high`, `type-safety`

**Description:**

Several functions are missing return type hints, and mypy is not configured in strict mode.

### Problem
- `extract_shell_scripts()` returns `dict` instead of `Dict[str, List[CommandInfo]]`
- `extract_tox_commands()` returns `dict` instead of `Dict[str, List[CommandInfo]]`
- `extract_makefile_commands()` returns `Dict[str, List[CommandInfo]]` but not consistently
- No mypy strict mode enforcement

### Proposed Solution
1. Add explicit return type hints to all functions
2. Enable mypy strict mode in `pyproject.toml`
3. Fix all type errors revealed by strict mode
4. Add mypy to CI pipeline (already done in recent update)

### Files to Update
- `src/mcp_repo_onboarding/analysis.py` (lines 168, 255, 305)
- `src/mcp_repo_onboarding/describers.py`
- `pyproject.toml` (enable strict mode)

### Acceptance Criteria
- [x] All functions have complete type hints
- [x] mypy strict mode enabled
- [x] All mypy errors resolved
- [x] CI enforces type checking

---

## Issue #34: Refactor `analyze_repo` Function to Reduce Complexity

**Title:** Refactor `analyze_repo` function to reduce cyclomatic complexity

**Labels:** `refactoring`, `priority: high`, `maintainability`

**Description:**

The `analyze_repo` function is 189 lines long with high cyclomatic complexity, making it difficult to maintain and test.

### Problem
- `analyze_repo()` in `analysis.py` (lines 380-568) is too long
- Multiple responsibilities in one function
- Hard to test individual components
- High cognitive load for developers

### Proposed Solution
Break down into smaller, focused functions:

1. `_scan_and_categorize_files()` - File scanning and categorization
2. `_extract_all_commands()` - Command extraction from all sources
3. `_infer_python_environment()` - Python environment detection
4. `_build_repo_analysis()` - Final assembly of RepoAnalysis object

### Files to Update
- `src/mcp_repo_onboarding/analysis.py`

### Acceptance Criteria
- [ ] `analyze_repo` is under 50 lines
- [ ] Each extracted function has a single responsibility
- [ ] All existing tests still pass
- [ ] New unit tests for extracted functions
- [ ] Cyclomatic complexity < 10 per function

---

## Issue #35: Add Comprehensive Docstrings

**Title:** Add comprehensive docstrings to all public functions

**Labels:** `documentation`, `priority: medium`, `quality`

**Description:**

Many functions lack docstrings or have incomplete documentation.

### Problem
- Missing docstrings in `get_config_priority()`, `get_doc_priority()`
- Incomplete docstrings missing Args, Returns, Examples
- No module-level docstrings

### Proposed Solution
1. Add Google-style docstrings to all public functions
2. Include Args, Returns, Raises, and Examples sections
3. Add module-level docstrings
4. Configure pydocstyle to enforce standards

### Files to Update
- All files in `src/mcp_repo_onboarding/`

### Example
```python
def get_config_priority(path: str) -> int:
    """Calculate priority score for configuration files.

    Higher priority files are sorted first in the analysis results.

    Args:
        path: Relative path to the configuration file.

    Returns:
        Priority score (0-100), where 100 is highest priority.

    Examples:
        >>> get_config_priority("Makefile")
        100
        >>> get_config_priority("tox.ini")
        80
    """
```

### Acceptance Criteria
- [x] All public functions have complete docstrings
- [x] pydocstyle configured and passing
- [x] Module-level docstrings added
- [x] Examples included for complex functions

---

## Issue #36: Add Error Scenario Test Coverage

**Title:** Add comprehensive error scenario test coverage

**Labels:** `testing`, `priority: medium`, `quality`

**Description:**

Current tests focus on happy paths. Need tests for error scenarios and edge cases.

### Missing Test Coverage
1. **Error scenarios:**
   - Permission denied errors
   - Corrupted file handling
   - Extremely large repositories
   - Symbolic link handling

2. **Edge cases:**
   - Empty repository
   - Repository with only binary files
   - Circular symbolic links
   - Invalid UTF-8 in files

3. **Performance:**
   - `max_files` limit behavior
   - Large repository benchmarks

### Proposed Solution
1. Add error scenario tests to `tests/test_analysis.py`
2. Add edge case tests
3. Add performance benchmarks
4. Consider property-based testing with `hypothesis`

### Acceptance Criteria
- [x] Test coverage > 85%
- [x] All error paths tested
- [x] Edge cases covered
- [x] Performance benchmarks added

---

## Issue #37: Extract Configuration to Dedicated Module

**Title:** Extract magic numbers and configuration to dedicated config module

**Labels:** `refactoring`, `priority: medium`, `maintainability`

**Description:**

Magic numbers and configuration are scattered throughout the codebase.

### Problem
```python
MAX_DOCS_CAP = 10      # Line 47
MAX_CONFIG_CAP = 15    # Line 48
max_files: int = 5000  # Multiple locations
```

### Proposed Solution
Create `src/mcp_repo_onboarding/config.py`:

```python
from dataclasses import dataclass
from typing import List

@dataclass
class AnalysisConfig:
    """Configuration for repository analysis."""

    MAX_DOCS_CAP: int = 10
    MAX_CONFIG_CAP: int = 15
    DEFAULT_MAX_FILES: int = 5000

    SAFETY_IGNORES: List[str] = [
        ".git/",
        ".venv/",
        # ... etc
    ]

    CONFIG_FILE_TYPES: set[str] = {
        "makefile",
        "tox.ini",
        # ... etc
    }
```

### Files to Update
- Create `src/mcp_repo_onboarding/config.py`
- Update `src/mcp_repo_onboarding/analysis/core.py` (and other analysis modules)

### Acceptance Criteria
- [x] All configuration in dedicated module
- [x] No magic numbers in code
- [x] Configuration is type-safe
- [x] Easy to modify for testing

---

## Proposed Issue: Add Dependency Upper Bounds and Security Scanning

**Title:** Add dependency upper bounds and security scanning

**Labels:** `dependencies`, `priority: medium`, `security`

**Description:**

Dependencies have no upper bounds, risking breaking changes from major updates.

### Problem
```toml
dependencies = [
    "mcp[cli]>=1.25.0",      # No upper bound
    "packaging>=25.0",        # No upper bound
    "pathspec>=0.12.1",       # No upper bound
    "pydantic>=2.12.5",       # No upper bound
]
```

### Proposed Solution
1. Add upper bounds for major versions
2. Set up Dependabot or Renovate
3. Add security scanning with `pip-audit` or `safety`
4. Add dependency update workflow

### Files to Update
- `pyproject.toml`
- `.github/dependabot.yml` (create)
- `.github/workflows/security.yml` (create)

### Example
```toml
dependencies = [
    "mcp[cli]>=1.25.0,<2.0.0",
    "packaging>=25.0,<26.0",
    "pathspec>=0.12.1,<1.0.0",
    "pydantic>=2.12.5,<3.0.0",
]
```

### Acceptance Criteria
- [ ] All dependencies have upper bounds
- [ ] Dependabot configured
- [ ] Security scanning in CI
- [ ] Documentation on dependency updates

---

## Issue #38: Improve Error Response Handling in Server

**Title:** Use Pydantic models for error responses instead of manual JSON

**Labels:** `enhancement`, `priority: medium`, `api`

**Description:**

Server error responses use manual JSON string formatting, which is error-prone.

### Problem
```python
# server.py line 109-110
except ValueError as e:
    return f'{{"error": "{str(e)}"}}' # ⚠️ Manual JSON formatting
```

### Proposed Solution
1. Create error response Pydantic models
2. Use consistent error response format
3. Include error codes and details

### Files to Update
- `src/mcp_repo_onboarding/schema.py` (add error models)
- `src/mcp_repo_onboarding/server.py`

### Example
```python
# schema.py
class ErrorResponse(BaseModel):
    error: str
    error_code: str
    details: Optional[Dict[str, Any]] = None

# server.py
except ValueError as e:
    error = ErrorResponse(
        error=str(e),
        error_code="INVALID_PATH",
        details={"path": path}
    )
    return error.model_dump_json()
```

### Acceptance Criteria
- [x] Logic split into helper functions or classes
- [x] `analyze_repo` function length significantly reduced
- [x] No logic changes (refactor only)
- [x] Tests pass
- [x] Error response models defined
- [x] All error responses use models
- [x] Error codes documented
- [x] Tests for error responses

---

## Issue #39: Add Performance Benchmarks and Caching

**Title:** Add performance benchmarks and optional caching layer

**Labels:** `performance`, `priority: low`, `enhancement`

**Description:**

No performance benchmarks or caching for repeated analysis operations.

### Proposed Solution
1. Add performance benchmarks using `pytest-benchmark`
2. Implement optional caching layer
3. Add progress callbacks for large repositories
4. Consider async I/O for file operations

### Files to Update
- `tests/test_performance.py` (create)
- `src/mcp_repo_onboarding/analysis/core.py`
- `src/mcp_repo_onboarding/cache.py` (create)

### Acceptance Criteria
- [ ] Performance benchmarks added
- [ ] Optional caching implemented
- [ ] Progress callbacks for long operations
- [ ] Performance regression tests in CI

---

## Issue #40: Enhance Security with Symbolic Link Protection

**Title:** Add symbolic link detection and protection

**Labels:** `security`, `priority: medium`, `enhancement`

**Description:**

Current path sandboxing doesn't protect against symbolic link attacks.

### Problem
- No symbolic link detection in `resolve_path_inside_repo()`
- Potential for symbolic link traversal attacks
- No protection against race conditions

### Proposed Solution
1. Add symbolic link detection
2. Use `Path.is_relative_to()` (Python 3.9+)
3. Document security assumptions
4. Add security tests

### Files to Update
- `src/mcp_repo_onboarding/onboarding.py`
- `tests/test_onboarding.py`
- `README.md` (security documentation)

### Acceptance Criteria
- [x] Traversal attempts blocked
- [x] Symlinks inside the repo are still supported
- [x] Security tests pass
- [x] Code reviewed for common bypasses
- [x] Security assumptions documented
- [ ] No race conditions in path resolution

---

## Proposed Issue: Document Defaults in Prompt Text

**Title:** Define and document defaults in evaluation prompt text

**Labels:** `documentation`, `priority: low`, `prompt-engineering`

**Description:**

The prompt text in `docs/evaluation/B-prompt.txt` does not explicitly document the default values used by the analysis (e.g., `MAX_DOCS_CAP`, `max_files`).

### Proposed Solution
1. Review `src/mcp_repo_onboarding/config.py` (once created) for default values.
2. Update `docs/evaluation/B-prompt.txt` to clearly state these defaults.

### Acceptance Criteria
- [ ] Defaults documented in `B-prompt.txt`
- [ ] Consistent with code values

---

## Priority Summary

### High Priority (Do First) 🔴
1. Issue #32: Add Comprehensive Error Logging
2. Issue #33: Add Complete Type Hints
3. Issue #34: Refactor `analyze_repo` Function

### Medium Priority (Do Soon) 🟡
4. Issue #35: Add Comprehensive Docstrings
5. Issue #36: Add Error Scenario Tests
6. Issue #37: Extract Configuration Module
7. Proposed Issue: Dependency Upper Bounds
8. Issue #38: Improve Error Responses
10. Issue #40: Symbolic Link Protection

### Low Priority (Nice to Have) 🟢
9. Issue #39: Performance Benchmarks
11. Proposed Issue: Document Defaults in Prompt Text

---

## How to Create These Issues

1. Go to https://github.com/YOUR_USERNAME/mcp-repo-onboarding/issues/new
2. Copy the title from each issue above
3. Copy the description (everything under the title)
4. Add the suggested labels
5. Create the issue

Alternatively, you can use the GitHub CLI:

```bash
# Install GitHub CLI if needed
# brew install gh  # macOS
# sudo apt install gh  # Ubuntu

# Authenticate
gh auth login

# Create issues from this file
gh issue create --title "Add comprehensive error logging" --body "$(cat github_issues.md | sed -n '/^## Issue 1/,/^---$/p')" --label "enhancement,priority: high,quality"
```
