# Dev Phase 9 — Python-Only First Release

## Status
* Phase 8 is signed off once #12 eval is green.
* Phase 9 delivers the first public release: **Python-primary onboarding only**.

## Phase 9 Product Rule
* The product is **Python-first and Python-only**.
* Mixed repos are supported **only** in the sense that we can surface *neutral secondary tooling presence* (from Phase 8: `otherToolingDetected`) without suggesting commands.
* Node-first / non-Python-primary repos are **out of scope** for Phase 9 and will be handled in Phase 10.

---

## Goals
* Ship a correct, deterministic, validator-compliant `ONBOARDING.md` for Python repos.
* Improve Python framework detection for real-world repos that use `requirements.txt` (not just `pyproject.toml`).
* Ensure mixed repos don’t look “pure Python” by surfacing neutral secondary tooling evidence (already supported by Phase 8 plumbing).
* Keep the prompt “UX-only” (no logic in prompt; all structure is code-owned).

## Non-Goals
* No non-Python-primary onboarding (Phase 10).
* No command inference for secondary tooling (no `npm`, `yarn`, `pnpm`, etc.).
* No dynamic execution, no subprocess calls, no network.
* No user overrides parsing (that’s Phase 8+ scaffolding via EffectiveConfig, not user-facing yet).

---

## Scope: What we will build in Phase 9

### 1) Python framework detection improvements (requirements-based)
* Add framework detection from explicit dependency manifests, especially:
  * `requirements.txt` / `requirements-*.txt`
* Add **Streamlit** and **Gradio** as detectable Python frameworks.
* Evidence must be grounded:
  * framework name
  * evidence file path
  * detection reason that references the evidence file

### 2) Python-only release behavior for non-Python repos
* If Python evidence is weak/absent:
  * Still generate a validator-compliant ONBOARDING.md
  * Include a neutral note that this version is Python-only and Python signals were not detected strongly
  * Surface `otherToolingDetected` neutrally (no commands)

### 3) Onboarding rendering refinements (still validator-safe)
* Ensure framework detections appear neutrally (recommended location: `## Analyzer notes`).
* Keep bullet marker stable: `*` only.
* Keep command formatting rules unchanged (backticks + parentheses, or exact fallback line).

---

## Deliverables
* Framework detection supports Streamlit/Gradio (from `requirements*.txt`).
* Updated evaluation suite includes:
  * at least one Streamlit repo (DeepCode)
  * at least one mixed Python + Node repo (chat-langchain)
* Documentation: a short README section describing Phase 9 scope (“Python-only release” and what `otherToolingDetected` means).

---

## Proposed Issues / Tasks

### P9-A: Feature — Detect Streamlit/Gradio via requirements.txt
* Add a requirements parser that extracts package names deterministically.
* Add framework detection rules:
  * `streamlit` -> FrameworkInfo(name="Streamlit")
  * `gradio` -> FrameworkInfo(name="Gradio")
* Wire detection into `analysis/core.py` after dependency files are known.

Acceptance criteria:
* A repo with `requirements.txt` containing `streamlit` yields `frameworks` including `Streamlit`.
* A repo with `requirements.txt` containing `gradio` yields `frameworks` including `Gradio`.
* Reasons are grounded (mention the evidence file).
* Deterministic ordering and no command suggestions.

Tests:
* New unit test: requirements-based framework detection (synthetic repo).
* Update/extend integration eval fixture coverage (DeepCode).

### P9-B: Feature — Python-only scope message when Python not detected
* Add a deterministic “Python-only release” message when Python evidence is absent or extremely weak.
* Placement: `## Analyzer notes` (so validator rules around headings are unaffected).

Acceptance criteria:
* Node-only repo produces ONBOARDING.md that is validator-compliant and explicitly states Python-only scope (neutral).
* No npm/yarn/pnpm command suggestions.
* No change for Python repos.

Tests:
* Synthetic “Node-only repo” test that asserts message appears and no Node commands appear.

### P9-C: Maintenance — Evaluation suite updates for Phase 9
* Add/update eval repos:
  * DeepCode (Streamlit detected)
  * chat-langchain (Node detected as other tooling, still Python onboarding)

Acceptance criteria:
* Eval remains green and deterministic.
* Outputs reflect the new framework detection and neutral tooling notes.

### P9-D: Docs — Phase 9 release notes
* Document:
  * Python-only scope
  * what “Other tooling detected” means (evidence-only)
  * what is deferred to Phase 10 (non-Python-primary onboarding)

---

## Technical Design Notes

### Evidence-first only
* All detections must be based on explicit evidence files.
* Requirements parsing is allowed (static file reads, size-capped).
* No heuristics that imply commands.

### Determinism rules
* Apply size caps to any file reads (`requirements.txt`, etc.).
* Normalize and sort output lists.
* Deduplicate by stable keys (framework name, evidence path).

### Validator compatibility
* Do not change required headings order.
* If adding new content, prefer:
  * `## Analyzer notes` (optional, but if present must be non-empty)
* Do not introduce new headings unless validator explicitly allows extra headings.

---

## Testing & Gates

### Unit tests
* Requirements parsing:
  * handles comments, blank lines, env markers (`; python_version...`)
  * ignores `-r`, `--requirement`, `-c`, VCS URLs
* Framework detection:
  * Streamlit/Gradio present -> detected
  * not present -> not detected

### Integration tests
* DeepCode fixture or eval repo:
  * frameworks include Streamlit
* chat-langchain:
  * `otherToolingDetected` includes Node evidence
  * onboarding stays Python-first and doesn’t suggest Node commands

### Standard gates
* `uv run pytest`
* `uv run mypy src/mcp_repo_onboarding`
* `uv run ruff check .`
* `uv run --project . python scripts/validate_onboarding.py`
* Evaluation suite must be green (target: 5/5).

---

## Release Checklist (Phase 9)
* Python-only onboarding quality is acceptable for at least:
  * typical library repo (pyproject)
  * typical app repo (requirements + setup.py)
  * Streamlit repo (DeepCode)
* Determinism verified on eval repos.
* Validator passes.
* README updated: clearly states Phase 9 scope and Phase 10 roadmap.

---

## Risks & Mitigations

### Risk: requirements parsing edge cases
* Mitigation:
  * conservative parser (extract only leading distribution name)
  * ignore non-standard lines (`-r`, VCS, paths)
  * size cap and error-tolerant reads

### Risk: framework detection causes noise
* Mitigation:
  * only detect frameworks for high-signal packages (Streamlit/Gradio)
  * keep output neutral, no commands

### Risk: mixed repos confuse users
* Mitigation:
  * keep neutral “Other tooling detected” evidence list
  * keep Python-only scope explicit when Python is not strongly present

---

## Phase 10 Preview (Out of Scope)
* Introduce `primaryTooling` computed from evidence.
* Generate onboarding that is correct for Node-primary repos (and others).
* Potentially add grounded Node commands from `package.json` scripts (still deterministic).
