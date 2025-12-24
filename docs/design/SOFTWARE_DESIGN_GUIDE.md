# mcp-repo-onboarding – Software Design Guide

This document defines the design principles and process for building
**mcp-repo-onboarding** using a structured, maintainable approach.

We follow a 7‑step plan:

1. Define What You’re Building
2. Design the User Experience
3. Understand the Technical Needs
4. Implement Testing and Security Measures
5. Plan the Work
6. Identify Ripple Effects
7. Understand the Broader Context

Everything we implement (including code stubs) should align with this guide.

---

## 1. Define What You’re Building

### 1.1 What this application is

**mcp-repo-onboarding** is:

- An **MCP (Model Context Protocol) server** intended to be used primarily by the **Gemini CLI**.
- Purpose-built to analyze a **local code repository** (Python‑first) and help generate/maintain an `ONBOARDING.md` guide.

**Intended audience:**

- **Maintainers / tech leads** of Python repositories who want good onboarding docs without constant manual updates.
- **New contributors / new hires** who want a clear “how to set this repo up, run it, and test it” guide.

### 1.2 Problem we solve

- Repos rarely have accurate, up‑to‑date onboarding documentation.
- New contributors repeatedly ask the same questions:
  - How do I set up the environment?
  - How do I install dependencies?
  - How do I run tests?
  - How do I run the app?
- Maintainers don’t want to constantly rewrite `ONBOARDING.md` as the repo evolves.

**How it operates (high‑level):**

1. MCP server is started (e.g., via `uv run mcp-repo-onboarding`).
2. Gemini calls tools like:
   - `analyze_repo`
   - `read_onboarding`
   - `write_onboarding`
   - `get_run_and_test_commands`
3. The server:
   - Analyzes the repo’s structure and config (Python‑first).
   - Returns structured JSON describing env/setup/run/test/deploy aspects.
   - Reads/writes `ONBOARDING.md` as requested.
4. Gemini uses that structured info to generate or update the doc.

### 1.3 Domain-Driven Design (DDD) approach

We treat this as a small domain with a few clear concepts:

**Core domain concepts:**

- `Repository` – the project folder under analysis.
- `RepoAnalysis` – a **value object** (Pydantic model) describing what we know about the repo.
- `OnboardingDocument` – the `ONBOARDING.md` file (path + content).
- `CommandInfo` – canonical representation of commands (run/test/build etc.).

**Content Generation:**
- The server may generate simple, structured onboarding content when explicitly requested via tool parameters, ensuring critical information like truncation notes is included.

**Bounded Contexts:**

- **Analysis Context**
  - Pure logic that walks the repo and infers:
    - Python env
    - Dependencies
    - Scripts/commands
    - Frameworks
    - Test setup
  - Output: `RepoAnalysis`.

- **Onboarding Context**
  - Reading/writing `ONBOARDING.md`.
  - No business rules about *what* goes into the doc; just I/O and safety.

- **MCP Interface Context**
  - Adapts domain logic to MCP tools.
  - Translates:
    - MCP tool calls → domain service calls.
    - Domain objects → MCP responses.

### 1.4 Simplify the model

We deliberately **avoid** overcomplication:

- No heavy plugin system for now.
- No execution of repo code (analysis is static).
- Limit domain to:
  - “Describe this repo”
  - “Read/write this onboarding file”
  - “Expose commands in a structured way”
- Additional features (e.g., CI integration) can be add‑on services later.

### 1.5 Zoom out / Zoom in and MVP

**Zoomed out (vision):**

- MCP server that works across multiple languages.
- Rich heuristics for frameworks and CI/CD.
- Change‑aware onboarding (detects drift).

**Zoomed in MVP (what we build first):**

- Python‑first:
  - Identify dependencies and env (Poetry, pip, Pipenv, Conda, uv).
  - Identify test setup (pytest, unittest, tox, nox).
  - Detect common frameworks (Django, Flask, FastAPI) and CLIs.
- Provide:
  - `analyze_repo`
  - `read_onboarding`
  - `write_onboarding`
  - `get_run_and_test_commands`
- Good enough for Gemini to generate a **useful, accurate `ONBOARDING.md`**.

---

## 2. Design the User Experience

Even though this is a backend/MCP service, UX still matters:
our “users” are both humans and the LLM client.

### 2.1 Main user stories

**US1 – Create onboarding from scratch**

- As a **maintainer**, I want Gemini to create `ONBOARDING.md` for my Python repo.
- Flow:
  - User configures Gemini with this MCP server.
  - User asks: “Create an onboarding guide for this repo.”
  - Gemini calls `analyze_repo` → gets `RepoAnalysis`.
  - Gemini generates content → calls `write_onboarding(mode="create")`.

