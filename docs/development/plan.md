# Phase 7: Evaluation Regressions & Standards (Issues 11-15)

This phase addresses critical regressions in version detection and standardizes `ONBOARDING.md` output through a deterministic validator "Epic" (Issue 14).

## Gap Analysis
- **In-Scope**:
    - **Strict Pin Extraction**: Re-implementing Python logic to reject range specifiers (>=, ~, etc.).
    - **Deterministic Validator**: A Python-based regex validator (Rules V1-V8) to gate evaluation runs.
    - **Prompt Engineering**: Updating `B-prompt.txt` to align with new formatting and install policies.
- **Out-of-Scope**:
    - **LLM-based Self-Correction**: We rely on the validator to catch drift, not the model to "double check" itself.
    - **Automatic Markdown Fixing**: The validator will report errors and fail the run, requiring manual or prompt-based fixes.

## Proposed Changes

### [Component Name] Analysis Logic (Issue 11)

#### [MODIFY] [core.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/core.py)
- Refine `_infer_python_environment` to strictly filter `pythonVersionHints`.
- Add `is_exact_version(v: str) -> bool` helper:
    - PASS: `3.10`, `3.14.0`, etc.
    - FAIL: Contains `>=`, `^`, `~`, `*`, `x`, or non-digit starting chars (except version).

### [Component Name] Tooling & Validation (Issue 14 - Epic)

#### [NEW] [validate_onboarding.py](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/validate_onboarding.py)
A standalone Python script implementing Rules V1-V8:
- **V1 (Headings)**: Asserts exact presence and order of the 10 required headings.
- **V2 (Repo Path)**: Asserts `Repo path: <path>` under Overview.
- **V3 (No Pin Phrasing)**: Fails if `Python version: No Python version pin detected.` is found.
- **V4 (Venv Labeling)**: Fails if venv snippet found without `(Generic suggestion)` label in previous 3 lines.
- **V5 (Command Formatting)**: Asserts commands in specific sections are `backticked` and descriptions are `(parenthesized)`.
- **V6 (Analyzer Notes)**: Fails if heading exists but section is effectively empty.
- **V7 (Install Policy)**: Fails if >1 `pip install -r` line detected.
- **V8 (Provenance)**: Fails if `source:` or `evidence:` found (unless `--allow-provenance` passed).

#### [MODIFY] [run_headless_evaluation.sh](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/run_headless_evaluation.sh)
- Call the validator after each `ONBOARDING.md` generation.
- Propagate non-zero exit codes to fail the evaluation run.

### [Component Name] Prompt Engineering (Issues 12, 13, 15)

#### [MODIFY] [B-prompt.txt](file:///home/rogermt/mcp-repo-onboarding/docs/evaluation/B-prompt.txt)
- Update Step 3/4/5 with explicit rules for phrasing, venv labeling, and install priority (`make install` first).

## Verification Plan

### Automated Tests
- **Python Unit Tests**:
    - `tests/fixtures/python-pin-range/pyproject.toml` (verify empty hints).
    - `tests/test_onboarding_validator.py` (verify V1-V8 pass/fail logic).
- **Integration**:
    - User-run evaluation script must show validator passes for fixed repos.
