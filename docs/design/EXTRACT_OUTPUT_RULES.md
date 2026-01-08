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
These V-rules define only the hard fail conditions; the blueprint may include additional optional sections that the validator tolerates.

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

Additional optional headings (validator-tolerated)
- The validator enforces only the required headings above; it does not fail on additional headings.
- The blueprint may emit additional optional sections for UX as long as:
  - all required headings still exist exactly once and in the required order, and
  - provenance strings are not printed in standard mode (V8).

Currently supported optional heading:
- `## Other tooling detected`
  - Purpose: evidence-only "other ecosystem" signals (e.g., Node.js, Docker).
  - Placement in the standard blueprint: after `## Lint / format` and before `## Analyzer notes` (if present).

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

---

## 7. Notebook-centric detection (P7-01 / Issue #60)

If the analyzer detects any Jupyter notebooks (`*.ipynb`) after safety ignores are applied, it MUST:

1) Append a `notes` entry exactly:

`Notebook-centric repo detected; core logic may reside in Jupyter notebooks.`

2) Populate the `RepoAnalysis.notebooks` field:

`RepoAnalysis.notebooks`: a sorted list of **repo-relative directory paths** containing one or more `*.ipynb` files.

Rules:
- Notebook detection is based on the `.ipynb` file extension only.
- Use normalized repo-relative POSIX paths (`/` separators).
- If a notebook is located at repo root, include the directory as `.`.
- Purely informational (Scout stance):
  - Do NOT assume the notebook kernel language (notebooks may be Python/R/Julia/other).
  - Do NOT prescribe a runner (Kaggle/Colab/local/JupyterLab/etc.).

---

## 8. Framework key symbols (Issue #23)

When `RepoAnalysis.frameworks[]` includes a framework detection, the analyzer MUST attach minimal proof
strings as `frameworks[].keySymbols` (list of strings).

Definitions:
- `keySymbols` may come from pyproject.toml classifiers (preferred when present), e.g. Framework :: Django.

Optional debugging field:
- `frameworks[].evidencePath` (optional): repo-relative POSIX path where the selected key symbol was found.

Scope limits (must remain narrow and cheap):
- Only search for key symbols in a small candidate set of files, e.g.:
  - known entrypoints (`manage.py`, `app.py`, `main.py`, `wsgi.py`, `asgi.py`), and/or
  - a capped list of root-level `.py` files.
- Respect safety ignores and file size limits (size-capped reads).
- No execution, no network.

Determinism:
- If multiple candidate files match, choose deterministically (lexicographically first repo-relative path).
- Within a file, choose the first matching line encountered.

Output rule:
- This proof is stored in MCP JSON only. Do not require or encourage printing `evidence:` in `ONBOARDING.md`
  (validator V8 forbids `evidence:` in standard mode).

key symbol sources may include:
- `pyproject.toml` classifiers (preferred when present), e.g. `Framework :: Django`
- Poetry dependency keys for Poetry-format projects, e.g. `tool.poetry.dependencies.flask`

---

## 9. Phase 10 Analyzer Behavior: Primary Tooling and Node Command Derivation

This section defines **analyzer behavior** only (Phase 10). It does **not** add or modify validator rules.
Validator rules remain frozen at **V1–V8** (Section 1).

### 9.1 Primary tooling (`RepoAnalysis.primaryTooling`)

The analyzer MUST compute and emit an additive field:

`RepoAnalysis.primaryTooling: "Python" | "Node.js" | "Unknown"`

This is a deterministic, evidence-only classification used to support polyglot repositories.

#### 9.1.1 Evidence-only scoring

The analyzer computes two scores from explicit evidence file presence (after safety ignores):

**Python evidence**
- `pyproject.toml` → +10
- `requirements*.txt` → +6
- `setup.py` or `setup.cfg` → +5
- `uv.lock` or `poetry.lock` → +8

**Node.js evidence**
- `package.json` → +5
- any lockfile (`package-lock.json`, `npm-shrinkwrap.json`, `pnpm-lock.yaml`, `yarn.lock`, `bun.lockb`) → +10
- `.nvmrc` or `.node-version` → +3

#### Scoring (Evidence-Only)
The analyzer computes two scores: `python_score` and `node_score` based on explicit file evidence at the repo root or within the directory tree.

| Evidence | Python Score | Node Score |
|----------|---------------|------------|
| `pyproject.toml` (root) | +10 | — |
| `setup.py` (root) | +5 | — |
| `setup.cfg` (root) | +5 | — |
| `requirements*.txt` (any) | +6 | — |
| `uv.lock` (any) | +8 | — |
| `poetry.lock` (any) | +8 | — |
| `.py` files (any) | +1 each (capped) | — |
| `package.json` (root) | — | +5 |
| `pnpm-lock.yaml` (any) | — | +10 |
| `yarn.lock` (any) | — | +10 |
| `bun.lockb` (any) | — | +10 |
| `package-lock.json` (any) | — | +10 |
| `npm-shrinkwrap.json` (any) | — | +10 |
| `.nvmrc` (any) | — | +3 |
| `.node-version` (any) | — | +3 |

