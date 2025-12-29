# Phase 7 — Domain Specialization & UX Automation

## 0. Status

Phase 6 is complete and signed off:
- Python-native implementation is hardened.
- `pathspec` ignore handling is operational.
- Deterministic validator (`validate_onboarding.py`) gates all evaluation runs.
- Token savings are verified at ~80% reduction.

Important clarity:
- **The Scout (MCP):** Provides grounded JSON based on [EXTRACT_OUTPUT_RULES.md](../design/EXTRACT_OUTPUT_RULES.md).
- **The Agent (LLM):** Generates prose that must pass the Phase 6 Validator invariants.

---

## 1. Phase 7 Goals

Transform the "Hardened Extractor" into a "Domain Specialist" that understands the repository structure and culture (Data Science vs. Engineering) while automating the user experience.

Phase 7 focuses on:
1) **Signal Hierarchy:** Prioritize root and `/docs` files while suppressing test/fixture noise.
2) **UX Automation:** Eliminate copy-pasting by exposing the B-Prompt as a server resource.
3) **Research Awareness:** Identify "notebook-centric" repositories (Paper2Code style).
4) **High-Fidelity Proof:** Attach verbatim "Key Symbols" to framework detections.

---

## 2. Phase 7 Strategic Themes

### 2.1 Relevance & Noise Suppression (P0)
**Problem:** Our own repository analysis is currently polluted by 60+ requirements files from test fixtures, drowning out the root signals.
**Fix:** Implement Rule **R1-R3** from `EXTRACT_OUTPUT_RULES.md` (Root > Docs > Nested > Fixture Penalty).

### 2.2 UX Automation (P0)
**Problem:** Users must manually copy and paste grounding rules from a text file.
**Fix:** Expose `/generate_onboarding` (Prompt) and `get_onboarding_template` (Tool) via the MCP server to provide the validated Phase 6 prompt directly.

### 2.3 Research & Data Science Mastery (P1)
**Problem:** Research repos often lack standard entrypoints, causing the analyzer to report "No commands detected."
**Fix:** Add heuristics to detect `.ipynb` density and specifically identify `nbstripout` hygiene in pre-commit configs.

---

## 3. Backlog & User Stories

### P7-05: The Prompt Resource (UX)
**As an** interactive user, **I want** a stable onboarding template available as a prompt and tool **so that** I don't have to manually manage prompt files.
- Expose `/generate_onboarding` (Prompt).
- Expose `get_onboarding_template` (Tool).
- Return the full text of the validated B-Prompt.

### P7-07: Location-Aware Scoring (Relevance)
**As a** user, **I want** the 10-item cap to be filled with high-value root and documentation files **so that** I don't see test fixtures in the summary.
- Implement scoring: Root (`+100`), Docs (`+80`), Fixtures (`-200`).
- Apply sorting to all lists before truncation.

### P7-01/02: Notebook Centricity (Research)
**As a** data scientist, **I want** the tool to recognize that my project lives in notebooks **so that** the onboarding guidance is appropriate for Jupyter/Colab.
- Detect `.ipynb` density and surface a "Notebook-centric repo" signal.
- Detect `nbstripout` in pre-commit to prove notebook hygiene.

### P7-03/04: High-Fidelity Signal (Hardening)
**As an** agent, **I want** to see "Key Symbols" and secondary tooling signals (Node.js) **so that** my mental map of the repo is 100% accurate.
- Include `"evidence": "from fastapi import FastAPI"` in framework JSON.
- Detect presence of `.nvmrc` or `package.json` to signal Node.js presence.

---

## 4. Execution Sequence

1.  **Hardening the Contract:** Create `EXTRACT_OUTPUT_RULES.md` and synchronize all project docs.
2.  **Cleaning our House:** Implement **P7-07** (Relevance Scoring) to fix our own repo's output.
3.  **Standardizing UX:** Implement **P7-05** (Prompt Resource).
4.  **Domain Specialization:** Implement **P7-01/02** (Notebooks) and **P7-03/04** (Evidence).

---

## 5. Definition of Done for Phase 7

Phase 7 is complete when:
- [x] `EXTRACT_OUTPUT_RULES.md` is the single source of truth.
- [x] Our own repo onboarding is noise-free (no fixture pollution in top-10).
- [x] The `generate_onboarding` prompt and `get_onboarding_template` tool are functional.
- [x] All 5 evaluation repos pass the deterministic validator with 0 regressions.
- [ ] Notebook-centric repos (Paper2Code) are correctly identified as such.

---

## 6. Phase 8 Backlog (Future)
- Support for multiple languages beyond Python as primary signals.
- Custom user-defined prioritization rules via `.onboardingrc`.
- Integration with VS Code / IDE extensions.
