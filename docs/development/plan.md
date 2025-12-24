# Issue #10: Use tomllib to improve pyproject.toml signal accuracy

## Goal Description
Improve the accuracy of Python environment detection by parsing `pyproject.toml` using the standard library's `tomllib`. This enables extracting version constraints, build systems, and package manager configurations directly and reliably.

## Proposed Changes

### [Component Name] Analysis Package

#### [MODIFY] [extractors.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/extractors.py)
- Create `extract_pyproject_metadata(repo_root: Path, pyproject_path: str) -> dict[str, Any]` function.
- Parse `pyproject.toml` using `tomllib`.
- Extract `project.requires-python` and add to `pythonVersionHints`.
- Detect package managers from `tool.*` keys (poetry, hatch, pdm, flit).
- Detect build backend from `build-system`.

#### [MODIFY] [core.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/core.py)
- Update `_infer_python_environment` to call `extract_pyproject_metadata`.
- Use the extracted metadata to populate the `PythonInfo` object.

## Verification Plan

### Automated Tests
- Create a new fixture: `tests/fixtures/pyproject-rich/`.
- Add test file `tests/test_pyproject_parsing.py`.
- Verify:
    - Accurate `pythonVersionHints` when `requires-python` is present.
    - Correct `packageManagers` detection (e.g., Poetry, Hatch).
    - Robustness against malformed TOML files.
- Run `uv run pytest`.

### Manual Verification
- Verify the output of `analyze_repo` on the new fixture.
