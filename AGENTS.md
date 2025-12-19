# AGENTS.md — Agent & Copilot Instructions

## Project Identity
- **Name:** `mcp-repo-onboarding`
- **Language:** Python 3.11+
- **Manager:** `uv`
- **Architecture:** FastMCP (Server), Pydantic (Schema), Pytest (Testing).

## ⚠️ CRITICAL: TDD Required

**ALL code changes MUST follow Test-Driven Development:**

1.  **Write failing test FIRST** in `tests/`.
2.  **Run test to confirm failure** (`uv run pytest`).
3.  **Implement the fix** in `src/`.
4.  **Run test to confirm pass** (`uv run pytest`).

**NO EXCEPTIONS.** Do not write logic without a red test first.

## Build & Run Commands
- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server (Local):** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`

## File Structure
- `src/mcp_repo_onboarding/` -> Source code.
- `tests/` -> Pytest tests and fixtures.
- `tests/fixtures/` -> **READ-ONLY** test data copied from legacy repo.

## Code Style
- Use **Type Hints** everywhere.
- Use **Pydantic** for all data structures (do not use raw dicts for API outputs).
- Use `pathlib` for all file paths.
