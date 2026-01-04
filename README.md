
> [!NOTE]
> **Phase 9 (Python-Only Release)** is now supported in this server (v0.1.0)!
>
> The analyzer generates **Python-focused onboarding**. Non-Python repos will see a neutral "Python tooling not detected" message.
> Node.js/TypeScript commands are not generated yet (deferred to Phase 10).

# mcp-repo-onboarding — MCP Server for Static Analysis & Onboarding

A professional MCP server for analyzing local Python repositories and generating practical `ONBOARDING.md`. It detects environment configuration, dependencies, scripts, and frameworks with **deterministic, static analysis** (no execution, no network).

---

## ✨ Features

- **📊 Repo Structure Analysis**: Analyzes local Python repository layout and categorizes files (docs, configs, dependencies).
- **🧰 Dependency Detection**: Detects Python environment files (`requirements.txt`, `pyproject.toml`, `setup.py`, etc.).
- **⚙️ Command Detection**: Extracts developer and test commands from `Makefile`, `tox.ini`, `shell scripts`, and more.
- **🔍 Framework Detection**: Detects popular Python frameworks (Django, Flask, FastAPI, Streamlit, Gradio) from `pyproject.toml` and `requirements.txt`.
- **📝 ONBOARDING.md Generation**: Generates validator-compliant onboarding documents with consistent heading order.
- **📜 Changelog**: Track project history in [CHANGELOG.md](CHANGELOG.md).
- **🛡️ Safe & Deterministic**: Uses static file I/O only (no subprocess, no network, no command execution).
- **🔧 Other Tooling Reporting**: Reports secondary tooling (Node.js, Docker, Go, Rust) neutrally via evidence files (Phase 9).

---

## 📋 Prerequisites

