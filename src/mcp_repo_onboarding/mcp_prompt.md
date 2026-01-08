# MCP Prompt: ONBOARDING.md Generation

**PROMPT_VERSION:** blueprint-v2-renderer-2025-12-31

You are generating ONBOARDING.md using MCP tool output only.

Use the `repo-onboarding` MCP server and follow these rules strictly.

## Configuration

```
SHOW_PROVENANCE = False
```

## Hard Rules

- **DO NOT** inspect or read repository files directly. Use only MCP tool output as evidence.
- **DO NOT** execute any shell commands, git commands, or similar external processes.
- **DO NOT** use the Shell tool (or any shell-execution tool) for any reason.
- MCP tool calls are executed by Gemini CLI via MCP. They are **NOT** Python functions you import.
- **MUST NOT** attempt tool emulation such as: `python`, `python3`, `python3 -c`, `which python`, `uv`, `pip`, etc.
- **MUST NOT** claim MCP tools cannot run due to missing Python/interpreters/PATH.

## Provenance Rule (Hard Rule)

- `SHOW_PROVENANCE` is false.
- `ONBOARDING.md` **MUST NOT** contain the substrings: `"source:"` or `"evidence:"` anywhere.

## No Retries + Circuit Breaker (Hard Rule)

- You get at most **ONE** attempt per required MCP tool call.
- If **ANY** tool call fails, is denied, is blocked, times out, or returns an error:
  - Do **NOT** retry.
  - Do **NOT** attempt debugging.
  - Immediately use the fallback skeleton (below) and proceed to `write_onboarding`.

## Step 1 — Call MCP Tools

1. Call `analyze_repo` with `{}`
2. Call `get_run_and_test_commands` with `{}`
   - This call is allowed, but ignored for rendering if blueprint v2 is present.

## Step 2 — Produce ONBOARDING.md Content

### PRIMARY PATH — Blueprint v2 (Hard Rule)

If `analyze_repo` output contains `onboarding_blueprint_v2.render.markdown`:
- The `ONBOARDING.md` content **MUST** be **EXACTLY** that string.
- Render verbatim: do **NOT** modify, reformat, reorder, wrap, or "fix" any content.
- Do **NOT** change bullet markers (do not convert `*` to `-`, etc.).
- Do **NOT** add any narration such as "I received the blueprint".

### SECONDARY PATH — Blueprint v1 (Temporary Compatibility Only)

Else if `onboarding_blueprint_v1` exists:
- Render it verbatim:
  - For each section in `onboarding_blueprint_v1.sections`:
    - Print `section.heading` exactly as-is
    - Then print each line in `section.lines` exactly as-is
  - Separate sections with exactly one blank line
- Do **NOT** modify content.

### FALLBACK PATH — Only If No Blueprint Is Available

#### Fallback Repo Path Rule (Hard Rule)

- If `analyze_repo` returned any JSON that contains `"repoPath"`, use that value for the Repo path line.
- Else if `analyze_repo` returned an `ErrorResponse` JSON containing `details.repo_root`, use `details.repo_root`.
- Else use: `Repo path: (unknown)`

If blueprint v2 and v1 are both missing (tool failed or field absent), output this exact validator-safe skeleton:

```markdown
# ONBOARDING.md

## Overview
Repo path: (unknown)

## Environment setup
No Python version pin detected.
(Generic suggestion)
* `python3 -m venv .venv` (Create virtual environment.)
* `source .venv/bin/activate` (Activate virtual environment.)

## Install dependencies
No explicit commands detected.

## Run / develop locally
No explicit commands detected.

## Run tests
No explicit commands detected.

## Lint / format
No explicit commands detected.

## Dependency files detected
No dependency files detected.

## Useful configuration files
No useful configuration files detected.

## Useful docs
No useful docs detected.
```

## Step 3 — Write File (Hard Rule)

You **MUST** call `write_onboarding` to persist the content:
- `path`: `"ONBOARDING.md"`
- `mode`: `"overwrite"`
- `content`: (the exact ONBOARDING.md content from Step 2)

## Step 4 — Token Usage (Hard Rule)

At the end of your chat response (NOT inside ONBOARDING.md), write:

```
Token usage: <value if available, else unknown>
```

---

## Execution

Now execute.
