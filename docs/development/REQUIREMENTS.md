# mcp-repo-onboarding
**Requirements & Implementation Plan (Python‑First MCP Server for Gemini CLI)**

Canonical name (repo + python package): `mcp-repo-onboarding`

Scope: Focus on **Python repos** first (services, CLIs, libraries, research repos), with the primary value being a **high-signal grounded extractor** (commands + key setup signals) that reduces hallucinations and reduces token usage. Polyglot repos may be present but remain secondary until Python extraction is consistently high-signal.

---

## 0. Naming and Consistency Rules

To avoid drift across docs, code, and configs:

- **Repo / package name**: `mcp-repo-onboarding`
- **Binary name** (when using uv): `mcp-repo-onboarding`
- **Default onboarding file**: `ONBOARDING.md`
- **MCP tool names** (stable API):
  - `ping`
  - `analyze_repo`
  - `get_run_and_test_commands`
  - `read_onboarding`
  - `write_onboarding`

Note: The **Gemini CLI `mcpServers` key** (e.g. `"repo-onboarding"`) is user-configurable and is not part of this project’s API.

---

## 0.1 Phase 5 Pivot

Phase 5 pivots the product objective from “generate great ONBOARDING.md automatically” to:

1) Produce **high-signal, grounded extraction output** (commands + setup signals) that is safe and non-misleading.
2) Provide **token-saving** structured output for Gemini (measured in A/B evaluation).
3) Keep `ONBOARDING.md` read/write tools, but treat prose generation as optional and secondary to extractor quality.

This pivot is driven by A/B results: MCP mode saves tokens, but utility suffers when extraction is noisy (e.g., Makefile recipe internals), polluted by env/vendor directories (e.g., `site-packages`), or misses common patterns (e.g., `scripts/*.sh`).

---

## 1. Overview

### 1.1 Problem

For Python repos, new contributors repeatedly need to know:

- How do I set up a virtualenv?
- How do I install dependencies (pip / Poetry / Pipenv / Conda)?
- How do I run tests (pytest / unittest / tox / nox)?
- How do I run the app (Django / Flask / FastAPI / CLI)?
- How is it deployed (Docker / GitHub Actions / etc.)?

Maintainers rarely keep onboarding docs up to date as tooling or layout changes.

Additionally, LLM-only onboarding attempts tend to either (a) guess commands/versions or (b) burn tokens scanning files. We need a structured, grounded signal extractor that is compact enough to improve Gemini UX and reduce token usage.

### 1.2 Proposed Solution

Build an MCP server (for Gemini CLI) that:

- Analyzes a **local Python repo** and returns a **compact, structured signal summary**:
  - environment/dependency signals
  - high-signal run/test/lint/format command candidates
  - repo layout and notable entrypoints (lightweight)
  - docs/config pointers (capped)
- Manages `ONBOARDING.md` as an optional artifact:
  - read existing file
  - write/update with backups
- Enables Gemini to produce grounded onboarding **without reading the entire repo**, reducing hallucinations and token usage.

Division of responsibilities:

- MCP server does **static analysis + safe local file I/O** (no code execution, no network).
- Gemini (LLM) produces **natural language onboarding content**.

---

## 2. Target Users & Use Cases

### 2.1 Personas

1. **Python repo evaluator (token-saving extraction)**
   - Uses Gemini CLI + MCP to quickly get “how do I run/test/lint this?” without scanning the repo manually.
2. **Python project maintainer**
   - Wants high-quality onboarding with low maintenance burden.
3. **New contributor / new hire**
   - Wants reliable setup/run/test instructions grounded in repo signals.

### 2.2 Core Use Cases (Python-first)

1. **Extract high-signal commands and setup signals (token-saving)**
   - Flow:
     1. Gemini calls `analyze_repo` and `get_run_and_test_commands`.
     2. Gemini uses only the returned signals to answer “how do I run/test/lint this?”
   - Success criteria:
     - Commands are clean and human-facing (e.g., `make test`, `tox`, `bash scripts/run.sh`).
     - Output is compact and does not overwhelm Gemini UI.

