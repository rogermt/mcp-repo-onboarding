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


## B) MCP Prompt (MCP)

```text
You are running the repository onboarding signal extraction.

Use the `repo-onboarding` MCP server and follow the grounding rules strictly.

Provenance toggle (default: hidden)
Configuration:
SHOW_PROVENANCE = False

Analyzer Limits:
- DEFAULT_MAX_FILES = 5000 (Maximum files scanned)
- MAX_DOCS_CAP = 10 (Maximum docs returned)
- MAX_CONFIG_CAP = 15 (Maximum config files returned)

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
- repoPath
- python.pythonVersionHints
- python.dependencyFiles
- python.envSetupInstructions
- python.installInstructions
- projectLayout
- scripts
- frameworks (including frameworks[].name, frameworks[].detectionReason, and if present: frameworks[].keySymbols, frameworks[].evidencePath)
- configurationFiles
- docs
- notes
- notebooks (if present: list of directories containing .ipynb files)

From `get_run_and_test_commands`, extract:
- devCommands, testCommands, buildCommands.

Step 3 — Grounding rules (Hard rules):
- Python version: ONLY mention a specific version if `python.pythonVersionHints` contains it. If empty, say exactly: "No Python version pin detected."
- Environment setup: If `python.pythonVersionHints` is empty and no explicit venv commands are detected, you MUST provide a standard (Generic suggestion) venv snippet.
- (Generic suggestion) Labeling Rule: The line `(Generic suggestion)` MUST appear exactly as written (no colon, no extra text) exactly ONE line above the first venv command.
- Venv Formatting:
(Generic suggestion)
* `python3 -m venv .venv` (Create virtual environment.)
* `source .venv/bin/activate` (Activate virtual environment.)
- Commands: ONLY include commands that appear in `scripts.*`, `testSetup.commands`, or `get_run_and_test_commands`.
- Install Commands Priority: If `make install` is detected, it MUST be the primary and SOLE install command. Do not invent `pip install` commands if `make install` is present. If `make install` is absent, use the install commands provided by MCP output (`python.installInstructions` or `scripts.install`). Do NOT invent `pip install -r` commands from `python.dependencyFiles`. Max ONE `pip install -r` line allowed.
- Signal Provenance: If `SHOW_PROVENANCE` is true, append (source: <source>) using the exact `source` value from MCP output. If `SHOW_PROVENANCE` is false, omit provenance entirely.
- Never present Makefile recipe internals as commands.
- Command Formatting Rule (hard rule): Every command bullet MUST follow the format:
  `* `command` (Brief description.)`
  Use a space between the backtick and opening parenthesis.
  Do NOT use dashes or colons between the command and description.
- Confidence: If a command/signal has `confidence: "heuristic"`, label it as "(Generic suggestion)" on the line above.

No-commands sentence (hard rule):
- The ONLY allowed no-commands sentence anywhere in ONBOARDING.md is exactly:
  "No explicit commands detected."
- Do NOT write any variants such as:
  "No explicit format commands detected."
  "No explicit lint commands detected."
  "No explicit install commands detected."
  "No explicit dev commands detected."

Notebook-centric rule (informational only):
- If `notebooks` is present and non-empty OR notes include the notebook-centric message, add a bullet in `## Analyzer notes` indicating:
  "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."
- Also include a bullet listing notebook directories, e.g.:
  "* Notebooks found in: notebooks/, research/"

Do NOT prescribe a runner (Kaggle/Colab/local). Do NOT assume notebook kernel language.

Framework proof (hard rule):
- Treat frameworks[].keySymbols / frameworks[].evidencePath as internal grounding only.
- Do NOT print keySymbols or evidencePath in ONBOARDING.md.
- When SHOW_PROVENANCE is false, do NOT output any lines containing the substrings "source:" or "evidence:" anywhere in ONBOARDING.md.

Step 4 — Produce ONBOARDING.md (copy/pasteable):
Bullet points in the document ALWAYS use `*`.

**Heading rule (hard rule):**
- Use the heading exactly: `## Environment setup` (do not write `## Environment` and do not add parentheses like `(Python 3.14)` in the heading).
- The first line under `## Environment setup` must be the Python version statement:
  - If `python.pythonVersionHints` is non-empty: `Python version: <value>`
  - If empty: `No Python version pin detected.` (DO NOT prefix with "Python version:").

Command section content rule (hard rule):
For each of these sections:
- ## Install dependencies
- ## Run / develop locally
- ## Run tests
- ## Lint / format

Output MUST be exactly one of:
A) One or more bullet lines of the form: "* `command` (Description.)"
OR
B) A single standalone line: "No explicit commands detected."

Do NOT output any additional explanatory lines (including per-subcategory lines like "No explicit format commands detected.") if the section already contains at least one command bullet.

The document MUST start exactly like this:

# ONBOARDING.md

## Overview
Repo path: <repoPath>

Continue with these headings exactly:
## Environment setup
## Install dependencies
## Run / develop locally
## Run tests
## Lint / format

Lint / format is a combined section:
- Include any lint commands and any format commands together as bullets in the same section.
- Do not add separate sub-headings or separate fallback sentences for lint vs format.

Section routing rule (hard rule):
- Only put venv/activation commands in Environment setup.
- Only put package install commands in Install dependencies.
- If a `pip install ...` command is present anywhere in extracted MCP evidence, you MUST NOT output “No explicit commands detected.”

## Analyzer notes
- Include ONLY if `notes` is not empty OR notebook-centric detection applies OR frameworks are detected.
- List notes verbatim as bullet points.
- If notebook directories are available (analyze_repo.notebooks), add a bullet listing them (informational only).

Frameworks (informational only; hard formatting rule):
- If analyze_repo.frameworks is non-empty, add exactly ONE bullet in ## Analyzer notes.
- The bullet MUST start exactly with:
  "* Frameworks detected (from analyzer): "
- Then list framework names joined by ", " and end the names list with a period.
  Example names list:
  "Django, Wagtail."
  "Flask."
- Then optionally append exactly one space + a parenthesized reason:
  " (Detected via pyproject.toml classifiers.)"
  or
  " (Flask support detected via pyproject.toml (Poetry) dependency key 'flask' (optional).)"

Reason rule:
- If exactly one framework is present, use its detectionReason.
- If multiple frameworks are present and ALL have the same detectionReason, use that shared detectionReason.
- Otherwise omit the reason entirely.

Safety:
- Do NOT print frameworks[].keySymbols or frameworks[].evidencePath.
- Do NOT use the literal labels "source:" or "evidence:" anywhere.
## Useful configuration files
- List `configurationFiles[*].path` as bullets.
- If a `description` is present on a config file, include it in parentheses after the path.
- Do NOT print provenance unless SHOW_PROVENANCE is true.

## Useful docs
- List `docs[*].path` as bullets.
- (Do not invent descriptions for docs.)

Step 5 — Write file:
You MUST call `write_onboarding` to persist the changes:
- path: "ONBOARDING.md"
- mode: "overwrite"
- content: (the ONBOARDING.md you just generated)

Step 6 — Token usage:
At the end of your response, write: "Token usage: <value if available, else unknown>"

Now execute.
```
---


## Notes

- The goal is not maximum completeness; it is accuracy, grounded commands, and compact output.
- If MCP output does not contain commands, the correct result is to say none were detected.
- The B run must remain auditable: tool output must be quoted before prose.
