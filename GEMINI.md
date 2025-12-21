## Runtime responsibilities (avoid confusion)

- **Gemini CLI** is the runtime agent that calls MCP tools (via `mcpServers`).
- This MCP server only performs **static analysis + safe local file I/O**.
- The server does **not** generate prose. Gemini generates `ONBOARDING.md` content and passes it to `write_onboarding`.

## Stable API / naming (must not drift)

Repo/package/binary: `mcp-repo-onboarding`  
Default onboarding file: `ONBOARDING.md`

MCP tool names are a stable API and must not change:
- `ping`
- `analyze_repo`
- `get_run_and_test_commands`
- `read_onboarding`
- `write_onboarding`

*ALL code changes MUST follow Test-Driven Development:**
0.  **submit plan** overwrite /home/rogermt/mcp-repo-onboarding/docs/development/plan.md
1.  **Write failing test FIRST** in `tests/`.
2.  **Run test to confirm failure** (`uv run pytest`).
3.  **Implement the fix** in `src/`.
4.  **Run test to confirm pass** (`uv run pytest`).

see /home/rogermt/mcp-repo-onboarding/docs/design/SOFTWARE_DESIGN_GUIDE.md





## Build & Run (uv required)

This project uses `uv` for dependency management.

- **Sync Dependencies:** `uv sync`
- **Run Tests:** `uv run pytest`
- **Run Server:** `uv run mcp-repo-onboarding`
- **Lint/Format:** `uv run ruff check .`

### Setup for Gemini-Cli
- **Create Directory**

```bash
mkdir .gemnini
```

- **Create JSON File**

Create a file named `settings.json` inside the `.gemnini` directory with the following content:

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
- **Ignore Hndling:** [pathspec](/home/rogermt/mcp-repo-onboarding/docs/design/ignore-handling.md)
- **Structure:**
    - `src/mcp_repo_onboarding/schema.py`: Pydantic models (API Contract).
    - `src/mcp_repo_onboarding/analysis.py`: Core logic (AST, File walking).
    - `src/mcp_repo_onboarding/server.py`: Tool wiring.

## Safety Invariants
- No code execution (no `subprocess.run` on user code).
- All file paths sandboxed to `REPO_ROOT` using `pathlib.Path.resolve()`.
- The server does **not** generate prose. Gemini generates `ONBOARDING.md` content and passes it to `write_onboarding`.