Scoring uses only **file presence** (repo-relative paths). No file contents are required for scoring.

#### 9.1.2 Tie-break rule

- If `node_score > python_score` → `primaryTooling = "Node.js"`
- If `python_score > node_score` → `primaryTooling = "Python"`
- If `python_score == 0` and `node_score == 0` → `primaryTooling = "Unknown"`
- If scores tie (non-zero tie) → `primaryTooling = "Python"` (tie-break)

Determinism:
- Evidence is computed from the analyzer’s normalized repo-relative POSIX file list.
- Safety ignores (especially `tests/fixtures/`) apply before scoring.

---

### 9.2 Node.js command derivation (static-only, grounded)

If `primaryTooling == "Node.js"`, the analyzer MAY derive deterministic Node.js commands from explicit evidence and publish them via the existing command surfaces (e.g. `RepoAnalysis.scripts.*`).

This is **static-only**:
- no subprocess calls
- no network calls
- no execution of package managers
- no inferred commands beyond explicit evidence

#### 9.2.1 package.json discovery and parsing (size-capped)

The analyzer may read `package.json` to extract the `scripts` map.

Rules:
- Read is size-capped (e.g., 256 KB max).
- JSON parsing must be failure-safe:
  - malformed JSON must not crash analysis
  - malformed JSON yields “no Node commands derived”
- Deterministic selection when multiple `package.json` files exist:
  - prefer root `package.json` if present
  - otherwise choose lexicographically first repo-relative path

#### 9.2.2 Package manager selection (deterministic)

The analyzer must select a package manager deterministically from explicit evidence:

1) `package.json.packageManager` if present and valid:
   - accepted values (prefix before `@`): `npm`, `pnpm`, `yarn`, `bun`

2) lockfile precedence (preferred to avoid guessing):
   - `pnpm-lock.yaml` → `pnpm`
   - `yarn.lock` → `yarn`
   - `package-lock.json` or `npm-shrinkwrap.json` → `npm`
   - `bun.lockb` → `bun`

If no valid package manager can be selected, the analyzer must not emit Node commands.

Determinism:
- Evidence paths are normalized and compared by basename where applicable.
- Lockfile selection is stable across runs.

#### 9.2.3 Script extraction (evidence-only)

The analyzer may emit commands only for these script keys when explicitly present in `package.json.scripts`:

- `dev`
- `start`
- `test`
- `lint`
- `format`

If the `scripts` map is missing or empty:
- the analyzer must not invent `dev/test/lint/format/start` commands.

#### 9.2.4 Deterministic command generation

Derived commands:

**Install**
- npm:
  - `npm ci` if a lockfile exists (`package-lock.json` or `npm-shrinkwrap.json`)
  - otherwise `npm install`
- pnpm:
  - `pnpm install`
- yarn:
  - `yarn install`
- bun:
  - `bun install`

**Scripts**
- For each supported script key `k` present:
  - `<pm> run <k>`
  - Examples:
    - `pnpm run dev`
    - `npm run test`
    - `yarn run lint`

Descriptions must be deterministic and neutral:
- Install:
  - `Install dependencies using the detected Node.js package manager.`
- Script commands:
  - `Run the '<script>' script from package.json.`

No additional advice (e.g., “install Node 20”) may be emitted unless it is explicit evidence and is surfaced as evidence-only, not as a command.

#### 9.2.5 Interaction with blueprint / validator

This EXTRACT_OUTPUT_RULES section governs analyzer behavior only.
Blueprint rendering may choose how to surface these commands under the existing required headings,
but validator rules (V1–V8) remain unchanged.

#### 9.2.6 Node-primary environment setup messaging (blueprint behavior)

While Phase 10 rules in this section primarily define analyzer behavior, the standard blueprint
is expected to keep ONBOARDING.md messaging consistent with `primaryTooling`.

If `RepoAnalysis.primaryTooling == "Node.js"`, the blueprint should not print Python-first
version-pin messaging by default. Instead:

- If `.nvmrc` and/or `.node-version` are present (evidence-only), print:
  - `Node version pin file detected: <.nvmrc/.node-version/...>.`
- Otherwise print:
  - `No Node.js version pin file detected.`

Additionally, for Node-primary repos the blueprint must not emit a generic Python venv snippet
unless Python is explicitly the primary tooling (see validator V4 for venv labeling requirements).

---

### 9.3 Examples

#### Example A: Node-primary repo (nanobanana-like)

Evidence:
- `package.json` present
- `package-lock.json` present
- no Python dependency manifests

Results:
- `primaryTooling = "Node.js"`
- derived install command:
  - `npm ci`
- derived scripts (only if present in package.json):
  - `npm run dev` / `npm run test` / etc.

#### Example B: Python-primary repo with frontend (wagtail-like)

Evidence:
- `pyproject.toml` present
- `requirements*.txt` present
- `client/package-lock.json` present

Results:
- `primaryTooling = "Python"` (Python score outweighs Node or tie-break)
- Node commands are not derived unless explicitly enabled and `primaryTooling == "Node.js"`
- Node presence may still be reported via evidence-only “other tooling detected” signals.
