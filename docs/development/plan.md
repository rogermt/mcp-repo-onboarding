# Phase 7: Technical Implementation Plan (Issue #64)

## 🛡️ Protected Files (Do Not Touch)
To maintain the Phase 6 contract and Senior Lead authority, the following files are **STRICTLY OUT OF SCOPE** for modification:
- `docs/evaluation/validate_onboarding.py` (Canonical Phase 6 V1–V8 validator).
- `docs/design/EXTRACT_OUTPUT_RULES.md` (Senior Lead-owned rules definition).

---

## 1. Safety Ignore Rules (IgnoreMatcher)
**Goal**: Any path matching safety ignore is invisible, including targeted discovery. **No code path can bypass `is_safety_ignored()`**.

### 1.1 Add “Safety Ignore” Layer
- **Location**: `src/mcp_repo_onboarding/analysis/structs.py` (within `IgnoreMatcher`)
- **Action**: Add `is_safety_ignored(self, path: str) -> bool`.
- **Blocklist (Repo-relative POSIX)**:
    - `tests/fixtures/`, `test/fixtures/`
    - `.git/`, `.hg/`, `.svn/`
    - `node_modules/`
    - `.venv/`, `venv/`, `env/`, `site-packages/`
    - `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.coverage`
    - `dist/`, `build/`
- **File Matching**: Ensure `.coverage` (and similar entries) matches both as a root file and as a substring `/.coverage` to catch it in nested locations.

### 1.2 Enforce Safety Across ALL Paths
- **Constraint**: Every analysis path—including initial repo-walk enumeration, targeted detection for known files (`pyproject.toml`, `Makefile`, workflows), and any “parse this file” step—MUST check `is_safety_ignored()` first.
- **Rule**: Safety ignore beats targeted discovery; `.gitignore` does not.

### 1.3 Path Normalization
- **Action**: Centralize Path → repo-relative POSIX string conversion.
- **Constraint**: Use directory-prefix checks with trailing slash semantics (e.g., `rel_path.startswith("tests/fixtures/")`).

---

## 2. Classification Boundaries
**Goal**: Dependency files MUST NEVER appear in the configuration list.

### 2.1 Categorization Order & Guardrails
- Build three independent candidate lists (`deps`, `configs`, `docs`).
- **Canonical Decision**: `pyproject.toml`, `setup.py`, and `setup.cfg` are treated canonically as **dependency files**.
- **Exclusion**: `config_candidates = [p for p in config_candidates if not is_dependency_file(p)]`. These files MUST NOT be mixed or duplicated.

---

## 3. Ranking and Truncation
**Goal**: Deterministic ranking (Score DESC, then Path ASC) followed by truncation caps.

### 3.1 Scoring Heuristics
- **Docs (Cap 10)**:
    - `+300`: Root standards (`README*`, `CONTRIBUTING*`, `LICENSE*`, `SECURITY*`) at root.
    - `+250`: Directly under `docs/`.
    - `+200`: Explicit keywords in path (case-insensitive): `quickstart`, `install`, `setup`, `tutorial`.
    - `+150`: Nested under `docs/`.
    - `-100`: Under `tests/`, `examples/`, `scripts/`, `src/`.
- **Config (Cap 15)**:
    - `+300`: `Makefile` / `Justfile`.
    - `+200`: `tox/nox/pre-commit/pytest.ini`.
    - `+150`: GitHub Workflows.
    - **Note**: Config scoring does **not** include `pyproject.toml/setup.py/setup.cfg` as they are classified as dependencies.
- **Deps (No Cap, but Ranked)**:
    - `+300`: Root manifests (`pyproject.toml`, `requirements.txt`).
    - `+150`: Nested manifests.
    - `-100`: Under `tests/`, `examples/`, `scripts/`.

### 3.2 Determinism
- **Sort Key**: `lambda p: (-score_fn(p), p)` (Ensures stable sort by score desc, path asc).

---

## 4. Required Truncation Notes (V6 Compliance)
**Goal**: Exact phrasing for truncation messages. Emitted at the truncation site.

- **Exact Strings**:
    - `docs list truncated to 10 entries (total=<total>)`
    - `configurationFiles list truncated to 15 entries (total=<total>)`
- **Formatting**: No extra punctuation; use exact section keys; only render `## Analyzer notes` if non-empty.

---

## Verification Plan
1. **Unit Test**: `tests/fixtures/foo/requirements.txt` is invisible to all collectors.
2. **Category Test**: `pyproject.toml` appears in `dependencyFiles` but NOT `configurationFiles`.
3. **Ranking Test**: Root `README.md` ranks higher than `tests/fixtures/README.md`.
4. **Integration (Pollution Check)**: Analyze `mcp-repo-onboarding` and verify zero `tests/fixtures/**` appear in:
    - `dependencyFiles`
    - `configurationFiles`
    - `docs`
5. **Validator Regression**: Phase 6 Validator (`V1-V8`) still passes 100%.
