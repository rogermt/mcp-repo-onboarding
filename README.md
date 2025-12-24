# mcp-repo-onboarding

An **MCP server** for **Gemini CLI** that analyzes a local **Python** repository and helps you generate and maintain a practical `ONBOARDING.md`:

- How to set up the environment
- How to install dependencies
- How to run tests
- How to run the app / dev entrypoints (where detectable)

The server provides **structured JSON about the repo**; **Gemini CLI** turns that into human-readable onboarding docs.

Important clarity:
- **Gemini CLI is the runtime agent that calls MCP tools** (via `mcpServers`).
- This MCP server only performs **static analysis + safe local file I/O**.
- **The server does not generate prose**; Gemini generates `ONBOARDING.md` content and passes it to `write_onboarding`.

> Status: Python-first MVP implementation is complete (Phases 1–4).
> Phase 5 (validation/CI/distribution + A/B evaluation) is in progress.

---

## What this server does (and doesn’t do)

### Does

- Detect Python env / deps:
  - `requirements*.txt`
  - `pyproject.toml`
  - `Pipfile`
  - `environment.yml` / `environment.yaml`
  - `setup.cfg`, `setup.py`
- Detect tests and commands (best-effort):
  - Test layout: `tests/`, `test_*.py`, `*_test.py`
  - `pytest` / `unittest` via config and file patterns
  - `tox` / `nox` and basic commands
  - `Makefile` targets: `dev`, `test`, `lint`, `format`, etc.
  - (If present) scripts in `pyproject.toml`
- Report key files:
  - Docs: `README`, `CONTRIBUTING`, `docs/`
  - Config: `pyproject.toml`, `tox.ini`, `.pre-commit-config.yaml`, GitHub Actions workflows, etc.
- Manage `ONBOARDING.md`:
  - Read existing file
  - Write / overwrite / append, with optional backups

### Does *not* do

- Replace tools like DeepWiki or full architecture docs
- Infer deep architecture, data flows, or design rationale
- Decide org/team policies (e.g. whether pre-commit or CI is “required”)
- Execute project code or make network calls

This MCP server is **static analysis + file I/O** for a single repo root; Gemini provides the natural language onboarding on top.

---

## Ignore Rules

The analyzer applies ignore rules in this order:

- **Hard ignores** are always excluded (e.g., `.git/`, `node_modules/`, `.venv/`, `venv/`, `env/`, `__pycache__/`, `dist/`, `build/`, and anything under `site-packages/`).
- **Targeted signal files** (e.g., `pyproject.toml`, `requirements*.txt`, `tox.ini`, `Makefile`, `.github/workflows/*`) are still detected even if ignored, so onboarding signals remain reliable.
- **Broad scanning** (e.g., listing docs/config candidates) respects the repo’s `.gitignore` to reduce noise.

---

## MCP tools provided

These tool names are the stable API that Gemini should call:

| Tool | Purpose |
|------|---------|
| `ping` | sanity-check MCP wiring |
| `analyze_repo` | returns structured JSON (`RepoAnalysis`) about env/deps/run/test/layout/config signals |
| `get_run_and_test_commands` | convenience view: dev/test/build commands derived from analysis |
| `read_onboarding` | reads `ONBOARDING.md` (or a provided relative path) |
| `write_onboarding` | creates/overwrites/appends onboarding content (optional backup) |

---

## Installation & Usage

### Prerequisites
- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (Recommended package manager)

### 1. Build / Install
```bash
# Clone the repo
git clone https://github.com/rogermt/mcp-repo-onboarding.git
cd mcp-repo-onboarding

# Sync dependencies
uv sync
```
# 2. Start The Server
uv run mcp-repo-onboarding

---

## Configuring Gemini CLI

Gemini CLI reads settings from:

- User settings: `~/.gemini/settings.json`
- Project settings: `.gemini/settings.json` (recommended)

### Local dev config (recommended while developing)

In the Python repo you want to analyze:

```bash
cd /path/to/your/python-repo
mkdir -p .gemini
```

Create/edit `.gemini/settings.json`:

