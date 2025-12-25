# PR: Classify Python Version Pins vs Ranges (#11)

## Goal
Improve the precision of Python version detection by distinguishing between exact pins (e.g., `==3.11.0`) and compatibility ranges (e.g., `>=3.11`). This prevents the analyzer from incorrectly claiming a project is "pinned" to a version when it only specifies a range.

## Related issues
- Closes #11

## Changes

- **Schema Update**: Added `pythonVersionPin` and `pythonVersionComments` to the `PythonInfo` Pydantic model.
- **Classification Utility**: Created `src/mcp_repo_onboarding/analysis/utils.py` with `classify_python_version()` which uses the `packaging` library to parse and categorize version specifiers.
- **Improved Reporting**:
    - **Exact Pins**: Reported in `pythonVersionPin`.
    - **Ranges**: Summarized in `pythonVersionComments` (e.g., "Requires Python >=3.11").
- **Integration**: Updated `_infer_python_environment` in `core.py` to process all detected hints (from workflows and `pyproject.toml`) through the classification logic.

## Verification

### Automated Tests
- Ran `uv run pytest tests/test_version_classification.py`.
- **Unit Tests**: Verified correct classification for pins, bounds, compatibility ranges (`~=`), and implicit versions.
- **Integration Tests**: Verified that `analyze_repo` correctly populates the schema fields using a real fixture.

### Manual Verification
- Verified that `mypy src/` passes with no issues in the modified files.
- Verified that `ruff` formatting and linting are consistent.