1. **Python 3.11+** installed.
2. **[uv](https://github.com/astral-sh/uv)** (recommended for faster installation).
3. **Gemini CLI** (or any LLM runtime that supports MCP servers).

---

## 🚀 Installation

### 1. Install Server Locally

Install the server locally using `uv` (recommended):

```bash
git clone https://github.com/rogermt/mcp-repo-onboarding.git
cd mcp-repo-onboarding
uv sync
```

### 2. Run Server

Run the server in standalone mode:

```bash
uv run mcp-repo-onboarding
```

### 3. Install as Gemini CLI Extension (Recommended)

This server is designed to be installed as an extension in [Gemini CLI](https://github.com/google-gemini/gemini-cli).

```bash
# From GitHub
gemini extensions install https://github.com/rogermt/mcp-repo-onboarding

# From local path
gemini extensions install /path/to/mcp-repo-onboarding
```

### 4. Activate

Restart the Gemini CLI. The following MCP tools will be available:

- `/analyze_repo` — Analyze local repository and return structured JSON.
- `/write_onboarding` — Write (or overwrite) `ONBOARDING.md` to the repo root.
- `/read_onboarding` — Read existing `ONBOARDING.md` content.
- `/get_run_and_test_commands` — Get simplified run/test command suggestions.

---

## 💡 Usage

The server provides MCP tools for analyzing repositories and managing onboarding documents.

### 🎯 Specific Tools (Recommended)

**Analyze Repository:**

```bash
# Analyze current directory (default)
/analyze_repo

# Analyze specific path
/analyze_repo path/to/repo
```

**Generate ONBOARDING.md:**

```bash
# Write to repo root (default, uses blueprint)
/write_onboarding

# Append to existing file
/write_onboarding mode="append"

# Overwrite existing file
/write_onboarding mode="overwrite"
```

**Read ONBOARDING.md:**

```bash
# Read from repo root
/read_onboarding

# Read specific path
/read_onboarding path/to/ONBOARDING.md
```

**Get Run & Test Commands:**

```bash
# Get suggestions
/get_run_and_test_commands
```

### 🔧 Advanced Options (Environment Variables)

You can customize behavior by setting environment variables:

- **`MCP_REPO_ONBOARDING_MAX_FILES`** (default: `5000`)
  - Maximum number of files to scan in the repo.

- **`MCP_REPO_ONBOARDING_PYTHON_DETECTED`** (calculated)
  - Indicates whether Python was detected (used internally for scope messaging).

---

## 🎨 Advanced Analysis Features

### Framework Detection

The analyzer detects Python frameworks from `pyproject.toml` and `requirements.txt`.

**Supported Frameworks:**
- Django (Classifiers + Poetry deps)
- Wagtail (Classifiers)
- Flask (Poetry deps)
- FastAPI (Poetry deps)
- Streamlit (Requirements deps)
- Gradio (Requirements deps)

**Note:** Framework detection is evidence-only and does not infer commands.

### Notebook Detection & Capping

The analyzer detects Jupyter notebook directories.

- **Truncation:** The list of notebook directories in `ONBOARDING.md` is capped to `20` entries to prevent massive lists (e.g., in monorepos).
- **Note:** If truncated, a message like `"* notebooks list truncated to 20 entries (total=215)"` is added to Analyzer notes.

### "Other Tooling Detected" (Phase 9)

Secondary tooling (e.g., Node.js, Docker, Go) is reported neutrally in the `Other tooling detected` section.

- **Evidence Files:** Lists explicit files (e.g., `.nvmrc`, `package.json`).
- **No Commands:** No `npm`, `yarn`, `pnpm`, or `docker` commands are suggested.
- **Sorting & Truncation:** Evidence lists are sorted alphabetically and capped to 3 files with a deterministic note.

---

## 🏗️ Architecture

### Analysis Pipeline

1. **File Scanning**: Scans repo tree (respects `.gitignore`, safety ignores).
2. **Categorization**: Sorts files into docs, configs, deps, scripts.
3. **Prioritization**: Ranks files by importance (root, standards, keywords).
4. **Extraction**:
   - **Scripts**: `Makefile`, `tox.ini`, `shell` scripts.
   - **Frameworks**: `pyproject.toml`, `requirements.txt`.
   - **Other Tooling**: `.nvmrc`, `package.json`, lockfiles.
5. **Bluepring Generation**: Compiles sections from a registry (`onboarding_blueprint_engine`).
6. **Validation**: Output is checked against validator rules (V1-V3).

### Registry Pattern

The blueprint engine uses a **registry pattern** (Strategy Pattern) for detectors.

- **Detectors:** `PyprojectClassifierDetector`, `PoetryDependencyDetector`, `RequirementsDetector`.
- **Extensible:** Add new detectors by registering them in `DETECTORS`.

---

## 📁 File Management

### Input/Output Locations

- **Repo Root:** The target repository path (default: `.`).
- **ONBOARDING.md:** Written to the root of the target repository.
- **Analysis Cache:** No persistent cache; analysis is performed on demand.

### Safety Ignores

The scanner ignores specific paths to prevent noise and ensure determinism:

- `tests/fixtures/`
- `test/fixtures/`
- `.git/`, `.venv/`, `__pycache__/`
- `node_modules/`, `site-packages/`

---

## 🐛 Troubleshooting

### Common Issues

1. **"No Python detected" message appears:**
   - **Cause:** The repo has no explicit Python evidence files (`pyproject.toml`, `setup.py`, `requirements.txt`) or `.py` files.
   - **Fix:** This is expected for non-Python repos in Phase 9. The onboarding will still be generated but will state Python-only scope.

2. **"No explicit commands detected" in sections:**
   - **Cause:** No Makefile, `tox.ini`, or shell scripts found with recognizable targets.
   - **Fix:** Add a `Makefile` or `tox.ini` with standard targets (`test`, `install`, `lint`).

3. **"No description provided by analyzer" for scripts:**
   - **Cause:** Script has no safe header comment.
   - **Fix:** Add a safe header comment (e.g., `# Run the test suite`) to the top of the script.

4. **ONBOARDING.md validation fails:**
   - **Cause:** Generated document does not match validator rules (missing required headings, wrong bullets).
   - **Fix:** This should not happen with Phase 9. If it does, run `scripts/validate_onboarding.py` locally to debug.

### Debug Mode

The server logs detailed warnings to the console:

```bash
# Run with debug output
uv run mcp-repo-onboarding
```

---

## 📊 Technical Details

### MCP Server Protocol

- **Protocol:** JSON-RPC over stdio
- **SDK:** `mcp[cli]>=1.25.0`
- **Tools:** `analyze_repo`, `write_onboarding`, `read_onboarding`, `get_run_and_test_commands`

### Analysis Core

- **Language:** Python 3.11+
- **Dependencies:** `packaging`, `pathspec`, `pydantic`, `tomllib`
- **File I/O:** Standard library (`pathlib`, `os`)

### Schema (`RepoAnalysis`)

- `repoPath`: Repository root path.
- `python`: Python env info (versions, package managers, deps).
- `scripts`: Grouped scripts (dev, test, lint, format, install).
- `frameworks`: List of detected frameworks.
- `configurationFiles`: Config files (Makefile, workflows, etc.).
- `docs`: Documentation files.
- `notebooks`: Notebook directories.
- `otherTooling`: Secondary tooling (Node.js, Docker, etc.).
- `notes`: Analyzer notes (truncations, etc.).

### Blueprint Engine

- **Module:** `onboarding_blueprint_engine`
- **Registry:** `registry.py` (list of `SectionSpec`).
- **Render Mode:** Verbatim (bullet list format).

---

## 🤝 Contributing

1. Fork the repository.
2. Create a feature branch.
3. Make your changes (ensure tests pass).
4. Run `uv run pytest` and `uv run mypy`.
5. Submit a pull request.

---

## 📄 Legal

- **License:** [Apache License 2.0](LICENSE)
- **Security:** [Security Policy](SECURITY.md)
