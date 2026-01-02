# Phase 8 — Refinement, Determinism Hardening, and Maintainability

## 0. Status

Phase 7 is complete and signed off:
- Analyzer behavior is governed by `docs/design/EXTRACT_OUTPUT_RULES.md` (filtering, classification boundaries, ranking, truncation notes).
- `docs/evaluation/validate_onboarding.py` enforces the V1–V8 output contract.
- Safety ignores are strict (especially `tests/fixtures/`).
- 5/5 evaluation suite previously passed end-to-end.

Phase 8 is a **refinement phase**: reduce technical debt, lock determinism harder, improve packaging/UX hygiene, and prepare safe seams for future configuration—without breaking the Phase 7 contract.

---

## 1. Phase 8 Goals

1) **Determinism as a product guarantee (P0)**
   - Enforce global sort rule everywhere: `(score DESC, path ASC)` before any truncation.
   - Add regression tests proving identical JSON output across repeated runs.

2) **Maintainability (P1)**
   - Remove “LLM-cheat” code patterns (giant `if/elif` ladders) by converting to registry-based scoring.
   - Centralize file classification into a single source of truth (eliminate overlapping sets and downstream guard hacks).
   - Reorganize tests for discoverability and long-term maintenance.

3) **Extensibility with safety locks (P1)**
   - Add `EffectiveConfig` scaffolding (defaults ⊕ overrides) with **no behavior change** in Phase 8.
   - Overrides must never bypass Safety Ignore Rules (Section 2 of `EXTRACT_OUTPUT_RULES.md`).

4) **Neutral secondary tooling signals (P2)**
   - Add “Other tooling detected” plumbing that can support Node presence detection neutrally (no commands, no version guessing).
   - Keep the project stance aligned with `REQUIREMENTS.md`: Python-focused; secondary tooling signals are allowed only as neutral context.

5) **UX hygiene + distribution (P1/P2)**
   - Centralize `ONBOARDING.md` backups into a dedicated archive directory instead of polluting repo root.
   - Package as a Gemini CLI extension for easier installation.

---

## 2. Strategic Themes

### 2.1 Contract-First Development (P0)
**Rule:** Analyzer changes must remain compliant with:
- `docs/design/EXTRACT_OUTPUT_RULES.md` (Sections 2–5 especially)
- Validator contract V1–V8 (`validate_onboarding.py`)

No refactor is “just internal” if it can change ordering, truncation notes, or list membership. Phase 8 refactors must include tests that prove no drift.

---

### 2.2 Determinism Hardening (P0)
**Why:** The extractor’s value depends on repeatability. Tie cases must be resolved the same way every time.

Key contract from `EXTRACT_OUTPUT_RULES.md`:
- Rank first, cap second
- Global sort: `(score DESC, path ASC)`
- Tie-break by path ascending

Tracked issue:
- **#79** Determinism hardening — stable tie-break sorting and regression tests.

---

### 2.3 Maintainability: Replace Branch Ladders with Registries (P1)
**Why:** The `if/elif` ladder pattern is brittle, hard to review, and easy for contributors/LLMs to “cheat” into.

Tracked issue:
- **#77** Refactor `prioritization.py` to registry-driven scoring.

---

### 2.4 Data Model Cleanup: Single Source of Truth for Classification (P1)
**Why:** Overlapping sets cause confusion and guard code. The rules require strict boundaries:
- Dependency files must never appear in configuration list.

Tracked issue:
- **#78** Config cleanup — single source of truth for file classification.

---

### 2.5 Extensibility Without Drift: EffectiveConfig (P1)
**Why:** Users will want overrides eventually, but Phase 8 must not change behavior. This is scaffolding only.

Hard requirement:
- Safety ignores (Section 2) must be applied *before* any config override logic.
- `tests/fixtures/` ignore can never be disabled.

Tracked issue:
- **#80** Phase 8 scaffold — EffectiveConfig layering for future overrides.

---

### 2.6 Secondary Tooling Signals (P2)
**Why:** Some repos are Python-first but not Python-only. We can report secondary tooling *neutrally* without suggesting commands.

Alignment note (important): `REQUIREMENTS.md` states “Python-only” scope, but explicitly allows non-Python signals only when they help avoid misleading impressions. So Phase 8 work here is **plumbing + neutral reporting only**.

Tracked issues:
- **#81** Polyglot foundations — “Other tooling detected” signal plumbing.
- **#12** Neutral detection of secondary tooling (Node.js presence)

---

### 2.7 UX Hygiene + Installability (P1/P2)
Tracked issues:
- **#74** Cleanup: Centralize and manage ONBOARDING.md backup files
- **#75** Feature: Enable installation as a Gemini CLI Extension

---

### 2.8 Test Suite Maintainability (P1)
Problem: tests are harder to navigate as the suite grows.

Tracked issue:
- **#73** Refactor: Reorganize test directory to mirror src structure

---

## 3. Phase 8 Backlog and User Stories

### P8-01 (P0): Determinism hardening
**As a** maintainer, **I want** stable ordering and identical output across runs **so that** evaluation and user experience are reliable.
Issue: **#79**

