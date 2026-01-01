# Issue #87 — Refactoring Plan: Blueprint Architecture (Registry + Engine + Canonical Module)

**Status:** PLANNING PHASE — Identification of problems and architecture changes ONLY (no implementation without explicit approval)

**Target Issue:** #87
**Type:** Major Architecture Refactoring
**Phase Context:** Phase 8 (Refinement, Maintainability)
**TDD Model:** Tests-first, with equivalence gates as the primary validation mechanism

---

## 1. Executive Summary

Issue #87 is a **major architecture refactoring** of the blueprint rendering system. The goal is to decompose the monolithic `onboarding_blueprint_v2.py` (current "v2") into a **registry-driven engine package** while maintaining **100% output equivalence** with the reference implementation.

### What We're Building
- **Current state:** Two versions coexist (`onboarding_blueprint.py` v1, `onboarding_blueprint_v2.py` monolithic v2)
- **Future state:**
  - `onboarding_blueprint_reference.py` — frozen copy of v2 (baseline for equivalence testing)
  - `onboarding_blueprint_engine/` — modular, registry-driven implementation
  - `onboarding_blueprint.py` — canonical versionless entrypoint (engine-backed)
  - `onboarding_blueprint_legacy.py` — v1 preserved (no deletion)
  - Optional shim: `onboarding_blueprint_v2.py` → imports canonical module

### Why This Matters
- **Maintainability:** Registry pattern replaces giant section-building code with composable rules
- **Testability:** Equivalence gates prove output byte-for-byte identical to reference
- **Extensibility:** Engine structure makes it easier to add new sections/builders
- **Safety:** Frozen reference prevents regression; equivalence tests are unambiguous

---

## 2. Architecture Overview: What We're Building

### Current State (Problems)
```
src/mcp_repo_onboarding/analysis/
├── onboarding_blueprint.py        # v1 monolith (legacy, still used)
└── onboarding_blueprint_v2.py     # v2 monolith (current, giant section builders)

tests/
├── test_onboarding_blueprint.py   # tests v1
└── test_onboarding_blueprint_v2.py # tests v2 (but doesn't actually test anything real)
```

**Problem:**
- Two monolithic implementations exist simultaneously
- v2 is large, hard to modify (section builders are inline, not composable)
- Tests don't enforce equivalence or prevent regression
- No clear canonical path for production code

### Target State (Solution)

```
src/mcp_repo_onboarding/analysis/
├── onboarding_blueprint.py                     # ← CANONICAL (versionless, engine-backed)
│   └── imports from onboarding_blueprint_engine
├── onboarding_blueprint_reference.py           # ← FROZEN reference (v2 for equivalence testing)
├── onboarding_blueprint_legacy.py              # ← v1 preserved (for backward compat tests)
├── onboarding_blueprint_v2.py [optional shim]  # ← Compat shim (backward-compat imports)
└── onboarding_blueprint_engine/                # ← NEW: Modular, registry-based
    ├── __init__.py                  # Exports public API
    ├── context.py                   # Context/builder state
    ├── specs.py                     # Section specs and builders
    ├── registry.py                  # Section registry + constants
    └── compile.py                   # Blueprint compilation + markdown rendering

tests/onboarding/
├── test_blueprint_engine_equivalence.py        # ← NEW: Equivalence gate (core of #87)
├── test_onboarding_blueprint_canonical_module.py # ← NEW: Tests canonical module
├── test_onboarding_blueprint.py                # refactored for v1
├── test_onboarding_blueprint_v2.py             # refactored for v2 reference
└── test_prompt_blueprint_v2_renderer.py        # [unchanged, integration tests]
```

### Key Design Decisions

1. **Two "v2" implementations coexist during refactor:**
   - `onboarding_blueprint_reference.py` — frozen current behavior (baseline)
   - `onboarding_blueprint_engine/` — new implementation with identical output
   - Equivalence gate tests prove they're byte-for-byte identical

2. **Registry pattern replaces monolithic builders:**
   - Section specs live in a registry (list of builders with order)
   - Each section builder is a pure function: `(context) → section_dict | None`
   - No giant `if/elif` chains; just iterate registry and call builders

3. **Canonical module is "versionless":**
   - Production code imports from `onboarding_blueprint` (no `_v2` suffix)
   - Path is clean, but output format is still `"onboarding_blueprint_v2"` (no change to API contract)

