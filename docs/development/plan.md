# Phase 6: Evaluation Regressions & Standards (Issues 53-57)

This phase addresses critical regressions in version detection and standardizes `ONBOARDING.md` output through a deterministic validator "Epic" (Issue 56).

## Gap Analysis
- **In-Scope**:
    - **Deterministic Validator (#56)**: Implements Rules V1-V8 to gate evaluation runs.
    - **Strict Pin Extraction (#53)**: Uses **regex-based** filtering to reject range specifiers.
    - **Prompt Engineering (#54, #55, #57)**: Updates `B-prompt.txt` to align with validator rules.
- **Out-of-Scope**:
    - **LLM-based Self-Correction**: Enforcement is via the deterministic validator, not the model itself.

## Proposed Changes

### Step 1: Tooling & Validation (Issue 56 - Epic)
Implement the validator first to establish a stable gate.

#### [NEW] [validate_onboarding.py](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/validate_onboarding.py)
A standalone Python script implementing Rules V1-V8:
- **V1 (Headings)**: Asserts exact presence and order of the 10 required headings.
- **V2 (Repo Path)**: Asserts `Repo path: <path>` under Overview.
- **V3 (No Pin Phrasing)**: Fails on forbidden `Python version: No Python version pin detected.`
- **V4 (Venv Labeling)**: Fails on unlabeled venv snippets.
- **V5 (Command Formatting)**: Asserts backticks for commands and parentheses for descriptions.
- **V6 (Analyzer Notes)**: Fails on empty placeholder notes.
- **V7 (Install Policy)**: Fails on >1 `pip install -r` line.
- **V8 (Provenance)**: Fails on `source:`/`evidence:` unless overridden.

#### [MODIFY] [run_headless_evaluation.sh](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/run_headless_evaluation.sh)
- Integrate `validate_onboarding.py` into the evaluation loop.

### Step 2: Analysis Logic (Issue 53)
Fix correctly at the source using strict versioning rules.

#### [MODIFY] [core.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/core.py)
- Refine `_infer_python_environment` with **regex-based** exact version filtering.
- Regex: `^\d+\.\d+(\.\d+)?$` (Matches `X.Y` or `X.Y.Z` only).
- Rejects any string with operators (`>`, `<`, `~`, `^`), wildcards (`*`, `x`), or text prefixes.

### Step 3: Prompt Engineering (Issues 54, 55, 57)
Align prompt instructions with Validator rules (V3, V4, V7).

#### [MODIFY] [B-prompt.txt](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/B-prompt.txt)
- **#54 (No Pin)**: Forbid "Python version:" prefix for "No pin" state.
- **#55 (Venv)**: Mandatory labeling of venv snippets.
- **#57 (Install)**: Prioritize `make install` and cap pip commands.

### Step 4: Verification
Run full evaluation batch with validator enabled.

## Verification Plan

### Automated Tests
- **Validator Unit Tests**: `tests/test_onboarding_validator.py` covering Rules V1-V8.
- **Pin Logic Tests**:
    - `python-pin-range/pyproject.toml` (>=3.10 -> empty).
    - `workflow-python-pin-env` (3.14 -> 3.14).
    - `3.x` -> empty.
