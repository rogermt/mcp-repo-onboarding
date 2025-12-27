# Phase 7: Technical Implementation Plan (Issue #61)

## 🛡️ Protected Files (Do Not Touch)
- `docs/evaluation/validate_onboarding.py`
- `docs/design/EXTRACT_OUTPUT_RULES.md`

---

## 1. Notebook Hygiene Detection (P7-02 / #61)
**Goal**: Neutral, static detection of notebook stripping tools in pre-commit configs.

### 1.1 TDD: Failing Tests
- **Location**: `tests/test_notebook_hygiene.py`
- **Scenarios**:
    - `.pre-commit-config.yaml` containing `nbstripout` triggers override description.
    - `.pre-commit-config.yaml` without markers uses standard generic description.
    - Pathological cases (missing file, oversized file > 256KB) return False (generic).

### 1.2 Scanner Helper
- **Location**: `src/mcp_repo_onboarding/analysis/notebook_hygiene.py`
- **Logic**:
    - Verify path is under root.
    - Check file size (< 256KB).
    - Case-insensitive string search for: `nbstripout`, `nb-clean`, `jupyter-notebook-cleanup`.

### 1.3 Core Integration
- **Location**: `src/mcp_repo_onboarding/analysis/core.py`
- **Action**:
    - Update `_categorize_files` to accept `root: Path`.
    - In `_categorize_files`, if file is `.pre-commit-config.yaml/.yml`, call helper and apply description override if True.

---

## Verification Plan
1. **Red Test**: Confirm `uv run pytest tests/test_notebook_hygiene.py` fails.
2. **Implementation**: Add helper and patch `core.py`.
3. **Green Test**: Confirm all tests pass.
4. **Linting**: `uv run ruff check .` and `uv run mypy .`.
