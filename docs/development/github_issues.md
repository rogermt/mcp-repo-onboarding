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

## Issue #41: Document Defaults in Prompt Text
### Phase 6: Evaluation Regressions & Standards (Hardening)

**Title:** Define and document defaults in evaluation prompt text

**Labels:** `documentation`, `priority: low`, `prompt-engineering`

**Description:**

The prompt text in `docs/evaluation/B-prompt.txt` does not explicitly document the default values used by the analysis (e.g., `MAX_DOCS_CAP`, `max_files`).

### Proposed Solution
1. Review `src/mcp_repo_onboarding/config.py` for default values.
2. Update `docs/evaluation/B-prompt.txt` and `docs/evaluation/phase5-ab-prompts.md` to clearly state these defaults.

### Acceptance Criteria
- [x] Defaults documented in `B-prompt.txt`
- [x] Defaults synced to `phase5-ab-prompts.md`
- [x] Consistent with code values

---

## Issue #42: Add Dependency Upper Bounds and Security Scanning

**Title:** Add dependency upper bounds and security scanning

**Labels:** `dependencies`, `priority: medium`, `security`

**Description:**

Dependencies have no upper bounds, risking breaking changes from major updates.

### Proposed Solution
1. Add upper bounds for major versions in `pyproject.toml`.
2. Set up Dependabot or Renovate.
3. Add security scanning with `pip-audit`.
4. Add dependency update workflow.

### Acceptance Criteria
- [x] All dependencies have upper bounds
- [x] Dependabot configured
- [x] Security scanning in CI
- [x] Documentation on dependency updates

## Issue #50: Binary/Asset Exclusion for Documentation

**Title:** Exclude binary and non-human asset files from documentation list

**Labels:** `enhancement`, `priority: medium`, `quality`

**Description:**

Currently, binary files (images, PDFs) and assets (CSS, JS) can be categorized as documentation if they reside in the `docs/` folder or have "readme" in their name, consuming the `MAX_DOCS_CAP`.

### Proposed Solution
1. Create a denylist of binary/asset extensions in `config.py`.
2. Implement filtering in `_categorize_files` to skip these extensions.
3. Allowlist specific human-readable extensions (.md, .rst, .txt, .adoc) for files within `docs/`.
4. Ensure top-level README/CONTRIBUTING are always included.
5. Enhance documentation prioritization heuristics.

### Acceptance Criteria
- [x] Binary files (.png, .jpg, .pdf, etc.) excluded from `docs`.
- [x] Non-human assets (.css, .js) excluded from `docs`.
- [x] Truncation totals only reflect human-readable docs.
- [x] README remains high priority.
- [x] Tests verify filtering and prioritization.

---

## Issue #10: Use tomllib to improve pyproject.toml signal accuracy

**Title:** Parse pyproject.toml using Python’s stdlib tomllib instead of regex

**Labels:** `enhancement`, `priority: high`, `quality`

**Description:**

Moved from basic line/regex scanning to robust TOML parsing using the standard library's `tomllib`.

### Achievements
- [x] Accurate detection of `requires-python` constraints.
- [x] Robust package manager detection (Poetry, Hatch, PDM, Flit).
- [x] Build backend extraction.
- [x] Graceful handling of malformed TOML files.
- [x] Dedicated test suite `tests/test_pyproject_parsing.py`.

---

## Issue #53 — BUG: Python version pins must be exact versions only

**Title:** BUG: Python version pins must be exact versions only (reject ranges like `>=3.10`)

**Labels:** bug, phase6, correctness

**Context**
We observed repos (e.g., wagtail) where compatibility constraints like `requires-python = ">=3.10"` were rendered as a “pin” (`Python version: >=3.10`). This violates grounding: ranges are not pins.

**Rules (must be enforced in analyzer output)**
- `python.pythonVersionHints` must contain only **exact version strings** matching:
  - `X.Y` or `X.Y.Z` where X/Y/Z are digits (e.g., `3.14`, `3.14.0`)
- Reject and never include in `pythonVersionHints`:
  - `>=3.10`, `^3.11`, `~=3.12`, `!=3.10.*`, `3.x`, `3.*`, `3`
  - any string containing operator/wildcard/range syntax
