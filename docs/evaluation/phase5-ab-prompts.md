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
You are running the Phase 5 A/B evaluation for onboarding quality.

Hard rule: DO NOT use any MCP tools or MCP servers in this run.

Goal: Generate an ONBOARDING.md for this repository that is accurate and copy/pastable.

Rules:
- Do not claim a Python version unless you can cite an explicit pin you found (e.g. .python-version, runtime.txt, pyproject.toml requires-python, CI config). If you did not find one, write exactly: "No Python version pin detected."
- Do not invent run/test/lint/format/build commands. Only include a command if you can cite exactly where it came from (filename + snippet/target name).
- If you are unsure about a command, write "Unsure" and list the exact file(s) you would check next.
- Prefer being correct over being complete.

Output format:
1) Evidence used (bullet list of the exact files you inspected and what each contributed)
2) ONBOARDING.md content (single Markdown document, ready to save as ONBOARDING.md)
3) Uncertainties / follow-ups (what you could not confirm, and which file(s) to check)
4) Token usage: <value or unknown>
4) Token usage (if available from the UI; otherwise write "Token usage: unknown")

Now produce the output.
```

---

## B) MCP Prompt (WITH mcp-repo-onboarding)

Use this run to generate onboarding grounded in MCP output.

```text
You are running the Phase 5 A/B evaluation for onboarding quality.

Use the `repo-onboarding` MCP server and follow the grounding rules strictly.

Hard rule: DO NOT inspect/read repository files directly in this run. Use only MCP tool output as evidence.

Step 1 — Call MCP tools:
1) Call `analyze_repo` with {}.
2) Call `get_run_and_test_commands` with {}.

Step 2 — Extract evidence (internal use only, do NOT include raw tool JSON in ONBOARDING.md):
From `analyze_repo`, extract these fields for grounding your prose:
- repoPath
- python.pythonVersionHints
- python.packageManagers
- python.dependencyFiles
- python.envSetupInstructions
- projectLayout
- scripts
- testSetup
- configurationFiles
- docs
- notes

From `get_run_and_test_commands`, extract:
- devCommands
- testCommands
- buildCommands

Step 3 — Grounding rules (hard rules):
- Python version: ONLY mention a specific version if `python.pythonVersionHints` contains it. If empty, write exactly: "No Python version pin detected."
- Commands: ONLY include commands that appear in:
  - `scripts.*`, or
  - `testSetup.commands`, or
  - `get_run_and_test_commands` arrays.
- If those arrays are empty for a section, state: "No explicit commands detected by the analyzer." Do not invent alternatives.
- Never present Makefile recipe internals as commands. Prefer stable `make <target>` style commands if present.
- Generic suggestions: If a command has `description: "Generic suggestion"` or `confidence: "heuristic"`, label it as "(Generic suggestion)" in the output. Keep to 1–2 bullets max.

Step 4 — Produce ONBOARDING.md (copy/pasteable):
Write a single Markdown document that MUST start with the following exact structure:

# ONBOARDING.md

## Overview
Repo path: <repoPath>

Then continue with these sections (always include the headings exactly as written):
- Environment setup
- Install dependencies
- Run / develop locally (if commands exist; otherwise state none detected)
- Run tests (if commands exist; otherwise state none detected)
- Lint / format (if commands exist; otherwise state none detected)
- Analyzer notes (include this section ONLY if `notes` is not empty; if empty or missing, omit the section entirely; if included, render notes verbatim as bullet points)

Then include three separate “files” sections grounded to the correct MCP fields (do not mix them):
- Dependency files detected (list only from `python.dependencyFiles[*].path`)
- Useful configuration files (list only from `configurationFiles[*].path`)
- Useful docs (list only from `docs[*].path`)

Important formatting rule:
- Do NOT use "Repository:" as a title or heading.
- Always use "## Overview" and "Repo path: <repoPath>" exactly as above.

Step 5 — Write file (interactive mode only):
If you are running interactively and file writing is supported, call `write_onboarding` with:
- path: "ONBOARDING.md"
- mode: "overwrite"
- createBackup: true
- content: (the ONBOARDING.md you just generated)

If you are running in headless mode and `write_onboarding` causes the run to halt, SKIP the tool call and only output the ONBOARDING.md content.

Step 6 — Token usage:
At the end of your response (outside the ONBOARDING.md), write: "Token usage: <value if available, else unknown>"

Now execute.
```
---


## Notes

- The goal is not maximum completeness; it is accuracy, grounded commands, and compact output.
- If MCP output does not contain commands, the correct result is to say none were detected.
- The B run must remain auditable: tool output must be quoted before prose.