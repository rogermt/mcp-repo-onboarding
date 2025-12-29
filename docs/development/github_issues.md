---

## Issue #77 — Refactor prioritization.py to registry-driven scoring (no behavior change)

**Title:** Refactor prioritization.py to registry-driven scoring (no behavior change)

**Labels:** `enhancement`, `refactoring`

**Description:**

Replace the current `if/elif` prioritization logic with a registry (dict-based lookups + small ordered rule lists), similar to the pattern used in `describers.py`, while preserving **exact scoring semantics** and ordering behavior.

### Motivation
- Current `if/elif` chains are hard to maintain and slow to extend.
- Registry pattern makes prioritization rules explicit, composable, and easy to test.
- Phase 7 guarantees (root +300 dominance, safety ignores, deterministic output) must remain intact.

### Proposed approach
- Introduce registries:
  - `EXACT_NAME_SCORES: dict[str, int]`
  - `EXTENSION_SCORES: dict[str, int]`
  - `DIR_PREFIX_RULES: list[tuple[str, int]]` (ordered, with “first match wins” if that’s the current behavior)
- Keep root bonus logic unchanged.
- Ensure tie-breaking remains deterministic.

### Acceptance criteria
- `analyze_repo` returns **identical JSON** on existing eval fixtures compared to baseline (Phase 7 behavior).
- Root-level files still outrank nested files consistently (root +300 invariant preserved).
- All unit tests pass; evaluation suite stays 5/5.
- No changes to safety ignore behavior (especially `tests/fixtures/`).

---

## Issue #78 — Config cleanup — single source of truth for config/dependency file classification

**Title:** Config cleanup — single source of truth for config/dependency file classification

**Labels:** `enhancement`, `refactoring`

**Description:**

Clean up `config.py` to eliminate overlapping/duplicated sets like `CONFIG_FILE_TYPES` vs `DEPENDENCY_FILE_TYPES` by creating a single authoritative mapping (file → flags/kind) and deriving sets from it.

### Motivation
- Overlapping sets cause confusion and require defensive logic in `core.py`.
- Centralizing classification prevents drift and makes future polyglot support easier.

### Proposed approach
- Introduce something like `FILE_KINDS: dict[str, FileKind]` (flags: `is_config`, `is_dependency`, etc.).
- Derive:
  - `CONFIG_FILE_TYPES = {name for name, kind in FILE_KINDS.items() if kind.is_config}`
  - `DEPENDENCY_FILE_TYPES = {name for name, kind in FILE_KINDS.items() if kind.is_dependency}`
- Update any downstream guards that exist only to reconcile overlap.

### Acceptance criteria
- No behavioral change in repo analysis output (same ranking/categorization as Phase 7).
- `core.py` no longer needs “overlap guard” logic (or it becomes trivial).
- All tests + evaluation suite pass.

---

## Issue #79 — Determinism hardening — stable tie-break sorting + regression test for identical output

**Title:** Determinism hardening — stable tie-break sorting + regression test for identical output

**Labels:** `enhancement`, `hardening`

**Description:**

Guarantee fully deterministic ordering when multiple files have equal score by enforcing a stable secondary sort key (e.g., `rel_path`), and add a regression test that runs analysis twice and asserts identical output.

### Motivation
- Determinism is a core constraint: same repo state must produce same JSON every time.
- Tie cases can cause “random-looking” ordering if sorting relies on non-stable iteration order.

### Proposed approach
- Ensure ranking sort key is something like: `(-score, rel_path)` (or whatever path field is canonical in your structs).
- Add a test that:
  - runs `analyze_repo` twice on the same fixture
  - asserts deep equality of the returned dict/JSON
- Add a targeted test for the tie-breaker: two items with equal score must sort by path consistently.

### Acceptance criteria
- Analysis output ordering is stable across runs and platforms.
- New determinism tests pass.
- No change to safety ignores; no subprocess/network calls introduced.

---

## Issue #80 — Phase 8 scaffold — EffectiveConfig layering for future user overrides (no user-facing behavior yet)

**Title:** Phase 8 scaffold — EffectiveConfig layering for future user overrides (no user-facing behavior yet)

**Labels:** `enhancement`, `scaffolding`

**Description:**

Add an internal configuration layering mechanism (`defaults ⊕ overrides`) so Phase 8+ can support `.onboardingrc` / `pyproject.toml` overrides without refactoring core logic again. This issue does **not** implement parsing user config yet—just the internal scaffolding.

### Motivation
- Sets up the architecture for user configuration cleanly.
- Keeps current behavior unchanged while creating a safe seam for future expansion.

### Proposed approach
- Create an `EffectiveConfig` dataclass with fields like:
  - additional include paths / pinned folders
  - additional ignore patterns (but never allowing override of `tests/fixtures/` ignore)
  - prioritization adjustments (optional)
- Wire analysis pipeline to accept an `EffectiveConfig`, but default to “no overrides”.

### Acceptance criteria
- With no user config present, analysis output is **unchanged**.
- Safety constraint enforced: `tests/fixtures/` ignore cannot be disabled through any override mechanism.
- Tests updated/added to confirm no-change baseline.

---

## Issue #81 — Polyglot foundations — add “Other tooling detected” signal plumbing (ties into #12)

**Title:** Polyglot foundations — add “Other tooling detected” signal plumbing (ties into #12)

**Labels:** `enhancement`, `plumbing`

**Description:**

Introduce a generic “Other tooling detected” signal bucket in the analysis output so the LLM can surface neutral secondary tooling presence (Node, etc.) without suggesting commands. This is the plumbing/framework; the Node.js detection itself is already tracked in **#12**.

### Motivation
- Supports mixed Python + JS/TS repos (your long-term goal).
- Prevents misleading “pure Python” onboarding docs when Node tooling exists.
- Keeps behavior neutral and static-only.

### Proposed approach
- Add an analysis field like: `other_tooling_detected: list[str]` (or a structured list with evidence files).
- Ensure it’s populated only by explicit evidence files (e.g., `.nvmrc`, `package.json`, `pnpm-lock.yaml`, `yarn.lock`, etc.) and never infers commands.
- Update MCP prompt/template expectations if needed (without breaking validator rules).

### Acceptance criteria
- Output includes a neutral list of detected tooling when evidence exists.
- No commands or setup instructions are generated by the tool itself (it only reports evidence).
- No subprocess/network calls; static scan only.
- Related issue #12 can implement the first detector using this plumbing.