Acceptance criteria:
- Sorting uses `(score DESC, path ASC)` consistently for all ranked lists.
- Add regression test: run analysis twice on same fixture → deep-equal JSON.
- All tests + validator suite pass with no output drift.

---

### P8-02 (P1): Registry-driven prioritization refactor
**As a** maintainer, **I want** prioritization rules expressed as registries **so that** scoring changes are obvious and reviewable.
Issue: **#77**

Acceptance criteria:
- No behavior drift relative to `EXTRACT_OUTPUT_RULES.md` ranking buckets.
- Root-vs-nested dominance remains intact.
- Tests prove scores/order for representative paths (docs/config/deps, root/docs/nested, deprioritized folders).
- No reintroduction of large `if/elif` scoring ladders.

---

### P8-03 (P1): Classification single source of truth
**As a** maintainer, **I want** file classification encoded once **so that** dependency/config/doc boundaries can’t drift.
Issue: **#78**

Acceptance criteria:
- Dependency files never appear in `configurationFiles` (hard rule).
- Code no longer relies on “overlap guards” to fix inconsistent config data.
- All tests + validator suite pass.

---

### P8-04 (P1): EffectiveConfig scaffolding
**As a** future user, **I want** override capability **so that** nonstandard repo layouts can surface their true entrypoints.
Issue: **#80**

Acceptance criteria:
- With defaults only, output is identical to current baseline.
- Safety ignores remain absolute and cannot be overridden.
- Determinism preserved (no env-dependent behavior).

---

### P8-05 (P2): “Other tooling detected” plumbing (+ Node neutral detection)
**As an** agent, **I want** neutral secondary tooling context **so that** onboarding doesn’t falsely imply “pure Python”.
Issues: **#81**, then **#12**

Acceptance criteria:
- Adds a neutral output field for other tooling detections (optionally with evidence file paths).
- No commands emitted, no version inference beyond explicit pins.
- Fully static and deterministic; safety ignores respected.

---

### P8-06 (P1): Centralize onboarding backups
**As a** user, **I want** backups stored in `.onboarding_archive/` **so that** the repo root isn’t polluted.
Issue: **#74**

Acceptance criteria:
- Backups written under `.onboarding_archive/` (auto-created).
- `.gitignore` updated.
- Tests updated.

---

### P8-07 (P2): Gemini CLI extension packaging
**As a** user, **I want** extension-based installation **so that** setup is one-step and repeatable.
Issue: **#75**

Acceptance criteria:
- `gemini-extension.json` exists and is packaged correctly.
- Paths/entrypoints work post-install.
- No changes to analysis semantics.

---

### P8-08 (P1): Restructure tests to mirror src layout
**As a** maintainer, **I want** tests organized by module **so that** it’s obvious what covers what.
Issue: **#73**

Acceptance criteria:
- `tests/` mirrors `src/mcp_repo_onboarding/` structure.
- `uv run pytest` passes.
- Any path-based fixtures/imports updated.

---

## 4. Execution Sequence

1) **#79 Determinism hardening** (build the safety net first)
2) **#77 Prioritization refactor** (now protected by determinism tests)
3) **#78 Config cleanup** (simplify classification safely)
4) **#73 Test reorg** (improves future velocity; low product risk)
5) **#80 EffectiveConfig scaffolding** (no user-facing change)
6) **#81 → #12 Tooling plumbing and Node detection** (neutral, evidence-based)
7) **#74 Backups archive** (UX hygiene)
8) **#75 Gemini extension packaging** (distribution)

---

## 5. Definition of Done for Phase 8

Phase 8 is complete when:

- [x] **Determinism is proven**: stable sort + regression tests merged (**#79**).
- [x] `prioritization.py` uses a registry pattern and preserves scoring contract (**#77**).
- [x] Classification is centralized; dependency/config boundaries are enforced structurally (**#78**).
- [ ] Tests are reorganized and remain green (**#72**).
- [ ] `EffectiveConfig` seam exists; defaults produce identical output; safety ignores cannot be bypassed (**#80**).
- [ ] Neutral tooling signal plumbing exists; Node detection remains command-free and non-inferential (**#81**, **#12**).
- [x] Backups are archived and gitignored (**#74**).
- [x] Extension packaging works without changing analyzer semantics (**#75**).
- [ ] Full evaluation suite continues to pass validator rules V1–V8 with zero regressions.

---

## 6. Phase 8 Code Quality Gates (Non-negotiable)

To prevent “LLM shortcut” regressions (like reintroducing `if/elif` ladders in scoring code), Phase 8 PRs must be blocked by automation:

- Linting/formatting enforced in CI (Ruff).
- Complexity/branch limits enabled (reject giant branch ladders).
- CODEOWNERS required review for core analysis modules (prioritization, scanning, structs, contract docs).
- CI required for merge (tests + lint + validator smoke).

(Exact implementation is a Phase 8 task if not already present; it supports every issue above.)

---

## 7. Phase 9 Preview

- User config parsing (`.onboardingrc` or `pyproject.toml`) using the `EffectiveConfig` seam.
- Expanded neutral secondary tooling signals (still no commands).
- IDE/MCP client diagnostics improvements.

---
