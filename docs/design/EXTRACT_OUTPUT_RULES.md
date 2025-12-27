# EXTRACT_OUTPUT_RULES

This document is the **single source of truth** for:

1) **ONBOARDING.md output validation contract** (Phase 6; deterministic pass/fail rules V1–V8)
2) **Analyzer behavior** (Phase 7; safety ignore filtering, classification boundaries, ranking before caps, truncation notes)
3) **Analyzer enrichment rules** (e.g., pre-commit notebook hygiene detection)

Project stance: **High-Signal Scout**
- Deterministic, compact, grounded signals.
- Static analysis only (no code execution, no shell, no git commands, no network).

---

## 0. Sources of truth and anti-drift rule

### Validator contract (Phase 6)
- Enforced by: `docs/evaluation/validate_onboarding.py`
- The rules V1–V8 below define what is considered a valid `ONBOARDING.md`.

### Analyzer behavior (Phase 7)
- Implemented in analysis code under `src/mcp_repo_onboarding/analysis/`.
- The rules in Sections 2–4 govern file filtering, classification, and ranking.

### Anti-drift rule
- Do **not** invent new “V-rules” for ranking or heuristics.
- V-rules are **validator** rules only (hard fail conditions in `validate_onboarding.py`).
- Ranking, prioritization, and selection logic belongs only in the analyzer rules in this file.

---

## 1. ONBOARDING.md Validator Contract (V1–V8)

These are deterministic rules enforced by `docs/evaluation/validate_onboarding.py`. If violated, validation fails and the evaluation run fails.

### V1 — Required headings must exist (exact)

`ONBOARDING.md` must contain these headings (exact spelling/case), once each, in this order:

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

Notes:
- `## Analyzer notes` is optional and must only appear if notes are present (see V6).

Fail if:
- a heading is missing
- a heading uses a different name (e.g., `## Environment`)
- headings appear as bullet items instead of `##` headings
- headings are out of order

### V2 — Repo path line must be present

Immediately after `## Overview`, there must be a line:

`Repo path: <non-empty>`

Fail if:
- missing
- empty path
- uses `Repository:` as a heading/title

### V3 — “No pin” must be exact and not prefixed

If `ONBOARDING.md` includes `No Python version pin detected.` it must appear as a standalone sentence, not prefixed with `Python version:`.

Fail if:
- a line matches `Python version: No Python version pin detected.`

(Validator does not need to know repo pin state; it only checks this forbidden pattern.)

### V4 — Venv snippet labeling

If `ONBOARDING.md` contains venv commands, the snippet must be labeled as generic.

Detect venv snippet if either appears anywhere:
- `python -m venv .venv` OR
- `python3 -m venv .venv`

Then require:
- a line containing `(Generic suggestion)` within the preceding 3 lines.

Fail if:
- venv snippet exists without generic suggestion label nearby.

### V5 — Command formatting in command sections

In these sections:
- Install dependencies
- Run / develop locally
- Run tests
- Lint / format

Any bullet line that contains a command must:
- wrap the command in backticks (e.g., `` `tox` ``)
- if a description exists, it must be in parentheses immediately after the command (e.g., `` `tox` (Run tests via tox.) ``)

Fail if:
- a command appears without backticks (e.g., `* tox`)
- a description is present but not parenthesized (e.g., `` `tox` Run tests via tox ``)

### V6 — Analyzer notes section policy

If `## Analyzer notes` exists, it must contain at least one bullet note line (non-empty).
If `## Analyzer notes` exists and contains text like `(empty)` or is blank, fail.

(Validator does not attempt to infer whether notes should exist; it only enforces “if present, it must not be empty”.)

### V7 — Install policy: prevent invented multi-requirements installs

Fail if `ONBOARDING.md` includes more than one `pip install -r ...` line.

Rationale:
- Prevents invented multi-subproject installs (e.g., Connexion examples) until explicit MCP-provided install command support exists.

### V8 — No provenance printed by default

If `SHOW_PROVENANCE=false` is the standard mode, then in standard evaluation runs provenance must not be printed.

Fail if `ONBOARDING.md` contains:
- `source:`
- `evidence:`

If running a provenance debug mode, the validator may be invoked with `--allow-provenance`.

---

## 2. Safety Ignore Rules

Before any file is classified, counted, ranked, read, or returned in output lists, it **MUST** pass the safety ignore check.

If a path matches a safety ignore rule, it is **invisible** to the system (including targeted signal discovery).

### 2.1 Hardcoded safety ignore blocklist

Ignore any path that is:
- under `tests/fixtures/` or `test/fixtures/` (critical for self-analysis pollution control)
- under `.git/`, `.hg/`, `.svn/`
- under `node_modules/`
- under any virtualenv: `.venv/`, `venv/`, `env/`
- under `site-packages/`
- cache/artifacts: `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.coverage`
- build artifacts: `dist/`, `build/`