4. **v1 is not deleted:**
   - Stays as `onboarding_blueprint_legacy.py`
   - Kept for historical tests and potential A/B testing
   - Not promoted; new code should use canonical module

---

## 3. TDD Workflow: Tests-First Approach

### Phase A: Write Failing Tests (identify gaps and requirements)

**Step 1:** Create equivalence gate tests
File: `tests/onboarding/test_blueprint_engine_equivalence.py`
- Synthetic test data (no MCP tool calls, no analyzer dependencies)
- Create reference context → render with `onboarding_blueprint_reference`
- Create engine context → render with `onboarding_blueprint_engine.compile`
- Assert: `engine_output == reference_output` (byte-for-byte markdown + sections)
- These tests **FAIL** until engine code exists

**Step 2:** Create canonical module tests
File: `tests/onboarding/test_onboarding_blueprint_canonical_module.py`
- Imports from `onboarding_blueprint` (canonical, versionless)
- Asserts canonical module re-exports engine API
- Tests canonical module returns `onboarding_blueprint_v2` format string
- These tests **FAIL** until canonical module exists

**Step 3:** Create integration/existing test stubs
- Move v1 tests to use `onboarding_blueprint_legacy`
- Move v2 tests to use `onboarding_blueprint_reference` (frozen)
- Tests should **PASS** after module rename but **FAIL** after canonical module is live (import changes)

### Phase B: Implement (make tests pass)

**Step 4:** Create `onboarding_blueprint_reference.py`
- Copy current `onboarding_blueprint_v2.py` exactly (frozen snapshot)
- Rename imports to reference
- Equivalence tests now run; initially PASS (reference is baseline)

**Step 5:** Create `onboarding_blueprint_engine/` package
- `context.py` — build context from analyze + commands dicts
- `specs.py` — section builders (pure functions)
- `registry.py` — section registry, constants, and orchestration
- `compile.py` — compilation logic, markdown rendering
- `__init__.py` — public API exports

At this stage, equivalence tests should still **FAIL** (engine output ≠ reference).

**Step 6:** Implement engine sections iteratively
- Start with one section builder (e.g., Python Environment)
- Make it match reference output exactly (use equivalence test feedback)
- Add next section, repeat until all sections pass
- Equivalence tests gradually **TURN GREEN**

**Step 7:** Create canonical module
File: `src/mcp_repo_onboarding/analysis/onboarding_blueprint.py`
- Re-export engine API (versionless import path)
- Canonical module tests should **PASS**

**Step 8:** Update imports in production code
- Find all imports of `onboarding_blueprint_v2`
- Change to `onboarding_blueprint` (canonical)
- Run full test suite; all tests should **PASS**

**Step 9:** Optional cleanup
- Create backward-compat shim `onboarding_blueprint_v2.py` (if needed)
- Or remove `_v2` suffix from old reference and update imports (cleaner, but breaking)

---

## 4. Detailed Implementation Plan: Components to Build

### A. `onboarding_blueprint_reference.py`
**Purpose:** Frozen snapshot of current v2 behavior
**Action:** Copy `onboarding_blueprint_v2.py` exactly
**Exports:** `build_context`, `compile_blueprint_v2`

### B. `onboarding_blueprint_engine/context.py`
**Purpose:** Build and hold the analysis context for rendering
**Responsibilities:**
- Accept raw `analyze` dict and `commands` dict
- Build a `Context` object with structured, typed fields
- Apply any filtering/normalization specific to v2 behavior

**Key types/functions:**
```python
class Context:
    repo_path: str
    python_version_hints: list[str]
    env_setup_instructions: list[str]
    install_instructions: list[str]
    dependency_files: list[dict]  # with descriptions
    scripts: dict[str, list[dict]]  # dev, start, test, lint, format, install, other
    notes: list[str]
    notebooks: list[dict]
    frameworks: list[str]
    config_files: list[dict]
    docs: list[dict]
    test_commands: list[str]
    # ... other fields as needed

def build_context(analyze: dict, commands: dict) -> Context:
    """Construct Context from analyzer output."""
```

### C. `onboarding_blueprint_engine/specs.py`
**Purpose:** Define section builders (pure functions)
**Responsibilities:**
- Each section builder is a function: `(context: Context) → section_dict | None`
- Section dict is `{"heading": str, "lines": list[str]}`
- Return `None` if section is empty/not applicable

