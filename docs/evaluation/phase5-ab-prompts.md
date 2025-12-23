Here is a **copy/paste replacement** for `docs/evaluation/phase5-ab-prompts.md` updated to match the pivot and your newer output contract:

- Adds the hard rule: **B run must not read repo files directly**
- Adds token recording for A and B
- Requires the **three separate sections**:
  - Dependency files detected (from `python.dependencyFiles`)
  - Useful configuration files (from `configurationFiles`)
  - Useful docs (from `docs`)
- Places truncation notes correctly (notes printed in “Analyzer notes”, but also requires section-local notes if you prefer)
- Removes the mixed “Useful repo docs/files” requirement

---

# Phase 5 A/B Evaluation Prompts (Baseline vs MCP)

Purpose: measure onboarding quality **without MCP** vs **with mcp-repo-onboarding** on the same repo.
Run both A and B using the same Gemini model for fairness.

Evaluation focus (pivoted Phase 5):
- B-side output must be **high-signal**, **grounded**, **compact**, and **not misleading**
- Token usage should be lower in B on average (record when available)

---

## A) Baseline Prompt (NO MCP)

Use this run to see what Gemini produces without MCP grounding.

Hard rule: do not use any MCP tools/servers in this run.

```text
You are running the repository onboarding signal extraction.

Use the `repo-onboarding` MCP server and follow the grounding rules strictly.

Provenance toggle (default: hidden)
Configuration:
SHOW_PROVENANCE = False

Rules:
**Signal Provenance (hard rule):**
- Use the `description` field from the MCP JSON to explain why a command or detected item matters.
- If `SHOW_PROVENANCE` is true, append `(source: <source>)` using the exact `source` value from MCP output.
- If `SHOW_PROVENANCE` is false, omit the source entirely (do not print `source:` or `evidence:` anywhere in ONBOARDING.md).


Hard rule: DO NOT inspect or read repository files directly. Use only MCP tool output as evidence.
Hard rule: DO NOT execute any shell commands, git commands, or similar external processes. You are a Scout, not an Investigator.

Step 1 — Call MCP tools:
1) Call `analyze_repo` with {}
2) Call `get_run_and_test_commands` with {}

Step 2 — Extract Evidence (Internal use only):
From `analyze_repo`, extract:
- repoPath, summary, python.pythonVersionHints, python.dependencyFiles, python.envSetupInstructions, projectLayout, scripts, frameworks, configurationFiles, docs, notes.
From `get_run_and_test_commands`, extract:
- devCommands, testCommands, buildCommands.

Step 3 — Grounding rules (Hard rules):
- Python version: ONLY mention a specific version if `python.pythonVersionHints` contains it. If empty, say: "No Python version pin detected."
- Environment setup: If `python.pythonVersionHints` is empty and no explicit venv commands are detected, you MAY provide a standard (Generic suggestion) venv snippet:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
- Commands: ONLY include commands that appear in `scripts.*`, `testSetup.commands`, or `get_run_and_test_commands`.
- Signal Provenance: Use the `description` field from the JSON to explain why a command or framework was detected. If SHOW_PROVENANCE is true, append (source: <source>). If SHOW_PROVENANCE is false, omit the source entirely.
- Never present Makefile recipe internals as commands.
- Confidence: If a command/signal has `confidence: "heuristic"`, label it as "(Generic suggestion)". Keep to 1–2 bullets max per section.

Step 4 — Produce ONBOARDING.md (copy/pasteable):
Bullet points in the documnet ALWAYS use * or an asterix
**Heading rule (hard rule):**
- Use the heading exactly: `## Environment setup` (do not write `## Environment` and do not add parentheses like `(Python 3.14)` in the heading).
- The first line under `## Environment setup` must be the Python version statement:
  - If `python.pythonVersionHints` is non-empty: `Python version: <value>`
  - If empty: `No Python version pin detected.`
The document MUST start exactly like this:

# ONBOARDING.md

## Overview
Repo path: <repoPath>

(Include the verbatim 'summary' from analyze_repo here if present)

Continue with these headings exactly:
## Environment setup (Include Python version here)
## Install dependencies
## Run / develop locally (If commands exist; otherwise "No explicit commands detected.")
## Run tests (If commands exist; otherwise "No explicit commands detected.")
## Lint / format (If commands exist; otherwise "No explicit commands detected.")

Section routing rule (hard rule):

- Only put venv/activation commands in Environment setup (e.g., python -m venv, source .venv/..., activate).
- Only put package install commands in Install dependencies (e.g., any line containing pip install, poetry install, uv pip install, conda env create).
- If a pip install ... command is present anywhere in the extracted MCP evidence, you MUST NOT output “No explicit install commands detected.”

## Analyzer notes (Include ONLY if `notes` is not empty. List verbatim as bullet points.)

## Dependency files detected (List `python.dependencyFiles[*].path`)
## Useful configuration files (List `configurationFiles[*].path` and include their `description` if present. If SHOW_PROVENANCE is true, append (source: <path>))
## Useful docs (List `docs[*].path` and include their `description` if present)

Step 5 — Write file:
If file writing is supported, call `write_onboarding` with:
- path: "ONBOARDING.md"
- mode: "overwrite"
- content: (the ONBOARDING.md you just generated)

Hard rule: If you are running in headless mode (e.g., --yolo or --headless), DO NOT call write_onboarding. Output the Markdown content directly.

Step 6 — Token usage:
At the end of your response, write: "Token usage: <value if available, else unknown>"

Now execute.
```
---


## Notes

- The goal is not maximum completeness; it is accuracy, grounded commands, and compact output.
- If MCP output does not contain commands, the correct result is to say none were detected.
- The B run must remain auditable: tool output must be quoted before prose.