Implementation requirements:
- Matching is performed on **normalized repo-relative POSIX paths** using `/` separators.
- Safety ignore is applied **before** any “targeted discovery” override logic.

---

## 3. Classification Boundaries

These categories must not be mixed.

### 3.1 Dependency files (`python.dependencyFiles`)
Examples:
- `requirements*.txt`, `constraints*.txt`
- `pyproject.toml`
- `Pipfile`, `environment.yml`, `environment.yaml`
- `setup.py`, `setup.cfg`

### 3.2 Configuration files (`configurationFiles`)
Examples:
- `Makefile`, `Justfile`
- `tox.ini`, `noxfile.py`, `pytest.ini`
- `.pre-commit-config.yaml`
- `.github/workflows/*.yml`

### 3.3 Docs (`docs`)
Examples:
- `README*`, `CONTRIBUTING*`, `LICENSE*`, `SECURITY*`
- `docs/**` documentation pages

Hard rule:
- Dependency files must **NEVER** appear in the configuration list.

---

## 4. Ranking and Truncation

All capped lists must use deterministic ranking:
- **rank first**
- **cap second**
- tie-break by path ascending

Global sort rule:
- sort by `(score DESC, path ASC)`

### 4.1 Docs ranking (cap default: 10)

Docs candidates are scored by bucket:

- **+300 Root standards**
  - repo-root: `README*`, `CONTRIBUTING*`, `LICENSE*`, `SECURITY*`

- **+250 Primary docs folder**
  - files directly under `docs/` (e.g., `docs/index.md`)

- **+200 Onboarding keywords**
  - path contains (case-insensitive): `quickstart`, `install`, `setup`, `tutorial`

- **+150 Nested docs**
  - files deeper in `docs/` (e.g., `docs/api/v1/...`)

- **+0 General docs**
  - other valid doc candidates

- **-100 Deprioritized locations**
  - doc candidates under any of: `tests/`, `test/`, `examples/`, `scripts/`, `src/`

After scoring:
- sort by `(score DESC, path ASC)`
- keep first 10
- if truncated, add analyzer note: `docs list truncated to 10 entries (total=<total>)`

### 4.2 Configuration ranking (cap default: 15)

Configuration candidates are scored by bucket:

- **+300 Drivers**
  - `Makefile`, `Justfile`

- **+200 Test/lint tooling**
  - `tox.ini`, `noxfile.py`, `.pre-commit-config.yaml`, `.pre-commit-config.yml`, `pytest.ini`, `pytest.cfg`

- **+150 CI workflows**
  - `.github/workflows/*.yml` / `.yaml`

- **+0 Other config**

After scoring:
- sort by `(score DESC, path ASC)`
- keep first 15
- if truncated, add analyzer note:
  `configurationFiles list truncated to 15 entries (total=<total>)`

### 4.3 Dependency files ranking

Dependency files must also be ranked deterministically to prevent nested/example noise from crowding out root signals.

Score buckets:

- **+300 Root manifests**
  - repo-root: `pyproject.toml`, `requirements*.txt`, `Pipfile`,
    `environment.yml`, `environment.yaml`, `setup.py`, `setup.cfg`

- **+150 Nested manifests**
  - same patterns but nested

- **-100 Deprioritized locations**
  - under `tests/`, `test/`, `examples/`, `scripts/`

After scoring:
- sort by `(score DESC, path ASC)`
- apply any caps only after ranking (if caps are introduced later)

---

## 5. Required truncation notes format

If any list is truncated, `## Analyzer notes` must include:

- `docs list truncated to 10 entries (total=<total>)` and/or
- `configurationFiles list truncated to 15 entries (total=<total>)`

(Validator rules control whether `## Analyzer notes` may appear and whether it may be empty.)

---

## 6. Configuration enrichment

Configuration file entries may include a short, neutral `description` to help users understand why a file matters. Descriptions must be deterministic and based only on static repo contents.

### 6.1 Pre-commit notebook hygiene detection (P7-02 / Issue #61)

If a pre-commit configuration file exists:
- `.pre-commit-config.yaml` or `.pre-commit-config.yml`

the analyzer may statically scan its text (size-capped) for notebook hygiene hooks.

If the file contains any of these markers (case-insensitive):
- `nbstripout`
- `nb-clean`
- `jupyter-notebook-cleanup`

then the analyzer must set `configurationFiles[].description` to exactly:

`Pre-commit config for cleaning Jupyter notebooks (e.g. stripping outputs) for cleaner diffs.`

If none of the markers are present, use the standard generic pre-commit description.

Notes:
- This is a neutral detection (Scout stance). Do not imply policy requirements.
- This enrichment must not emit provenance strings (`source:` / `evidence:`) in standard mode.