**US2 – Update onboarding after repo changes**

- As a **maintainer**, I want `ONBOARDING.md` updated when dependencies/commands change.
- Flow:
  - User asks Gemini: “Update `ONBOARDING.md` to reflect the new toolchain.”
  - Gemini calls:
    - `analyze_repo`
    - `read_onboarding`
    - Generates updated content
    - `write_onboarding(mode="overwrite", create_backup=true)`.

**US3 – Answer “how do I run/test this?”**

- As a **new contributor**, I want concrete commands to set up, run, and test the repo.
- Flow:
  - User: “How do I run tests and the dev server?”
  - Gemini calls `get_run_and_test_commands` (or `analyze_repo`).
  - Gemini responds with direct commands like:
    - `uv sync`
    - `uv run pytest`

### 2.2 Impact on “UI” (Gemini interaction)

Design the tools so they’re:

- **Predictable** – consistent schemas so the model can learn to rely on them.
- **Minimal** – a small number of tools that do one thing well.
- **Composable** – `get_run_and_test_commands` is a filtered view of `analyze_repo`, not an entirely separate logic path.

### 2.3 UX design principles

- Favor **simple, structured JSON** (Pydantic models) over clever encodings.
- Don’t expose internal complexity; keep output focused:
  - Languages
  - Commands
  - Env setup hints
  - Framework/test/deployment hints
- Avoid making the LLM guess file paths when a clear path can be provided.

---

## 3. Understand the Technical Needs

### 3.1 Essential technical details

- **Runtime**: Python (≥ 3.11).
- **Framework**: FastMCP.
- **Validation**: Pydantic.
- **I/O**:
  - File system reads for repo analysis.
  - File system reads/writes for `ONBOARDING.md`.
  - Standard I/O (stdin/stdout) for MCP communication.
- **No database** for MVP.
- **Config**:
  - `REPO_ROOT` env var for repo root sandbox.
- **Parsing**:
  - TOML (e.g., `pyproject.toml`).
  - INI (e.g., `tox.ini`).
  - Simple text scanning for Python imports/framework hints.

### 3.2 Structural sketch

We’ll keep a clear separation of concerns.

**Modules:**

- `src/mcp_repo_onboarding/schema.py`
  - Pydantic models.
- `src/mcp_repo_onboarding/analysis/` (Package)
  - Logic that builds a `RepoAnalysis` from the filesystem.
- `src/mcp_repo_onboarding/onboarding.py`
  - Read/write `ONBOARDING.md`.
- `src/mcp_repo_onboarding/server.py`
  - FastMCP server and tool implementations.

### 3.3 Functional programming emphasis

Where possible:

- Use **pure functions** for transformations and heuristics.
- Separate side effects (I/O) in small, testable wrappers.

### 3.4 Edge cases & testability

We should explicitly support and test:

- Repo with only `requirements.txt`.
- Repo with only `pyproject.toml` (uv/Poetry).
- Repo with **no tests**.
- Repo **not a git repo**.
- Missing or unreadable files (return structured errors/omissions, don't crash).

---

## 4. Implement Testing and Security Measures

### 4.1 Testing strategy

**Coverage goals (MVP):**

- 80%+ coverage on `analysis` and `onboarding` logic.
- Tests for each tool handler.

**Test types:**

- **Unit tests**: Pure functions.
- **Integration tests**: Run analysis on small fixture repos under `tests/fixtures/`.

### 4.2 Security & side effects

- **Never execute** repo code or shell commands.
- **No network access**.
- File system sandbox:
  - All paths resolved relative to `REPO_ROOT`.
  - Reject any path that escapes the root.
- Handle:
  - Permission errors gracefully.
  - Large repos by limiting file scanning (`maxFiles`).

---

## 5. Plan the Work

### 5.1 Milestones

1. **M1 – MCP skeleton** (FastMCP).
2. **M2 – Core Python repo analysis**.
3. **M3 – Framework & test heuristics**.
4. **M4 – Onboarding tools**.
5. **M5 – Polish & docs**.

### 5.2 Risk factors

- False‑positive/negative detection of tools.
- Large repo performance.

---

## 6. Identify Ripple Effects

### 6.1 Beyond code

- **Docs updates**: README, CONTRIBUTING, etc.
- **User communication**: Changelog.

---

## 7. Understand the Broader Context

### 7.1 Limitations of current design

- Python‑focused.
- Static analysis only.

### 7.2 Future extensions

- **Polyglot support**.
- **Change‑aware onboarding**.
- **CI/CD integration**.

---

## Working Agreement

- All new features should follow this guide.
- Maintain clear separation between schema, analysis, onboarding, and server.
- **TDD is mandatory**.
