# AGENTS.md — Agent & Copilot Instructions

## Current Status
- **Phase 7 (Domain Specialization):** COMPLETE (Notebook detection, Prompt/Tool UX).
- **Phase 8 (Refinement):** ACTIVE (Determinism, Maintainability, Scaffold).
- **Validation Authority:** `scripts/validate_onboarding.py` is the source of truth for all code generation.

## Output Verification
When verifying output, ensure no files from `tests/fixtures/` appear in the lists. Refer to [EXTRACT_OUTPUT_RULES.md](./docs/design/EXTRACT_OUTPUT_RULES.md) for the priority order.

## Project Identity
- **Name:** `mcp-repo-onboarding`
- **Language:** Python 3.11+ (**100% Python scope**)
- **Manager:** `uv`
- **Architecture:** FastMCP (Server), Pydantic (Schema), Pytest (Testing).
- **Stable API (Tools):** `ping`, `analyze_repo`, `get_run_and_test_commands`, `read_onboarding`, `write_onboarding`, `get_onboarding_template`.
- **Stable API (Prompts):** `generate_onboarding` (Slash command: `/generate_onboarding`).

## ⚠️ CRITICAL: TDD Required

**ALL code changes MUST follow Test-Driven Development:**

1.  **NEVER commit directly to the `master` branch.** All changes must be verified in a feature branch first.
2.  **Write failing test FIRST** in `tests/`.
2.  **Run test to confirm failure** (`uv run pytest`).
3.  **Implement the fix** in `src/`.
4.  **Run test to confirm pass** (`uv run pytest`).

**NO EXCEPTIONS.** Do not write logic without a red test first.

## Key Project Artifacts
- **Validator:** `scripts/validate_onboarding.py` (Must be used to verify any generated `ONBOARDING.md`).
- **Requirements:** `docs/development/REQUIREMENTS.md` (The canonical spec).
- **Prompt Contract:** `docs/evaluation/B-prompt.txt` (Required prompt for compliant output).
- **Ignore Design:** `docs/design/ignore-handling.md` (Design for the `IgnoreMatcher` system).

## Build & Run Commands
- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server (Local):** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`
- **Type Check:** `uv run mypy src/mcp_repo_onboarding --ignore-missing-imports`

## ⚠️ MANDATORY: Run Linters After Every Edit

**After EVERY edit to a `.py` file, you MUST run:**

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src/mcp_repo_onboarding --ignore-missing-imports
```

**Do NOT commit or push until all three commands pass with zero errors.**

## File Structure
- `src/mcp_repo_onboarding/` -> Source code.
- `tests/` -> Pytest tests and fixtures.
- `tests/fixtures/` -> **READ-ONLY** test data.

## Code Style
- Use **Type Hints** everywhere.
- Use **Pydantic** for all data structures (do not use raw dicts for API outputs).
- Use `pathlib` for all file paths.

---

## Issue #87 Status — Blueprint Refactoring (Registry Engine)

### PR1: COMPLETE ✓
**Branch:** `feat/issue-87-pr1` (commit `80f09b3`)
**Status:** Tests GREEN, linters pass, pushed to remote.

**Deliverables:**
- `onboarding_blueprint_reference.py` — frozen v2 snapshot (baseline for equivalence tests)
- `onboarding_blueprint_engine/` package — registry-driven compilation engine
  - `context.py` — minimal Context (matches v2 exactly)
  - `specs.py` — SectionSpec data class
  - `registry.py` — all section builders (verbatim from v2) + registry list in order
  - `compile.py` — blueprint compiler and renderer (verbatim from v2)
  - `__init__.py` — engine API exports
- `onboarding_blueprint.py` (canonical) — versionless entrypoint, engine-backed
- `tests/onboarding/test_blueprint_engine_equivalence.py` — 6 synthetic equivalence tests
- `tests/onboarding/test_onboarding_blueprint_canonical_module.py` — 5 canonical module tests

**Test Results:** 11/11 passed
**Engine Output:** Byte-for-byte identical to reference v2 for all test cases.

### PR2: COMPLETE ✓
**Branch:** `feat/issue-87-pr2` (commit `57bff2e`)
**Status:** Tests GREEN, linters pass, ready for merge.

**Deliverables:**
- `onboarding_blueprint_legacy.py` — frozen v1 implementation (preserved for backward compatibility)
- Updated `onboarding_blueprint.py` — canonical module re-exports v2 from engine + v1 from legacy
- Updated `src/mcp_repo_onboarding/server.py` — production imports from canonical module
- Updated `tests/onboarding/test_onboarding_blueprint_v2.py` — import from canonical module
- Updated `pyproject.toml` — added `onboarding_blueprint_legacy.py` to ruff per-file-ignores

**Test Results:** 207 passed, 1 skipped
**All Linters:** ✓ ruff check, ✓ ruff format, ✓ mypy

### PR3: PENDING EVALUATION ⏳
**Branch:** `feat/issue-87-pr3` (commit `d72bcf3`)
**Status:** Tests GREEN, linters pass. **Awaiting evaluation (5/5) before merge.**

**Deliverables:**
- DELETED `onboarding_blueprint_legacy.py` (v1 preserved, no longer exported from core)
- DELETED `onboarding_blueprint_reference.py` (frozen v2 baseline, equivalence gate removed)
- DELETED `onboarding_blueprint_v2.py` (compatibility shim no longer needed)
- Updated `onboarding_blueprint.py` — canonical module now v2 engine-backed only (no v1)
- Updated `onboarding_blueprint_engine/compile.py` — function renamed `compile_blueprint` (was `compile_blueprint_v2`)
- Updated `server.py` — output key is now `onboarding_blueprint` (not `_v1` or `_v2`)
- Updated `analysis/__init__.py` — removed blueprint exports entirely
- Replaced equivalence tests with direct behavior tests (23 test cases)
- Updated server test to verify new output key
- Format string remains `"onboarding_blueprint_v2"` (API contract preserved)

**Test Results:** 197 passed
**All Linters:** ✓ ruff check, ✓ ruff format, ✓ mypy
**Files Deleted:** 8 (legacy, reference, v2 shim, 4 old tests)
**Net Change:** -2124 lines (deleted bloat), +433 lines (new tests, canonical code)

**Acceptance Criteria (Final Gate):**
- [ ] Evaluation tests: 5/5 passing (run `scripts/validate_onboarding.py`)
- [ ] No MCP output drift
- [ ] Format string contract preserved (`"onboarding_blueprint_v2"`)
- [ ] Output key is `onboarding_blueprint` (not `_v1` or `_v2`)
- [ ] All files with `_v1`, `_v2`, `_legacy`, `_reference` deleted from `src/`
- [ ] All unit tests pass (197/197)
- [ ] All linters pass
- [ ] Ready for merge to `master`
