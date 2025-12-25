# Gap Analysis Report: ONBOARDING.md Regressions

Following the latest evaluation run, here is a breakdown of the current state of generated onboarding signals. This analysis serves as the technical justification for Issues 53-57.

## 🟢 The Good (Stable & Accurate)
- **Exact Pin Grounding**: `searxng` successfully grounded `PYTHON_VERSION: "3.14"` from GitHub workflows.
- **Standalone Phrasing**: `imgix-python` correctly rendered `No Python version pin detected.` as a standalone sentence without the "Python version:" prefix.
- **Section Order**: All outputs followed the required heading sequence correctly.

## 🟡 The Bad (Formatting & Consistency)
- **Forbidden Prefixes**: `Paper2Code` produced `Python version: No Python version pin detected.`, violating the requirement for a standalone exact phrase (Issue 54).
- **Venv Visibility**: Both `searxng` and `Paper2Code` included standard venv creation snippets without the `(Generic suggestion)` label, making them appear as "detected" commands (Issue 55).
- **Command Bullets**: Descriptions were often missing parentheses (e.g., `make test - Run...`), and backtick usage was inconsistent (Issue 56/V5).

## 🔴 The Ugly (Critical Regressions)
- **Range vs Pin**: `wagtail` correctly found `requires-python = ">=3.10"` but incorrectly reported it as `Python version: >=3.10`. Ranges are NOT pins and must be rejected to maintain grounding integrity (Issue 53).
- **Invented Install Paths**: `connexion` included multiple `pip install -r` commands from various example subdirectories. This creates noise and violates the "primary install path" policy (Issue 57).
- **Description Drift**: `imgix-python` rendered `* tox Run tests via tox` with no delimiters, reducing readability and programmatic parseability.

---

## Conclusion
The current signals have drifted from the project contract. **Issue 56 (The Validator)** is the critical gatekeeper required to prevent these regressions from reaching production. **Issue 53** is the priority logic fix to restore version grounding.
