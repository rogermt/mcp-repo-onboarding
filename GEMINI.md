# GEMINI.md — Contribution & Execution Rules (Python Version)

This file defines how to work in this repo.

## Build & Run (uv required)

This project uses `uv` for dependency management.

- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server:** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`

## Architecture
- **Framework:** `mcp` (Official Python SDK), `FastMCP`.
- **Validation:** `pydantic`.
- **Structure:**
    - `src/mcp_repo_onboarding/schema.py`: Pydantic models (API Contract).
    - `src/mcp_repo_onboarding/analysis.py`: Core logic (AST, File walking).
    - `src/mcp_repo_onboarding/server.py`: Tool wiring.

## Safety Invariants
- No code execution (no `subprocess.run` on user code).
- All file paths sandboxed to `REPO_ROOT` using `pathlib.Path.resolve()`.
