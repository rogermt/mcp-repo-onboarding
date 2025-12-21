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

## Story 6-02 — Integrate IgnoreMatcher into analyze_repo traversal (ignore before classification + truncation)
**Title:** Phase 6: Apply IgnoreMatcher during analyze_repo traversal (ignore before classification, caps, and truncation)

**Labels:** phase6, enhancement, analysis, correctness, performance

### User Story
As a maintainer, I want analyze_repo to apply ignore rules during traversal (before classification and truncation math), so that ignored files/dirs never affect RepoAnalysis output, ordering, caps, or truncation notes.

### Scope
*   Use IgnoreMatcher from Story 6-01 during broad filesystem walks.
*   Ensure pruning (no descending into ignored dirs).
*   Ensure ignored paths never reach classification.
*   Ensure caps and “total counts” reflect post-ignore results only.
*   Ensure determinism (stable ordering) in output.

### Precedence (must match contract)
1.  **Safety ignores** (always enforced)
2.  **Targeted signal discovery** is not blocked by repo ignore rules:
    *   Known “signal files” must still be detected via explicit checks even if ignored by .gitignore.
    *   Safety ignores still apply.
3.  **Repo ignore rules** (pathspec) apply to broad scans only.

### Acceptance Criteria
*   **Ignored paths**:
    *   do not appear anywhere in RepoAnalysis
    *   do not contribute to section totals
    *   do not influence caps or truncation notes
*   **Truncation notes** reflect post-ignore totals (e.g., “docs list truncated to 10 entries (total=181)” uses totals after ignore).
*   **Deterministic ordering**:
    *   traversal ordering is stable (sort dirs/files)
    *   output lists are stable-sorted before truncation
*   **Targeted signals** remain detectable even if ignored by .gitignore:
    *   example signals: pyproject.toml, requirements*.txt, tox.ini, noxfile.py, setup.py, setup.cfg, Makefile, .pre-commit-config.yaml, .github/workflows/*.yml
*   No git CLI execution and no global/user ignore sources.

### Test Plan
*   Reuse the fixture repos from Story 6-01 and run analyze_repo end-to-end.
*   Assert:
    *   ignored content does not appear in docs, configurationFiles, dependency lists, or language counts (where applicable)
    *   truncation totals/caps exclude ignored files
    *   RepoAnalysis output remains stable across runs

### Definition of Done
*   End-to-end tests prove ignore is applied before classification and truncation math.
*   No regressions in existing repo-analysis fixtures.
*   Output determinism confirmed by stable ordering assertions.