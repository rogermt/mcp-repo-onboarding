# Issue #11: Use packaging.specifiers to classify version pins vs ranges

## Goal Description
Improve the reliability of Python version reporting by distinguishing between exact version pins (e.g., `==3.11.0`) and compatibility ranges (e.g., `>=3.11`). This ensures that ranges are not incorrectly reported as "pinned" versions, adhering to the project's grounding rules.

### Classification Examples

| Input (`requires-python`) | `pythonVersionPin` | `pythonVersionComments` | Logic / Reason |
| :--- | :--- | :--- | :--- |
| `==3.11.0` | `"3.11.0"` | `None` | **Exact Pin**: Uses the `==` operator. |
| `>=3.11` | `None` | `"Requires Python >=3.11"` | **Range**: Lower bound only. Not a pin. |
| `~=3.10.0` | `None` | `"Compatible with 3.10.x"` | **Range**: Tilde-equal is a range. |
| `>=3.9, !=3.9.7, <4` | `None` | `"Requires Python >=3.9, <4"` | **Complex Range**: Multiple specifiers. |
| `3.10` | `"3.10"` | `None` | **Implicit Pin**: No operator provided. |
| `*` | `None` | `"Any Python version"` | **Wildcard**: Open requirement. |

## Proposed Changes

### [Component Name] Schema

#### [MODIFY] [schema.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/schema.py)
- Add `pythonVersionPin: str | None = None` to `PythonInfo` class.
- Add `pythonVersionComments: str | None = None` to `PythonInfo` class to store range descriptions or context.

### [Component Name] Analysis Logic

#### [NEW] [utils.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/utils.py)
- Implement `classify_python_version(version_hint: str) -> tuple[str | None, str | None]`
- Use `packaging.specifiers.SpecifierSet` to parse the version hint.
- If a hint contains an exact pin (`==`), return it as the pin.
- Otherwise, return a descriptive comment about the range (e.g., "Requires Python >= 3.11").

#### [MODIFY] [core.py](file:///home/rogermt/mcp-repo-onboarding/src/mcp_repo_onboarding/analysis/core.py)
- Update `_infer_python_environment` to process all collected `pythonVersionHints`.
- Call `classify_python_version` for each hint.
- Prioritize exact pins. If multiple pins exist, choosing the most specific or latest one (or listing them).
- If no pin is found, populate `pythonVersionComments` with the summarized range requirements.

## Verification Plan

### Automated Tests
- Create a new test file `tests/test_version_classification.py`.
- Tests cases:
    - `requires-python = "==3.11.0"` -> `pythonVersionPin="3.11.0"`
    - `requires-python = ">=3.11"` -> `pythonVersionPin=None`, `pythonVersionComments="Requires Python >=3.11"`
    - Multiple hints: `["3.11", ">=3.10"]` -> prioritize the most specific.
    - Malformed specifiers should be handled gracefully.
- Run `uv run pytest`.

### Manual Verification
- Verify the output of `analyze_repo` on real-world repositories with ranges vs pins.
