# Contributing to mcp-repo-onboarding

Thanks for your interest in contributing!

This project aims to be a **practical MCP server for Python repos**, focused on:

- Environment & dependencies
- Run / test / lint / format commands
- Light hints about frameworks & structure

It is **not** trying to be a full code understanding or architecture tool.

---

## Ways to contribute

- **Bug reports**: incorrect analysis, crashes, broken MCP behavior.
- **Heuristics improvements**: better detection of Python tooling, tests, and commands.
- **Docs**: clarifying README, examples, or onboarding guidance.
- **New fixtures / tests**: to cover more real-world repo shapes.

For anything beyond a trivial fix, please open an issue first.

---

## Project scope & principles

- Python‑first:
  - Focuses on Python application and library repos.
- Practical onboarding:
  - Env setup, deps, run, test, lint/format.
- Static, local analysis:
  - No code execution.
  - No network access.
- Neutral about policy:
  - We don’t enforce or infer org/team rules (pre‑commit, CI, etc.).
  - We describe what’s there; Gemini + user context decide what it means.

If a feature feels like “DeepWiki” or “org policy engine”, it’s probably out of scope.

---

## Development setup

### 1. Clone and install

```bash
git clone https://github.com/<your-username>/mcp-repo-onboarding.git
cd mcp-repo-onboarding
uv sync
```

### 2. Build and test

```bash
uv run pytest
```

Tests use [pytest](https://docs.pytest.org/). We rely on fixtures under `tests/fixtures` to simulate different repo types.

---

## Repository structure (high level)

- `src/mcp_repo_onboarding/schema.py` – Pydantic models (`RepoAnalysis`, `CommandInfo`, etc.).
- `src/mcp_repo_onboarding/analysis/` – Python repo analysis package (core logic).
- `src/mcp_repo_onboarding/onboarding.py` – ONBOARDING.md read/write operations.
- `src/mcp_repo_onboarding/server.py` – FastMCP server wiring and tool implementations.
- `tests` – unit and integration tests, plus repo fixtures.

---

## Coding guidelines

- **Python**:
  - Use **Type Hints** everywhere.
  - Use **Pydantic** for all data structures (do not use raw dicts for API outputs).
  - Use `pathlib` for all file paths.
- **Functional core, imperative shell**:
  - Keep analysis logic as pure as possible.
  - Isolate I/O and env access in small helpers.
- **Tests (TDD Required)**:
  - Add/update tests for any heuristic change.
  - For new repo patterns, add a fixture under `tests/fixtures` and a pytest integration test.
  - **Write failing test FIRST** before implementing logic.

---

## Opening issues

Use the issue templates under `.github/ISSUE_TEMPLATE` if available.

In general, include:

- What you expected vs what you saw.
- A sample repo or a minimal fixture structure.
- The `RepoAnalysis` or tool output if possible.

If you’re proposing a new feature:

- Explain how it improves onboarding (env/deps/run/test).
- Confirm it stays within the project scope (no deep architecture or policy inference).

---

## Pull requests

1. **Discuss first**: open an issue for design/API/behavior changes.
2. **Keep PRs focused**:
   - One feature or bugfix per PR where possible.
3. **Tests**:
   - Ensure `uv run pytest` passes.
   - Add/update tests for new behavior.
4. **Style**:
   - Follow PEP 8 and use `ruff` for linting/formatting.
   - Run `uv run ruff check .` before submitting.

Please include a short summary in the PR description and link the relevant issue (e.g. “Fixes #12”).

---

## MCP & Gemini testing

If you change MCP tools or analysis, it’s helpful to also test via Gemini:

- In a Python repo:
  - Configure `.gemini/settings.json` with `mcpServers.repo-onboarding`.
  - Run `gemini mcp list` to ensure the server connects.
  - Use prompts to call `analyze_repo`, `get_run_and_test_commands`, etc.

This ensures your changes behave correctly when driven by Gemini Pro models.
