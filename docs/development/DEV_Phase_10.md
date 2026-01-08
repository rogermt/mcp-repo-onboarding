# Dev Phase 10 — Non‑Python Primary Onboarding Under Existing Validator Contract

## Context
* `v0.1.0` has shipped.
* Phase 9 is Python‑first release behavior with:
  * framework detection improvements (Streamlit/Gradio evidence‑based)
  * “Other tooling detected” evidence-only
  * caps/truncation formatting for notebooks and tooling evidence
  * Python-only scope message when Python not detected
* Phase 10 expands to support **Node-primary / non‑Python‑primary repos** while keeping the current validator contract **V1–V8** unchanged.

Critical constraint:
* `validate_onboarding.py` requires the exact headings and order in V1. We cannot introduce a Node-specific heading structure without changing the validator (out of scope for Phase 10).

Decision:
* For Node-primary repos: **do not show any Python venv snippet** in `## Environment setup`.

---

## Goals
* Add `primaryTooling` computed deterministically from explicit evidence (static-only).
* For Node-primary repos:
  * Populate the existing sections with **grounded Node commands** derived from `package.json` scripts and lockfiles.
  * Preserve V5 formatting and keep output deterministic.
  * Suppress Python venv snippet when Python is not detected and primary tooling is not Python.
* Preserve all existing behavior for Python-primary repos (no regressions).
* Keep “High-Signal Scout” stance:
  * static analysis only
  * no command invention
  * no shell execution
  * no network calls

---

## Non‑Goals
* SBOM generation, auditing, vulnerability scanning, snapshotting (RERA scope).
* Running package managers (`npm`, `pnpm`, `yarn`, `bun`) or executing any repo code.
* Suggesting commands without explicit evidence.
* Adding new required headings (validator would fail).

---

## Contract (Validator) Compatibility
V1 requires these headings and order:
1. `# ONBOARDING.md`
2. `## Overview`
3. `## Environment setup`
4. `## Install dependencies`
5. `## Run / develop locally`
6. `## Run tests`
7. `## Lint / format`
8. `## Dependency files detected`
9. `## Useful configuration files`
10. `## Useful docs`

Phase 10 will keep the headings exactly the same.
Node-primary support will be implemented as **different content inside the same sections**, not different headings.

---

## Phase 10 Product Behavior

### 1) Primary tooling selection
Add analysis field:
* `RepoAnalysis.primaryTooling: str | None`
  * Values: `"Python"`, `"Node.js"`, `"Unknown"` (string for forward compatibility)

Primary tooling is computed from explicit evidence files only:
* Python evidence:
  * `pyproject.toml`, `requirements*.txt`, `setup.py`, `setup.cfg`, `uv.lock`, `poetry.lock`, `Pipfile`
* Node evidence:
  * `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`, `.nvmrc`, `.node-version`, `.npmrc`

Deterministic scoring:
* Node:
  * `package.json` +5
  * any lockfile +10
  * `.nvmrc`/`.node-version` +3
* Python:
  * `pyproject.toml` +10
  * any `requirements*.txt` +6
  * `setup.py`/`setup.cfg` +5
  * lockfile (`uv.lock`/`poetry.lock`) +8
Tie-break:
* Python wins ties.

### 2) Node commands (grounded only)
Node commands must only be emitted if:
* `package.json` exists (and is readable under size cap), AND
* a package manager is deterministically selected from:
  * `pnpm-lock.yaml` → pnpm
  * `yarn.lock` → yarn
  * `package-lock.json` / `npm-shrinkwrap.json` → npm
  * `bun.lockb` → bun
  * or `package.json.packageManager` if present and valid

Allowed reads:
* `package.json` only (size-capped, deterministic parse)

Derived commands:
* Install:
  * npm → `npm ci` if lockfile present, else `npm install`
  * pnpm → `pnpm install`
  * yarn → `yarn install`
  * bun → `bun install`
* Dev/test/lint/format:
  * from `package.json.scripts` only:
    * `dev`, `start`, `test`, `lint`, `format`
  * commands become:
    * `<pm> run <script>`
Descriptions:
* Deterministic and neutral:
  * “Run the '<script>' script from package.json.”
  * “Install dependencies using the detected Node.js package manager.”

No command invention beyond evidence.
No version inference beyond evidence presence.

