# Plan: Eliminate Generic Virtualenv Instructions (Issue #15)

## Objective
Remove the ungrounded `python -m venv .venv` instruction from the `analyze_repo` output. Environment setup instructions must only be emitted if grounded in repository artifacts (docs, Makefiles, etc.).

## Analysis
Currently, `src/mcp_repo_onboarding/analysis.py` unconditionally adds a generic virtualenv creation instruction whenever Python files or dependency files are detected:

```python
# Env Setup
env_instructions.append(
    "Create a virtualenv: `python -m venv .venv` and activate it (`source .venv/bin/activate` on Unix, `.venv\\Scripts\\activate` on Windows)."
)
```

This violates the "extract, don't advise" contract.

## Proposed Changes

1.  **Modify `src/mcp_repo_onboarding/analysis.py`**:
    *   Remove the unconditional `env_instructions.append(...)` call in `analyze_repo`.
    *   Initialize `env_instructions` as an empty list.
    *   (Future/Phase-6 Feature) In later iterations, we might parse `README.md` or `CONTRIBUTING.md` for specific setup steps, but for now, **silence is correct** if no explicit instruction is found.

2.  **Update Tests (`tests/test_analysis.py`)**:
    *   Update `test_python_env_derivation` to **assert that the generic instruction is NOT present**.
    *   Ensure that `pip install` instructions derived from `requirements.txt` are still preserved (as those are grounded in the file existence).

## Verification Plan

1.  **Reproduction**: Run `uv run pytest tests/test_analysis.py` (expect failure after change if tests aren't updated, or verifying current behavior first).
2.  **Implementation**: Apply the changes to `analysis.py`.
3.  **Validation**: Update and run `tests/test_analysis.py`.
    *   Check `searxng` fixture (or similar) to ensure `envSetupInstructions` is empty or only contains grounded steps.
4.  **Regression Check**: Ensure other fields (`dependencyFiles`, `install` commands) remain correct.

## Outcome
The `analyze_repo` tool will no longer invent environment setup steps. This aligns with Phase 6 correctness goals.