**Key builders (examples):**
```python
def build_python_environment_section(ctx: Context) -> dict | None:
    """Build Python environment setup section."""
    # Handles version pins, env instructions, install commands, etc.
    # Returns None if no Python content

def build_scripts_section(ctx: Context) -> dict | None:
    """Build scripts/commands section."""
    # Builds dev, test, start commands
    # Returns None if no scripts

# ... more builders
```

### D. `onboarding_blueprint_engine/registry.py`
**Purpose:** Central registry of section specs and shared constants
**Responsibilities:**
- Define ordered list of section specs (controls output order)
- Define constants (BULLET, NO_COMMANDS, NO_DEPS, etc.)
- Provide registry access function

**Key exports:**
```python
BULLET = "* "  # or "`* `" depending on context
NO_COMMANDS = {"dev": [], "test": [], "build": []}
# ... other constants

def get_section_registry() -> list[SectionSpec]:
    """Return ordered list of section specs."""
    return [
        SectionSpec(name="python-environment", builder=build_python_environment_section),
        SectionSpec(name="scripts", builder=build_scripts_section),
        # ... more specs in order
    ]
```

### E. `onboarding_blueprint_engine/compile.py`
**Purpose:** Orchestrate compilation and markdown rendering
**Responsibilities:**
- Iterate through registry, call builders, collect sections
- Render sections to markdown
- Return blueprint dict in expected format

**Key functions:**
```python
def compile_blueprint_v2(ctx: Context) -> dict[str, Any]:
    """Compile analysis context into a blueprint."""
    # Call builders from registry
    # Return {"format": "onboarding_blueprint_v2", "sections": [...], "render": {...}}

def render_blueprint_to_markdown(blueprint: dict) -> str:
    """Render blueprint sections to markdown."""
```

### F. `onboarding_blueprint_engine/__init__.py`
**Purpose:** Public API export point
**Exports:**
```python
from .compile import compile_blueprint_v2, render_blueprint_to_markdown
from .context import Context, build_context
from .registry import BULLET, NO_COMMANDS, NO_CONFIG, NO_DEPS, NO_DOCS  # Constants

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
    # constants...
]
```

### G. `onboarding_blueprint.py` (Canonical Module)
**Purpose:** Stable, versionless import path
**Content:**
```python
"""Canonical blueprint module (engine-backed)."""
# Re-export engine API for versionless imports
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine import (
    Context,
    build_context,
    compile_blueprint_v2,
    render_blueprint_to_markdown,
)
from mcp_repo_onboarding.analysis.onboarding_blueprint_engine.registry import (
    BULLET,
    NO_COMMANDS,
    NO_CONFIG,
    NO_DEPS,
    NO_DOCS,
)

__all__ = [
    "Context",
    "build_context",
    "compile_blueprint_v2",
    "render_blueprint_to_markdown",
    "BULLET",
    "NO_COMMANDS",
    "NO_CONFIG",
    "NO_DEPS",
    "NO_DOCS",
]
```

### H. Test Files

#### `tests/onboarding/test_blueprint_engine_equivalence.py`
**Core TDD gate:** Reference == Engine
**Pattern:**
```python
def _mk(analyze_overrides=None, commands_overrides=None) -> (dict, dict):
    """Build minimal valid analyze + commands dicts."""
    # Returns synthetic test data

def _assert_equivalent(analyze, commands):
    """Assert engine and reference produce identical output."""
    ref = compile_ref(build_ctx_ref(analyze, commands))
    eng = compile_eng(build_ctx_eng(analyze, commands))
    assert eng["render"]["markdown"] == ref["render"]["markdown"]
    assert eng["sections"] == ref["sections"]

def test_equivalence_minimal_repo():
    analyze, commands = _mk()
    _assert_equivalent(analyze, commands)

def test_equivalence_no_pin_includes_generic_venv_lines():
    # Specific test for venv behavior
    ...

# ... more tests from blueprint.md
```

#### `tests/onboarding/test_onboarding_blueprint_canonical_module.py`
**Tests canonical module re-exports:**
```python
from mcp_repo_onboarding.analysis import onboarding_blueprint

def test_canonical_re_exports_engine_api():
    """Assert canonical module has expected exports."""
    assert hasattr(onboarding_blueprint, "Context")
    assert hasattr(onboarding_blueprint, "build_context")
    assert hasattr(onboarding_blueprint, "compile_blueprint_v2")

def test_canonical_produces_v2_format():
    """Assert output format is 'onboarding_blueprint_v2'."""
    analyze, commands = _mk()
    result = onboarding_blueprint.compile_blueprint_v2(
        onboarding_blueprint.build_context(analyze, commands)
    )
    assert result["format"] == "onboarding_blueprint_v2"
```

