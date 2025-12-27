# AGENTS.md — Agent & Copilot Instructions

## Current Status
- **Phase 6 (Hardening):** COMPLETE (5/5 validation pass).
- **Phase 7 (Domain Specialization):** ACTIVE.
- **Validation Authority:** `docs/evaluation/validate_onboarding.py` is the source of truth for all code generation.

## Output Verification
When verifying output, ensure no files from `tests/fixtures/` appear in the lists. Refer to [EXTRACT_OUTPUT_RULES.md](./docs/design/EXTRACT_OUTPUT_RULES.md) for the priority order.

## Project Identity
- **Name:** `mcp-repo-onboarding`
- **Language:** Python 3.11+ (**100% Python scope**)
- **Manager:** `uv`
- **Architecture:** FastMCP (Server), Pydantic (Schema), Pytest (Testing).

## ⚠️ CRITICAL: TDD Required

**ALL code changes MUST follow Test-Driven Development:**

1.  **Write failing test FIRST** in `tests/`.
2.  **Run test to confirm failure** (`uv run pytest`).
3.  **Implement the fix** in `src/`.
4.  **Run test to confirm pass** (`uv run pytest`).

**NO EXCEPTIONS.** Do not write logic without a red test first.

## Key Project Artifacts
- **Validator:** `docs/evaluation/validate_onboarding.py` (Must be used to verify any generated `ONBOARDING.md`).
- **Requirements:** `docs/development/REQUIREMENTS.md` (The canonical spec).
- **Prompt Contract:** `docs/evaluation/B-prompt.txt` (Required prompt for compliant output).
- **Ignore Design:** `docs/design/ignore-handling.md` (Design for the `IgnoreMatcher` system).

## Build & Run Commands
- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server (Local):** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`

## File Structure
- `src/mcp_repo_onboarding/` -> Source code.
- `tests/` -> Pytest tests and fixtures.
- `tests/fixtures/` -> **READ-ONLY** test data.

## Code Style
- Use **Type Hints** everywhere.
- Use **Pydantic** for all data structures (do not use raw dicts for API outputs).
- Use `pathlib` for all file paths.