2. **Create `ONBOARDING.md` from scratch (optional workflow)**
   - Flow:
     1. Gemini calls `analyze_repo` (and optionally `get_run_and_test_commands`).
     2. Gemini generates onboarding prose grounded in MCP output.
     3. Gemini calls `write_onboarding`.

3. **Update `ONBOARDING.md` after repo changes (optional workflow)**
   - Flow:
     1. Gemini calls `analyze_repo`.
     2. Gemini calls `read_onboarding`.
     3. Gemini updates relevant sections.
     4. Gemini calls `write_onboarding` (with backup).

---

## 3. Scope

### 3.1 In Scope (Python-first MVP)

- Environment setup signals (venv/Poetry/Pipenv/Conda detection, best-effort)
- Dependency file detection
- Test tooling signals (pytest/tox/nox best-effort)
- Command extraction (best-effort, but **high-signal** and **non-misleading**)
- Lightweight framework hints (Django/Flask/FastAPI/CLI) where safe
- Tooling/config presence detection (pre-commit, CI workflows, Dockerfiles, etc.)
- `ONBOARDING.md` read/write/update with backups (optional workflow)
- Detect common “research repo” entrypoints:
  - repo-root `scripts/*.sh` surfaced as runnable commands (existence-based)
- Noise control:
  - aggressive ignore patterns for env/vendor directories (e.g., `site-packages`)
  - cap large lists (`docs`, `configurationFiles`) to keep output usable

### 3.2 Out of Scope (MVP)

- Deep architecture discovery (data flows, rationale, full system explanation)
- Policy enforcement (pre-commit/CI detected, not judged)
- Executing repo code or shell commands; network access
- Remote knowledge sources (issues, wikis, external APIs)
- Exhaustive doc/config listing for large repos (we cap and summarize instead)

---

## 3.3 Definitions: docs vs configurationFiles vs dependencyFiles

These categories must not be mixed; they have different purposes.

- **dependencyFiles** (`RepoAnalysis.python.dependencyFiles`)
  - Dependency manifests and environment descriptors, e.g.:
    - `requirements*.txt`, `constraints*.txt`
    - `pyproject.toml` (when used for deps)
    - `Pipfile`, `environment.yml`
    - `setup.py`, `setup.cfg` (when they define install metadata)
- **configurationFiles** (`RepoAnalysis.configurationFiles`)
  - Project/automation config files, e.g.:
    - `Makefile`, `tox.ini`, `noxfile.py`
    - `.pre-commit-config.yaml`
    - `.github/workflows/*.yml`
    - Docker files and deployment configs
- **docs** (`RepoAnalysis.docs`)
  - Human-readable documentation artifacts, e.g.:
    - `README*`, `CONTRIBUTING*`
    - `docs/**` documentation pages
    - `notebooks/README*` and other doc entrypoints

---

## 3.4 Grounding Rules for LLM Output

To reduce model drift and avoid misleading output, Gemini responses must be grounded:

- **Python version**
  - Only claim a specific version if `python.pythonVersionHints` contains it.
  - If empty, say exactly: “No Python version pin detected.”
- **Commands**
  - Only claim a command if it appears in:
    - `RepoAnalysis.scripts.*`, or
    - `RepoAnalysis.testSetup.commands`, or
    - `get_run_and_test_commands` output.
  - Never present Makefile recipe internals as commands.
    - Prefer stable `make <target>` invocations.
  - Prefer detected/derived commands; avoid heuristics that guess tools.
- **Compatibility vs pin**
  - A pin is explicit (e.g., `.python-version`, `runtime.txt`, `requires-python`, CI pin).
  - Compatibility ranges (classifiers/CI matrices) must not be phrased as a pin unless the analyzer supports a separate field for compatibility.