```json
{
  "mcpServers": {
    "repo-onboarding": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-repo-onboarding",
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


Notes:
- Replace `/absolute/path/to/.../dist/index.js` with the real path to your built server.
- `REPO_ROOT: "."` means “analyze the directory I’m running Gemini from”.
  - If you run `gemini` from the repo root (recommended), this works.
  - If you run `gemini` from somewhere else, set `REPO_ROOT` to an absolute path.

Verify Gemini sees the server:

```bash
gemini mcp list
```

Then start a chat:

```bash
gemini chat
```

### (Optional) npx config (post-publish or once bin packaging is ready)

Once published to npm with a `bin` entry:

```jsonc
{
  "mcpServers": {
    "repo-onboarding": {
      "command": "npx",
      "args": ["-y", "mcp-repo-onboarding"],
      "env": {
        "REPO_ROOT": "."
      }
    }
  }
}
```

---

## Using the MCP tools from Gemini

### Quick connectivity check (ping)

Prompt:

> Use the `repo-onboarding` MCP server.
> Call `ping` with `{}` and show me the raw result.

### Grounding rules (important)

To avoid drift:
- Do **not** claim a specific Python version unless `pythonVersionHints` contains one.
- Do **not** claim dev/test/build commands unless they appear in MCP output (`scripts`, `testSetup.commands`, or `get_run_and_test_commands`).
- Generic suggestions are allowed but must be labeled as generic.

### Analyze the repo

Prompt:

> Use the `repo-onboarding` MCP server.
> Call `analyze_repo` on this repo, then summarize (grounded in the tool output):
> – How to set up the Python environment
> – How to install dependencies
> – Where the tests live and how to run them
> – Any dev / lint / format commands you find
> Also quote the exact `pythonVersionHints` and `dependencyFiles` arrays before summarizing.

### Get commands only

Prompt:

> Use the `repo-onboarding` MCP server.
> Call `get_run_and_test_commands`.
> Quote the returned arrays, then tell me how to run dev (if any), how to run tests, and any build commands.

### Generate `ONBOARDING.md`

Prompt:

> Using the `repo-onboarding` MCP server, create an `ONBOARDING.md` for this repo.
> 1) Call `analyze_repo` and `get_run_and_test_commands`.
> 2) Then call `write_onboarding` with `mode: "create"` to write a guide that explains:
> – Environment setup
> – Installing dependencies
> – Running the app in dev (if detectable)
> – Running tests (if detectable)
> – Lint/format commands (if detectable)
> Make sure every claimed command is present in MCP tool output, or clearly labeled as a generic suggestion.

---

### Phase 6 – Python MCP Hardening & Signal Precision

**Summary**
Phase 6 focuses on tightening correctness, grounding, and signal prioritization in the Python MCP implementation following successful Phase‑5 validation. The goal is to eliminate contradictory output, reduce generic suggestions, and leverage Python‑native tooling for more precise static extraction—without increasing scope, runtime, or token usage.

**Goals**

* Zero contradictory analyzer output
* Strict adherence to Phase‑5 B‑prompt contract
* Prefer repo‑native commands over generic ones
* Improve Python version and dependency signal accuracy
* Keep MCP output mechanical and non‑prose

**Non‑Goals**

* No code execution
* No dependency resolution
* No deep architecture inference
* No TS/JS parity work

See [Phase 5 A/B Evaluation Prompts](./docs/evaluation/phase5-ab-prompts.md).

---

## Development

### Project layout

```text
src/
  domain/        # Type definitions and value objects
  infra/         # Repo root resolution, filesystem utilities
  analysis/      # Python repo analysis (env, deps, tests, commands)
  onboarding/    # ONBOARDING.md read/write logic
  mcp/           # MCP server wiring and tools (analyze_repo, etc.)
  dev/           # Dev-only scripts
test/
  fixtures/      # Sample repos used by tests
  analysis/      # Tests for analyzePythonRepo and heuristics
  onboarding/    # Tests for onboardingService
  mcp/           # Tests for MCP tools' execute() behavior
```

### Commands

```bash
uv run pytest
```

---

## Logging

Set:

- `MCP_REPO_ONBOARDING_LOG_LEVEL=error|warn|info|debug`

Logs must go to **stderr** (stdout is reserved for MCP protocol transport).

---

## Command Provenance

The analyzer captures the source of each command (e.g., `Makefile`, `tox.ini`, or a specific script path). By default, this "provenance" is hidden in the generated `ONBOARDING.md` for a cleaner experience.

For debugging or auditing, you can enable provenance rendering by setting `SHOW_PROVENANCE = true` in the `.gemini/B-prompt.txt` configuration block. When enabled, commands and configuration files will include a `(source: ...)` annotation.

## License

MIT.