- If only ranges are available (pyproject constraints, poetry constraints), treat as **no pin**:
  - `pythonVersionHints` remains empty

**Examples**
- `requires-python = ">=3.10"` → `pythonVersionHints: []`
- workflow `env: PYTHON_VERSION: "3.14"` → `pythonVersionHints: ["3.14"]`

**Acceptance**
- Wagtail-style repo no longer yields `>=3.10` inside `pythonVersionHints`.
- Workflow pins like `"3.14"` continue to be detected as exact versions.

**Tests (must be added)**
1) Fixture: `tests/fixtures/python-pin-range/pyproject.toml`
   - contains `requires-python = ">=3.10"`
   - Assert `analysis.python.pythonVersionHints` is empty/None

2) Fixture: `tests/fixtures/workflow-python-pin-env/.github/workflows/checker.yml`
   - contains `env: PYTHON_VERSION: "3.14"`
   - Assert `analysis.python.pythonVersionHints == ["3.14"]`

3) Negative test (or param): workflow pin `PYTHON_VERSION: "3.x"`
   - Assert hints empty

---

## Issue #54 — BUG: “No pin” phrasing must be exact and standalone

**Title:** BUG: When no pin exists, render exactly “No Python version pin detected.”

**Labels:** bug, phase6, ux

**Context**
We observed output like:
- `Python version: No Python version pin detected.`

This violates the contract: the “no pin” phrase must be exact and standalone.

**Rules (must be enforced in generated ONBOARDING.md)**
Under `## Environment setup`, if no pin exists, the line must be exactly:

- `No Python version pin detected.`

Forbidden:
- `Python version: No Python version pin detected.`
- any paraphrase like “No pin found.”

**Examples**
- Good:
  - `No Python version pin detected.`
- Bad:
  - `Python version: No Python version pin detected.`

**Acceptance**
- All outputs render the no-pin phrase exactly, with no prefix.

**Tests (validator-enforced; must be added under #56)**
- Validator Rule V3 fails if it finds the forbidden pattern:
  - `Python version: No Python version pin detected.`

---

## Issue #55 — UX: venv snippet must be labeled “(Generic suggestion)”

**Title:** UX: Always label venv snippet as “(Generic suggestion)” unless explicitly detected

**Labels:** phase6, ux

**Context**
Venv snippets are generic guidance unless the analyzer explicitly detected venv commands (rare). Unlabeled venv snippets look like detected repo instructions.

**Rules (must be enforced in generated ONBOARDING.md)**
If ONBOARDING contains either:
- `python -m venv .venv` OR `python3 -m venv .venv`

Then a line containing exactly:
- `(Generic suggestion)`

must appear within 3 lines above the snippet.

**Examples**
Good:
- `(Generic suggestion)`
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

Bad:
- venv snippet present with no `(Generic suggestion)` label.

**Acceptance**
- Any venv snippet is always labeled generic.

**Tests (validator-enforced; must be added under #56)**
- Validator Rule V4:
  - detects venv snippet
  - fails if `(Generic suggestion)` not found within 3 lines above

---

## Issue #56 — TOOLING EPIC: Deterministic ONBOARDING.md validator (single source of truth)

**Title:** TOOLING: Add deterministic ONBOARDING.md validator to enforce prompt/format rules (V1–V8)

**Labels:** phase6, tooling, epic, evaluation

**Context**
ONBOARDING.md is generated by an LLM. Prompt rules drift. We need a deterministic validator that fails evaluation runs when output violates the contract. This validator is the enforcement mechanism for #54/#55/#57 and formatting stability.

**Deliverable**
- A deterministic validator script (recommended: `docs/evaluation/validate_onboarding.py`)
- Called by `docs/evaluation/run_headless_evaluation.sh`
- Non-zero exit on failure with clear messages (rule id + location + what failed)

**Rules (V1–V8)**
V1 — Required headings exist in exact order:
1) `# ONBOARDING.md`
2) `## Overview`
3) `## Environment setup`
4) `## Install dependencies`
5) `## Run / develop locally`
6) `## Run tests`
7) `## Lint / format`
8) `## Dependency files detected`
9) `## Useful configuration files`
10) `## Useful docs`
`## Analyzer notes` is optional (see V6).

