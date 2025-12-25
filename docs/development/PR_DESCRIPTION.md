# Title: Parse pyproject.toml using tomllib for robust signal accuracy (Issue #10)

## Summary

This PR replaces the fragile regex-based scanning of `pyproject.toml` with robust TOML parsing using the standard library's `tomllib`. This improvement ensures accurate extraction of Python version constraints, identification of package managers (Poetry, Hatch, PDM), and detection of build backends, significantly improving the reliability of the repository analysis.

## Related issues

- Closes #10

## Changes

- [x] Code changes in `src/mcp_repo_onboarding/analysis/extractors.py`
- [x] Tests added in `tests/test_pyproject_parsing.py`
- [x] New fixture added `tests/fixtures/pyproject-rich/pyproject.toml`

### Key Changes:

- **Robust TOML Parsing**: Switched from regex to `tomllib` for parsing `pyproject.toml`.
- **Accurate Metadata Extraction**: Now correctly identifies `requires-python`, build systems, and dependencies even in complex TOML files.
- **Package Manager Detection**: improved logic to detect Poetry, Hatch, PDM, and Flit.
- **Error Handling**: Graceful handling of malformed TOML files.

## How to test

Verify the parsing logic using the new test suite:

```bash
# Run the dedicated pyproject parsing tests
uv run pytest tests/test_pyproject_parsing.py

# Verify the full suite remains stable
uv run pytest
```

## Checklist

- [x] I’ve read the scope and non‑goals in the README/design docs.
- [x] My changes stay within the project’s responsibilities (env/deps/run/test).
- [x] `uv run pytest` passes locally.
- [x] I’ve added or updated tests for any new behavior.
