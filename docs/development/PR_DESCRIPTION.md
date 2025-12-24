# Title: Exclude Binary and Asset Files from Documentation (Issue #50)

## Summary

This PR implements a robust filtering system for the documentation analyzer to prevent non-human-readable files (images, PDFs, assets) from cluttering the documentation report and consuming capacity slots.

## Related issues

- Closes #50, #10

## Changes

- [x] Code changes in `src/...`
- [x] Tests added/updated in `test/...`
- [x] Docs updated (README/CONTRIBUTING/etc.)

### Key Changes:

- **Extension-Based Filtering**: Implemented a comprehensive denylist of 22+ binary and asset extensions (PNG, JPG, PDF, CSS, JS, etc.) in `config.py`.
- **pyproject.toml Parsing (Issue #10)**: Replaced regex-based scanning with robust TOML parsing using `tomllib` for accurate Python version and package manager detection.
- **Location-Specific Sensitivity**: Inside the `docs/` folder, the analyzer now strict-allows only `.md`, `.rst`, `.txt`, and `.adoc` formats.
- **Enhanced Heuristics**: Improved documentation prioritization—`getting_started` and `quickstart` are now prioritized (score 90), while `admin` guides are deprioritized (score 40).
- **Corrected Truncation Logic**: The truncation notes now report totals based *after* filtering, ensuring accurate counts for the user.

## How to test

Verify the filtering logic using the new test suite:

```bash
# Run the dedicated doc filtering tests
uv run pytest tests/test_doc_filtering.py

# Verify the full suite remains stable
uv run pytest
```

Tested with a new fixture `tests/fixtures/docs-with-binaries` containing various asset types.

## Checklist

- [x] I’ve read the scope and non‑goals in the README/design docs.
- [x] My changes stay within the project’s responsibilities (env/deps/run/test).
- [x] `uv run pytest` passes locally.
- [x] I’ve added or updated tests for any new behavior.
