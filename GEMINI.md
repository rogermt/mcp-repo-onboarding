## Current Status
- **Phase 7 (Domain Specialization):** COMPLETE (Notebook detection, Prompt/Tool UX).
- **Phase 8 (Refinement):** ACTIVE (Determinism, Maintainability, Scaffold).
- **Validation Authority:** `scripts/validate_onboarding.py` is the source of truth.

## Output Verification
...
## Stable API / naming (must not drift)

Repo/package/binary: `mcp-repo-onboarding`
Default onboarding file: `ONBOARDING.md`

MCP tool names are a stable API and must not change:
- `ping`
- `analyze_repo`
- `get_run_and_test_commands`
- `read_onboarding`
- `write_onboarding`
- `get_onboarding_template` (New: Returns authoritative prompt)

MCP prompts:
- `generate_onboarding` (New: Slash command /generate_onboarding)

*ALL code changes MUST follow Test-Driven Development:**
0.  **submit plan** overwrite /home/rogermt/mcp-repo-onboarding/docs/development/plan.md
1.  **Write failing test FIRST** in `tests/`.
2.  **Run test to confirm failure** (`uv run pytest`).
3.  **Implement the fix** in `src/`.
4.  **Run test to confirm pass** (`uv run pytest`).

see /home/rogermt/mcp-repo-onboarding/docs/design/SOFTWARE_DESIGN_GUIDE.md

## Key Phase 6 Artifacts (Reference)
- **Validator:** `scripts/validate_onboarding.py` (Run this to verify `ONBOARDING.md` compliance).
- **Requirements:** `docs/development/REQUIREMENTS.md` (Updated for Python-only scope & infrastructure).
- **Prompt Contract:** `docs/evaluation/B-prompt.txt` (The prompt template that must be satisfied).
- **Ignore Logic:** `docs/design/ignore-handling.md` (Docs for `IgnoreMatcher`).
- **Phase 7 Log:** `docs/development/DEV Phase 7.md` (Current work log).

## Build & Run (uv required)

This project uses `uv` for dependency management.

- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server:** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`

### Setup for Gemini-Cli
- **Create Directory**

```bash
mkdir .gemini
```

- **Create JSON File**

Create a file named `settings.json` inside the `.gemini` directory with the following content:

```json
{
  "mcpServers": {
    "repo-onboarding": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/rogermt/mcp-repo-onboarding",
        "run",
        "mcp-repo-onboarding"
      ],
      "env": {
        "REPO_ROOT": "/home/rogermt/Paper2Code"
      }
    }
  }
}
```

## Architecture
- **Framework:** `mcp` (Official Python SDK), `FastMCP`.
- **Validation:** `pydantic`.
- **Ignore Handling:** [pathspec](/home/rogermt/mcp-repo-onboarding/docs/design/ignore-handling.md)
- **Structure:**
    - `src/mcp_repo_onboarding/schema.py`: Pydantic models (API Contract).
    - `src/mcp_repo_onboarding/analysis.py`: Core logic (AST, File walking).
    - `src/mcp_repo_onboarding/server.py`: Tool wiring.

## Safety Invariants
- **NEVER EVER commit directly to the `master` branch.** All work MUST happen in a feature branch.
- No code execution (no `subprocess.run` on user code).
- All file paths sandboxed to `REPO_ROOT` using `pathlib.Path.resolve()`.
- The server does **not** generate prose. Gemini generates `ONBOARDING.md` content and passes it to `write_onboarding`.
- **CRITICAL:** Do NOT commit or push any code changes until the user has manually run and verified evaluations (due to rate limit constraints and validation requirements).

latest critical issues: /home/rogermt/mcp-repo-onboarding/docs/development/github_issues.md
