# Changelog

## v0.1.0

### Scope
- Python-first onboarding generation (validator-compliant, deterministic output).

### Added
- Framework detection improvements:
  - Detect Streamlit and Gradio from `requirements*.txt` (evidence-based).
- Polyglot awareness (evidence-only):
  - “Other tooling detected” section surfaces secondary tooling based on evidence files only.
  - Evidence lists are deterministically sorted and truncated with explicit wording.
- Onboarding readability improvements:
  - Notebook directory listings are deterministically capped with a truncation note.
- Python-only scope guard:
  - When Python tooling is not detected, ONBOARDING includes a neutral note indicating Python-only scope.

### Changed
- Bash script descriptions:
  - Improved deterministic fallback descriptions for common helper scripts (prevents “No description provided by analyzer.” in common cases).

### Notes
- No non-Python commands are suggested (no npm/yarn/pnpm instructions).
- No subprocess execution; no network calls.

### Next
- Phase 10: non-Python-primary onboarding (e.g., Node-first repos), including primary tooling selection.
