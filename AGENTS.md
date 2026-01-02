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

## ⚠️ CRITICAL: Trust the Plan and Documentation

**FOLLOW THE PLAN.** Do NOT deviate or second-guess:
- If AGENTS.md or approved plan says master is clean → **trust it. Do not "check" old commits.**
- If a plan specifies test structure → **follow it exactly. Do not restore old commits thinking things are broken.**
- **Always read the current documentation first.** Do not assume state based on suspicion.
- If status is documented (e.g., "Phase 7 COMPLETE"), do not undo or redo it.
- **Fetch from origin before making assumptions about branch state.**

**DO NOT:** Pull old commits, revert clean work, or reorganize things that are already correct just because you're unsure.

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

### PR2: PENDING
**Next Steps:**
1. Create `feat/issue-87-pr2` from `feat/issue-87-pr1`
2. Update production imports across `src/` and `tests/` to use canonical module
3. Create optional v2 compat shim (if needed)
4. Update existing v2 tests (if needed)
5. Run full test suite
6. Commit, push, ready for merge

**Reference Plan:** See `/scratch/blueprint_approved_pln.md` (section 6, File Checklist)

**Test Directory Structure:** STRICT enforcement
- ✓ Tests ONLY in subdirectories: `tests/analysis/`, `tests/integration/`, `tests/onboarding/`, `tests/server/`
- ✗ Never in root `tests/` directory
- ✓ Subdirectories created as needed during PR2
