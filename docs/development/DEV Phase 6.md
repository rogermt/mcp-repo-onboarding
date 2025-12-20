# DEV Phase 6 — Python MCP Hardening & Signal Precision

## Context

Phase 6 begins after the successful migration from TypeScript to Python for the MCP server and the validation of the Phase‑5 pivot via A/B evaluation. The Python MCP is now the **canonical implementation for Python repositories**.

Phase 6 focuses on **hardening**, **correctness**, and **signal precision**, not expansion of scope.

---

## Phase 6 Objectives

1. **Correctness & Contract Alignment**

   * Eliminate contradictory analyzer output
   * Strictly adhere to the Phase‑5 B‑prompt contract
   * Ensure MCP output is copy/paste‑safe and diff‑stable

2. **Signal Prioritization**

   * Prefer repo‑native abstractions (e.g. `make install`) over generic commands
   * Reduce generic suggestions in MCP‑backed output

3. **Extractor Precision (Not Expansion)**

   * Replace heuristics with Python‑native static parsers
   * Improve accuracy without increasing runtime or token usage

4. **Lock the Python MCP Contract**

   * Clearly define what Python MCP guarantees
   * Stabilize before expanding TS/JS parity work

---

## Non‑Goals (Phase 6)

* No execution of project code
* No dependency resolution or installs
* No deep architecture or data‑flow analysis
* No inference of org or policy rules
* No TS/JS parity work yet

---

## Epic

### Phase 6 – Python MCP Hardening & Signal Precision

**Summary**
Phase 6 focuses on tightening correctness, grounding, and signal prioritization in the Python MCP implementation following successful Phase‑5 validation. The goal is to eliminate contradictory output, reduce generic suggestions, and leverage Python‑native tooling for more precise static extraction—without increasing scope, runtime, or token usage.

**Goals**

* Zero contradictory analyzer output
* Strict adherence to Phase‑5 B‑prompt contract
* Prefer repo‑native commands over generic ones
* Improve Python version and dependency signal accuracy
* Keep MCP output mechanical and non‑prose

**Non‑Goals**

* No code execution
* No dependency resolution
* No deep architecture inference
* No TS/JS parity work

---

## Phase 6 Issue Breakdown

### 🐛 Bugs (Corrections First)

#### Bug: Contradictory “No explicit commands detected” message

* **Problem**: Analyzer may list a command and also state that none were detected
* **Fix**: If commands exist, list them only; otherwise emit the fallback message

---

#### Bug: MCP output does not match B‑prompt Overview format

* **Problem**: Uses `Repository:` instead of required `Repo path:`
* **Fix**: Enforce exact Overview header and line format

---

#### Bug: Generic virtualenv instructions emitted without grounding

* **Problem**: MCP emits `python -m venv .venv` without evidence
* **Fix**: Remove generic environment setup prose from MCP output

---

### ✨ Features (Precision Improvements)

#### Feature: Prefer `make install` over raw pip installs

* **Motivation**: Reflect repo author intent and reduce user error
* **Behavior**:

  * If `Makefile` defines an `install` target, surface `make install`
  * Fall back to pip only if no higher‑level abstraction exists

---

#### Feature: Parse `pyproject.toml` with `tomllib`

* **Motivation**: Improve accuracy of Python version and package manager detection
* **Behavior**:

  * Parse `requires-python`
  * Detect Poetry / Hatch / PEP‑621 metadata
  * Avoid regex‑based parsing

---

#### Feature: Classify version pins vs ranges using `packaging`

* **Motivation**: Enforce Phase‑5 rule distinguishing pins from compatibility
* **Behavior**:

  * Exact versions → reported as pins
  * Ranges → treated as compatibility, not pins

---

#### Feature: Neutral detection of secondary tooling (e.g. Node.js)

* **Motivation**: Avoid false impression of “pure Python” repos
* **Behavior**:

  * Detect `.nvmrc` or equivalent
  * Emit neutral signal only (no commands)

---

#### Feature: Improve ignore handling using `pathspec`

* **Motivation**: Reduce noise and prevent vendor pollution
* **Behavior**:

  * Honor `.gitignore` / `.dockerignore`
  * Apply ignores before file categorization

---

## Approved Python Tooling (Phase 6)

| Tool        | Purpose                | Scope                |
| ----------- | ---------------------- | -------------------- |
| `tomllib`   | pyproject.toml parsing | stdlib, static       |
| `packaging` | Version semantics      | static, no inference |
| `ast`       | CLI / entrypoint hints | parse‑only           |
| `pathspec`  | Ignore handling        | read‑only            |
| `PyYAML`    | CI/workflow parsing    | value‑only           |

**Explicitly excluded**: pip, poetry install, linters, language servers, runtime imports.

---

## Execution Order

1. Bug fixes (blocking correctness)
2. Signal prioritization (`make install`, secondary tooling)
3. Parser upgrades (`tomllib`, `packaging`, `pathspec`)
4. Contract lock for Python MCP

---

## Phase 6 Exit Criteria

* MCP output is strictly grounded, mechanical, and contradiction‑free
* Python version and dependency signals are parser‑accurate
* No generic prose emitted from MCP tools
* Python MCP contract is stable and documented
* Ready to plan TS/JS Phase 7 without revisiting Python foundations