---

## 4. Requirements

### 4.1 Functional Requirements

#### 4.1.1 Repo Root Handling

- Works on a single repo root.
- Root resolution order:
  1. `REPO_ROOT` env var (if provided)
  2. Current working directory (default)
- All file operations are sandboxed to this root:
  - Resolve paths relative to root
  - Validate they remain under root even with symlinks (use realpath checks)

#### 4.1.2 Python Repo Analysis (`analyze_repo`)

Input parameters:
- `path`: Optional sub-path within the repo to analyze.
- `maxFiles`: Optional safety cap on number of files to scan.

Notes:
- The analyzer must apply ignore rules consistently so env/vendor directories (including any `site-packages` paths) do not appear in output.

Output type (RepoAnalysis):
(See `src/mcp_repo_onboarding/schema.py` for full Pydantic models)

##### Output size / caps contract (Phase 5 pivot)
- `docs` is capped at **10** entries
- `configurationFiles` is capped at **15** entries
- When caps apply, add truncation messages to `notes`, e.g.:
  - “docs list truncated to 10 entries”
  - “configurationFiles list truncated to 15 entries”

#### 4.1.2.1 Makefile extraction rules (P0)
- If Makefile targets exist for common developer workflows (`test`, `lint`, `format`, `dev`, `run`, `start`, `check`, `install`), commands should be emitted as `make <target>`.
- Do not emit Makefile recipe lines as commands (anything containing Make variables like `$(`…`)` or line continuations).

#### 4.1.2.2 scripts directory entrypoints (P0)
- If repo root contains a `scripts/` directory with `*.sh`, emit command candidates such as `bash scripts/<file>.sh`.
- These commands are grounded solely in file existence; they must not imply correct args/env beyond existence.

#### 4.1.3 Read ONBOARDING.md (`read_onboarding`)

Input:
- `path`: Relative path to file (default `ONBOARDING.md`).

Behavior:
- Default path: `ONBOARDING.md` in repo root.
- If path provided, treat as relative to repo root.

#### 4.1.4 Write / Update ONBOARDING.md (`write_onboarding`)

Input:
- `content`: Markdown content to write.
- `path`: Relative path to file (default `ONBOARDING.md`).
- `mode`: `create`, `overwrite`, or `append`.
- `createBackup`: Whether to create a .bak file on overwrite.

Behavior:
- Default path: `ONBOARDING.md`.
- create: fail if file exists.
- overwrite: overwrite; create backup if enabled.
- append: append or create.

#### 4.1.5 Convenience Commands (`get_run_and_test_commands`)

Behavior:
- Derived from `analyze_repo`.
- Should be detected/derived from strong signals (tox/nox/Makefile targets/scripts directory).
- Avoid heuristics that guess tools.

---

### 4.2 Non‑Functional Requirements