V2 — Repo path line exists:
- Immediately after `## Overview`, there must be:
  - `Repo path: <non-empty>`

V3 — No-pin phrasing:
- Must fail if it finds:
  - `Python version: No Python version pin detected.`

V4 — Venv snippet labeling:
- If venv snippet exists, require `(Generic suggestion)` within 3 lines above.

V5 — Command formatting:
- In command sections (Install/Run/Test/Lint), commands must be backticked:
  - `` `command` ``
- If a description exists, it must be parenthesized immediately after:
  - `` `command` (Description.) ``

V6 — Analyzer notes:
- If `## Analyzer notes` exists, it must contain at least one non-empty bullet line.
- Fail if “(empty)” or blank notes section.

V7 — Install policy guard:
- Fail if ONBOARDING contains more than one `pip install -r` line.
  (Prevents invented Connexion-style multi-installs until we have explicit MCP-provided installs.)

V8 — Provenance hidden (standard mode):
- In standard runs with `SHOW_PROVENANCE=false`, fail if ONBOARDING contains:
  - `source:`
  - `evidence:`
(Allow override flag later if needed, e.g. `--allow-provenance`.)

**Acceptance**
- Validator is invoked for each repo output and fails runs when any V-rule is violated.
- Validator output clearly reports:
  - rule id (V1–V8)
  - line number/section
  - failure reason

**Tests (must be added)**
Add `tests/test_onboarding_validator.py` with string-based unit tests:
- One fully valid sample passes
- Each rule has at least one failing sample that asserts correct error id:
  - missing heading (V1)
  - missing repo path (V2)
  - forbidden “Python version: No Python…” (V3)
  - unlabeled venv snippet (V4)
  - unbackticked command / missing parentheses (V5)
  - empty analyzer notes section (V6)
  - multiple `pip install -r` lines (V7)
  - presence of `source:` when provenance is hidden (V8)

---

## Issue #57 — UX: Install dependencies policy (make install first)

**Title:** UX: Install dependencies policy — prefer `make install`; otherwise minimal generic pip

**Labels:** phase6, ux

**Context**
Install output can become noisy or misleading (e.g., Connexion invented multiple `pip install -r` lines). We need a stable, minimal policy.

**Rules (must be enforced in B-prompt and by validator)**
1) If `make install` exists in MCP command outputs:
- Install dependencies section must include:
  - `` `make install` ``
- It must not include generic pip commands (`pip install -r …`, `pip install -e .`) unless explicitly detected/derived by MCP output (default: omit).

2) If `make install` does not exist:
- Allow at most one `pip install -r …` line (generic) and keep it minimal.
- Do not generate multiple `pip install -r <nested requirements>` commands just because files exist.

**Examples**
- Makefile repo with install:
  - `` `make install` ``
- Simple pip repo:
  - `` `pip install -r requirements.txt` `` (Generic suggestion)

**Acceptance**
- Connexion-style output no longer invents multiple `pip install -r` commands.
- Makefile repos prefer `make install` when present.

**Tests**
- Validator Rule V7 enforces “max 1 pip install -r”.
- Add a validator test case where ONBOARDING contains 2+ pip install -r lines → must fail V7.

---

## Priority Summary

### High Priority (Critical) 🔴
1. Issue #10: Use tomllib for pyproject.toml accuracy ✅
2. Issue #53: BUG: Reject version ranges as pins 🆕
3. Issue #56: TOOLING: Epic Validator 🆕
4. Issue #32: Modularize Analysis Logic ✅
5. Issue #33: Enable Strict Mypy Mode ✅
6. Issue #40: Enhance security with symbolic link protection ✅

### Medium Priority (Important) 🟡
5. Issue #34: Standardize Error Logging ✅
6. Issue #35: Improve Unit Test Coverage ✅
7. Issue #36: Implement Comprehensive Error Scenario Tests ✅
8. Issue #38: Improve Server Error Responses ✅
10. Issue #42: Add Dependency Upper Bounds and Security Scanning ✅

### Low Priority (Nice to Have) 🟢
9. Issue #39: Performance Benchmarks ✅
11. Issue #41: Document Defaults in Prompt Text ✅
12. Issue #50: Binary/Asset Exclusion for Documentation ✅

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