#### Updates to existing tests
- `tests/onboarding/test_onboarding_blueprint.py` → imports `onboarding_blueprint_legacy`
- `tests/onboarding/test_onboarding_blueprint_v2.py` → imports `onboarding_blueprint_reference`
- Both should continue to pass

---

## 5. Identified Problems & Issues to Report

*This section documents concerns identified during planning. **Do NOT attempt fixes without explicit user approval.***

### P1: Monolithic Blueprint Structure
**Problem:** Current `onboarding_blueprint_v2.py` has section-building logic spread across large functions. Hard to maintain and extend.
**Impact:** New sections require modifying giant monolith; high risk of regression.
**Solution:** Registry-driven pattern (part of #87 implementation).

### P2: Lack of Equivalence Testing
**Problem:** No tests ensure engine output matches reference. Easy to introduce subtle differences.
**Impact:** Risk of silent regressions in output format, markdown rendering.
**Solution:** Equivalence gate test suite (part of #87 implementation).

### P3: Version Numbers in Filenames
**Problem:** Current naming (`onboarding_blueprint.py` v1, `onboarding_blueprint_v2.py` v2) is confusing. Production code must explicitly version.
**Impact:** Import paths are verbose; hard to deprecate versions cleanly.
**Solution:** Versionless canonical path (part of #87 implementation).

### P4: Incomplete Test Coverage
**Problem:** `tests/onboarding/test_onboarding_blueprint_v2.py` doesn't test actual behavior; it appears to copy implementation.
**Impact:** Tests don't catch regressions or validate equivalence.
**Solution:** Rewrite as equivalence gate tests (part of #87 implementation).

### P5: Missing Section Builder Abstraction
**Problem:** Section building is inline, no composable interface.
**Impact:** Hard to understand which sections are produced, in what order.
**Solution:** Explicit SectionSpec + registry (part of #87 implementation).

### P6: Potential Context Building Bugs
**Problem:** Context building from raw `analyze`/`commands` dicts may have implicit assumptions or bugs.
**Impact:** Engine implementation might discover bugs in reference when comparing outputs.
**Solution:** TDD workflow will catch these; fix in reference first, then engine (part of #87 implementation).

### P7: Constants Scattered
**Problem:** Constants like `BULLET`, `NO_COMMANDS`, `NO_DEPS` may be defined in multiple places or inline.
**Impact:** Inconsistency; hard to maintain shared constants.
**Solution:** Centralize in registry module (part of #87 implementation).

### P8: Import Path Explosion After Refactor
**Problem:** After refactor, old code must change imports from `onboarding_blueprint_v2` → `onboarding_blueprint`.
**Impact:** Large changelist; risk of missed imports.
**Solution:** Comprehensive grep + optional backward-compat shim (part of #87 implementation).

### P9: Large Refactor Risk
**Problem:** This is a major architecture change affecting core functionality.
**Impact:** High risk of subtle output changes that break validator or user expectations.
**Solution:** Equivalence gates must be byte-perfect; full test suite must pass (part of #87 implementation).

### P10: Test File Organization
**Problem:** Tests are now split between `tests/` root and `tests/onboarding/`. Need clarity on where blueprint tests live.
**Impact:** Confusion about test structure.
**Solution:** Clarify and document test organization (related to #72, test reorganization).

---

## 6. Success Criteria & Validation

### Phase A: Tests Written (RED)
- [ ] `tests/onboarding/test_blueprint_engine_equivalence.py` created and failing (imports don't exist yet)
- [ ] `tests/onboarding/test_onboarding_blueprint_canonical_module.py` created and failing
- [ ] All existing blueprint tests still pass (imports unchanged for reference)

### Phase B: Implementation Complete (GREEN)
- [ ] `onboarding_blueprint_reference.py` created and frozen
- [ ] `onboarding_blueprint_engine/` package fully implemented with all modules
- [ ] Equivalence gate tests **PASSING** (engine == reference byte-for-byte)
- [ ] Canonical module created and re-exporting engine
- [ ] All production imports updated to use canonical module
- [ ] All tests (existing + new) **PASSING**

### Phase C: Validation & Safety
- [ ] Full test suite passes: `uv run pytest`
- [ ] Linting passes: `uv run ruff check . && uv run ruff format --check .`
- [ ] Type checking passes: `uv run mypy src/mcp_repo_onboarding --ignore-missing-imports`
- [ ] Validation passes: `python scripts/validate_onboarding.py` (all V1-V8 rules)
- [ ] No regression in MCP tool output or format
- [ ] No new dependencies introduced

### Phase D: Refactor Cleanup (Optional)
- [ ] Legacy v1 module renamed to `onboarding_blueprint_legacy.py` (or stays as-is)
- [ ] Optional: Create `onboarding_blueprint_v2.py` compat shim
- [ ] Documentation updated to reflect new structure

---

## 7. Execution Sequence (High-Level)

1. **Create feature branch** from clean master
   `git checkout -b feat/issue-87-blueprint-refactor`

2. **Phase A: Write Tests First (TDD)**
   - Write equivalence gate tests (FAILING)
   - Write canonical module tests (FAILING)
   - Confirm old tests still pass with reference imports

3. **Phase B: Implement Engine**
   - Create `onboarding_blueprint_reference.py` (frozen copy)
   - Create `onboarding_blueprint_engine/` package modules
   - Implement section builders iteratively, using equivalence tests to validate

4. **Phase C: Integrate**
   - Create canonical module re-exporting engine
   - Update all production imports to use canonical module
   - Run full test suite; confirm green

5. **Phase D: Cleanup & Documentation**
   - Finalize test organization
   - Update docs/comments to explain new structure
   - Prepare PR description

6. **Review & Merge**
   - Submit PR with equivalence gates and implementation
   - Address review feedback
   - Merge to master

---

## 8. Risk Assessment & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Engine output ≠ reference (subtle differences) | Silent regressions | MEDIUM | Byte-perfect equivalence tests; iterative implementation |
| Missing section builders | Incomplete output | MEDIUM | Registry ensures all sections accounted for |
| Import changes break production code | Runtime errors | HIGH | Comprehensive grep; optional compat shim |
| Context building bugs discovered | Output differences | LOW | TDD workflow catches early; fix reference first |
| Large refactor introduces new bugs | Various failures | MEDIUM | Full test + validator suite gate merge |
| Test organization confusion | Maintenance burden | LOW | Clear documentation + consistent naming |

---

## 9. Questions for User Clarification (Before Implementation)

1. **Test organization:** Where should blueprint tests live after refactor? `tests/` root or `tests/onboarding/` subdirectory?
2. **Legacy v1 handling:** Should `onboarding_blueprint.py` (v1) be renamed to `onboarding_blueprint_legacy.py`, or kept as-is for backward compat?
3. **Compat shim:** Create `onboarding_blueprint_v2.py` → canonical module for soft migration, or require import changes immediately?
4. **Timeline:** Should this be done all at once, or phased (e.g., reference + equivalence tests first, engine second)?
5. **Review scope:** Who should review equivalence gates and architecture?

---

## 10. File Checklist (What Gets Created/Modified)

### New Files
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_reference.py` (frozen v2 copy)
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_engine/__init__.py`
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_engine/context.py`
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_engine/specs.py`
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_engine/registry.py`
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_engine/compile.py`
- [ ] `tests/onboarding/test_blueprint_engine_equivalence.py`
- [ ] `tests/onboarding/test_onboarding_blueprint_canonical_module.py`

### Modified Files
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint.py` (becomes canonical re-export)
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint_v2.py` (optional compat shim or delete)
- [ ] `tests/onboarding/test_onboarding_blueprint.py` (update imports for legacy)
- [ ] `tests/onboarding/test_onboarding_blueprint_v2.py` (update imports for reference)
- [ ] Any production code importing `onboarding_blueprint_v2` (change to canonical)
- [ ] Various other imports throughout codebase

### Renamed Files
- [ ] `src/mcp_repo_onboarding/analysis/onboarding_blueprint.py` → v1 (optional)
  OR stay as-is if backward compat not needed

---

## Next Steps

1. User reviews this plan
2. User approves or requests clarifications/changes
3. User grants permission to proceed with Phase A (test writing)
4. Agent creates feature branch and writes failing tests
5. Agent reports test status and waits for approval before implementing
6. Proceed iteratively: implement, report, get approval, continue