#### 4.2.1 Performance
- For typical Python repos (< 5k files), `analyze_repo` should complete in ≤ 2 seconds.
- Avoid reading full file contents except small config files (with size caps).
- Prefer targeted discovery before broad walking.
- Default ignore patterns should exclude:
  - `.git/`, `.venv/`, `venv/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
  - `node_modules/`, `dist/`, `build/`
  - any path containing `site-packages`
  - recognizable repo-local env/vendor patterns (e.g., `local/**/site-packages/**`)

#### 4.2.2 Security / Safety
- No execution of repo code, shell scripts, or tasks.
- No network access.
- All paths must remain under `REPO_ROOT`, including symlink-escape protection.

#### 4.2.3 UX / Installability
- Python package name: `mcp-repo-onboarding`
- Binary: `mcp-repo-onboarding` (run via `uv run`)

Gemini CLI config example (uv-based):

```json
{
  "mcpServers": {
    "repo-onboarding": {
      "command": "uv",
      "args": ["run", "--project", "/path/to/mcp-repo-onboarding", "mcp-repo-onboarding"],
      "env": { "REPO_ROOT": "." }
    }
  }
}
```

#### 4.2.4 Logging & Diagnostics
- Logs must go to stderr (stdout reserved for MCP transport).

---

## 4.3 Signal Interpretation Guidelines

- Pre-commit configs
  - Detect `.pre-commit-config.yaml` and list under `configurationFiles` with type `pre-commit`.
  - Neutral descriptions only; no policy judgments.

- CI/CD and workflows
  - Detect and list workflows/configs, but do not attempt full pipeline explanation.

Goal: point developers in the right direction, not substitute for detailed process docs.

---

## 4.4 Hard Rule — Environment Setup Sections

- **No invented commands**
   - MCP must never emit environment setup instructions (e.g., `python -m venv .venv`, `pip install -r requirements.txt`) unless explicitly found in repository evidence.

- **Evidence sources (only these are allowed)**
   - Documentation files (`README*`, `CONTRIBUTING*`, `docs/**`)
   - Makefile targets
   - Tooling configs (`tox.ini`, `noxfile.py`, `pyproject.toml` with `[tool.poetry]` or `[tool.pipenv]`)
   - Scripts referenced in `scripts/*`

- **Default behavior**
   - If no evidence exists:
     ```
     No explicit environment setup instructions detected by the analyzer.
     ```
   - Section may be omitted if no instructions exist.

- **No heuristics or assumptions**
   - MCP may not guess based on Python detection, dependency files, or common practices.

---

## 4.5 Gitignore-aware scanning precedence

  - **Repo scanning** uses three layers of filtering, in this strict order:

    - **Hard ignores (always enforced):** The analyzer must always ignore known noise/env/vendor directories (e.g., `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `dist/`, `build/`, and any path containing `site-packages/`). Hard ignores are invariants and must not be overridden by ignore negations.

    - **Targeted signal discovery (not blocked by ignore rules):** The analyzer must detect and parse “known signal files” via explicit checks (e.g., `pyproject.toml`, `requirements*.txt`, `tox.ini`, `noxfile.py`, `setup.py`, `setup.cfg`, `Makefile`, `.pre-commit-config.yaml`, `.github/workflows/*.yml`). These targeted reads must not be suppressed by `.gitignore`, since they are required to produce grounded, high-signal output.

    - **Broad scan filtering (gitignore-aware):** Any broad filesystem walk (e.g., enumerating docs/config candidates, language counts, fallback discovery) must respect repo-local ignore patterns from `.gitignore` (and optionally `.git/info/exclude`). Global/user gitignore configuration must not be used, to keep analyzer output deterministic across machines.

---

## 5. Implementation Plan

### 5.1 Tech Stack
- Language: Python 3.11+
- Framework: FastMCP
- Testing: pytest
- Dependency Manager: uv
- Validation: Pydantic

### 5.2 Milestones

Milestones 1–4 are implemented and tested.

Milestone 5 (pivoted):
- Lock extractor quality gates (P0) and output compactness contract (caps + truncation notes)
- Prioritize docs/config lists before truncation (high-signal ordering)

---

## 7. MVP Definition (Pivoted)

We consider the Python-focused MCP server MVP-ready when:

1) It runs locally and passes tests.
2) On the Phase 5 evaluation set (minimum: scripts repo + tox library + Makefile-heavy repo):
   - Makefile repos: output includes stable commands like `make test` and does not include recipe internals.
   - scripts repos: output surfaces `scripts/*.sh` entrypoints as runnable commands (`bash scripts/<file>.sh`).
   - Large repos: output does not include env/vendor pollution (no `site-packages` paths) and remains compact (caps + truncation notes).
3) A/B evaluation demonstrates:
   - MCP mode reduces misleading output (fewer invented commands/versions).
   - MCP mode shows meaningful token reduction vs baseline (recorded per run where possible).

At that point, iterate based on real-world usage.