### 3) ONBOARDING.md behavior for Node-primary repos (under existing headings)
* `## Environment setup`
  * Node-primary repos should not present Python-first environment messaging by default.
  * If `primaryTooling == "Node.js"`, the blueprint prints a Node.js version pin message:
    * If `.nvmrc` and/or `.node-version` are present (evidence-only), print:
      * `Node version pin file detected: <.nvmrc/.node-version/...>.`
    * Otherwise print:
      * `No Node.js version pin file detected.`
  * **Does NOT print Python venv snippet** when Node is primary.
  * Python version hints may still be printed when explicitly detected (e.g., from CI),
    but Node-primary messaging should remain Node-first.
  * May include neutral Node evidence in Analyzer notes (recommended), not here.
* `## Install dependencies`
  * Node-primary: include grounded Node install command if available; else fallback exact `No explicit commands detected.`
* `## Run / develop locally`, `## Run tests`, `## Lint / format`
  * Node-primary: include grounded Node commands if corresponding scripts exist; else fallback.
* `## Analyzer notes` (optional)
  * Add:
    * `* Primary tooling: Node.js (package.json present).`
    * For repos where primaryTooling is Unknown (neither Python nor Node.js) and Python not detected, show scope note:
      `* Python/Node.js tooling not detected; this release generates onboarding for Python and Node.js repos only.`
  * Keep existing notes/truncations/framework lines.

---

## Implementation Notes

### Where logic lives
* Primary tooling detection lives in analysis code (static evidence).
* Node command extraction lives in analysis code (read `package.json` only).
* Blueprint engine decides whether to show venv snippet based on:
  * `primaryTooling` and Python evidence presence.

### Determinism & Safety
* All reads must be size-capped.
* All lists sorted deterministically.
* Safety ignores apply before any evidence detection.

---

## Test Plan

### Unit tests
* primaryTooling selection:
  * Node-first evidence → Node.js
  * Python-first evidence → Python
  * tie → Python
* package.json parsing:
  * extracts scripts deterministically
  * malformed JSON → no commands, no crash
  * size cap enforced

### Blueprint tests
* Node-primary + Python not detected:
  * no `python -m venv .venv` or `python3 -m venv .venv` in output
  * Node commands appear in correct sections and in V5 format
* Python-primary repos remain unchanged (regression gate)

### Evaluation suite
* Add at least one Node-primary repo (e.g. nanobanana).
* Ensure validator remains green.

---

## Phase 10 Issues

### #P10-1 Feature: Add `primaryTooling` to analysis output
* Add `primaryTooling` field to `RepoAnalysis` schema.
* Implement deterministic evidence-only computation from repo file list.
Acceptance:
* Node-first repo sets `primaryTooling="Node.js"`.
* Python-first repo sets `primaryTooling="Python"`.
* Deterministic across runs.

### #P10-2 Feature: Node command extraction from `package.json` scripts (static-only)
* Read and parse `package.json` (size-capped).
* Select package manager deterministically from lockfiles or `packageManager` field.
* Derive install/dev/start/test/lint/format commands from scripts only.
* Inject derived commands into `RepoAnalysis.scripts` so blueprint remains simple.
Acceptance:
* No scripts → no invented commands.
* Scripts present → commands emitted with deterministic descriptions.
* No subprocess/network calls.

### #P10-3 Refactor: Blueprint env setup suppresses Python venv snippet when Node-primary and Python not detected
* Update blueprint v2 engine environment section:
  * If `primaryTooling != "Python"` and Python evidence absent → do not emit generic venv snippet.
Acceptance:
* Node-primary repo output contains no venv commands and no `(Generic suggestion)` label.
* Python repos unchanged.

### #P10-4 Feature: Onboarding adds “Primary tooling” note (Analyzer notes)
* If `primaryTooling` exists, add a bullet:
  * `* Primary tooling: <tool> (<evidence summary>).`
* Keep it neutral and deterministic.
Acceptance:
* Node-primary repo makes it obvious that Node is primary without breaking headings.

### #P10-5 Docs: Update `EXTRACT_OUTPUT_RULES.md` for Phase 10 analyzer behavior (non-validator)
* Add a section describing:
  * `primaryTooling` computation (evidence-only)
  * Node command derivation rules (scripts-only, lockfile-based pm selection)
* Must not introduce new validator “V-rules”.
Acceptance:
* Rules document updated and consistent with implementation.

### #P10-6 Evaluation: Add Node-primary repos to eval suite
* Add at least one Node-primary fixture/repo (e.g. nanobanana).
* Ensure evaluation remains deterministic and validator passes.
Acceptance:
* Node-primary repo produces validator-compliant ONBOARDING.md with Node commands and no Python venv snippet.

---
