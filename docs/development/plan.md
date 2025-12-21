# Phase 6: Ignore Handling & Correctness

## Story 6-01 — IgnoreMatcher infrastructure + fixtures (pathspec, no git execution)

**Title:** Phase 6: Implement IgnoreMatcher (safety + repo ignore via pathspec) with fixtures and deterministic matching

**Status:** Completed

**Labels:** phase6, infra, enhancement, tests, correctness

### User Story
As a maintainer, I want a dedicated IgnoreMatcher component that answers “should this path be ignored?” using safety ignores plus repo-local ignore rules (.gitignore and optional .git/info/exclude) via pathspec, so that ignore behavior is deterministic, fast, and does not require executing git.

### Scope
*   [x] Create the IgnoreMatcher module/class.
*   [x] Load/compile ignore rules once per run.
*   [x] Provide should_ignore() / should_descend() APIs.
*   [x] Add fixture repos and unit tests for ignore behavior.

### Precedence (must implement exactly inside IgnoreMatcher)
1.  **Safety ignores** (always enforced, never overridable)
2.  **Repo ignore rules** (pathspec, repo-root .gitignore + optional .git/info/exclude)
    *   (Integration of “targeted signals not blocked” is Story 6-02.)

### Acceptance Criteria
*   [x] **Safety ignores** always exclude their subtrees (e.g., `.git/`, `.venv/`, `venv/`, `__pycache__/`, `node_modules/`, any `site-packages/`, `dist/`, `build/`, `.pytest_cache/`, `.mypy_cache/`, `.coverage`).
*   [x] **Repo ignore rules**:
    *   read from repo root `.gitignore` and optional `.git/info/exclude`
    *   use GitWildMatchPattern semantics
    *   paths are normalized to repo-root-relative POSIX style
    *   directory checks treat directories with a trailing `/`
*   [x] **No git CLI usage** and no global/user gitignore sources.
*   [x] **Deterministic behavior**:
    *   given the same inputs, ignore results are stable.
*   [x] **Failure handling**:
    *   missing/unreadable ignore files → treat as empty repo ignore rules (safety only)
    *   invalid patterns → skipped (non-fatal)
*   [x] **No filesystem mutation**.

### Test Plan (fixtures required)
Create fixture repos under `tests/fixtures/ignore_handling/` and assert IgnoreMatcher decisions:

*   [x] `repo_no_gitignore`
    *   includes `.venv/`, `build/`
    *   safety ignores exclude both.
*   [x] `repo_basic_gitignore`
    *   `.gitignore` ignores `build/` and `.env`
    *   verify those are ignored; docs and requirements included.
*   [x] `repo_safety_override`
    *   `.gitignore` contains `!.venv/`
    *   `.venv/` remains ignored (safety wins).
*   [x] `repo_nested_ignores_root_only`
    *   `.gitignore` contains `docs/_build/`
    *   deep paths under that tree are ignored.
*   [x] `repo_env_path_false_positive`
    *   includes `local/py3/lib/python3.13/site-packages/...`
    *   ensure `site-packages` subtree is ignored via safety ignores.

### Definition of Done
*   [x] All fixtures/tests pass under `npm run preflight` (or your Python equivalent test command).
*   [x] IgnoreMatcher can be reused across traversal without rebuilding.