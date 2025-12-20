# Onboarding Role Aware Usage
**from the perspective of how real teams behave**, not how tools are marketed.

Sections:

1. **How senior devs would actually use this**
2. **How junior devs would actually use this**
3. **What’s already sufficient**
4. **What’s missing to make it *stick*** (without violating scope)
5. **What you should *not* add**

---

## 1. How **senior devs** would use this

Senior devs don’t want onboarding prose. They want **certainty** and **auditability**.

### Primary senior use cases

#### A. Fast repo triage

Typical questions a senior asks in the first 60 seconds:

* How do I run tests?
* What’s the canonical entry point?
* What tooling is enforced?
* Is this Makefile-driven or ad-hoc?
* Is CI telling me the truth?

**How they’d use your tool**

```bash
gemini repo-onboarding analyze_repo
gemini repo-onboarding get_run_and_test_commands
```

They scan:

* Commands
* Version pins
* CI presence
* Truncation notes

They don’t read docs yet.

✔️ Your Phase-5 output already supports this well.

---

#### B. “Is this repo lying?”

Seniors are allergic to outdated docs.

They’ll compare:

* MCP output vs README
* MCP output vs CI

If MCP disagrees, they trust MCP more.

✔️ This works because:

* No execution
* No prose
* No interpretation

---

#### C. PR review & maintenance hygiene

Seniors maintaining repos will use this to:

* Spot drift (`README` vs reality)
* Decide whether to update ONBOARDING.md
* Ensure new contributors don’t cargo-cult commands

This is where `write_onboarding` matters.

---

### What seniors still need (small additions)

1. **Source confidence tags**

   * `(from CI)`
   * `(from Makefile)`
   * `(from file presence)`

This helps them instantly judge trust without reading evidence.

2. **Explicit “not detected” sections**

   * “No test commands detected”
   * “No Python version pin detected”

Silence ≠ absence for seniors.

---

## 2. How **junior devs** would use this

Junior devs want **guardrails**, not completeness.

### Primary junior use cases

#### A. “What do I run without breaking things?”

Juniors are afraid of:

* Running the wrong command
* Installing deps incorrectly
* Messing up their environment

They don’t want options — they want *one safe path*.

**How they’d use your tool**

* Gemini turns MCP output into:

  * “Do these 3 steps”
  * No alternatives
  * No speculation

✔️ This is *exactly* why MCP → Gemini separation matters.

---

#### B. “Where should I look next?”

When something fails, juniors need:

* A file to open
* A directory to inspect

Your capped:

* docs
* config files

…already do this well.

---

### What juniors still need (but MCP should NOT provide directly)

Important distinction:

**Juniors need help, but MCP should not give it directly.**

Instead, MCP needs to provide **better hooks for Gemini**.

#### Needed MCP improvements (still in scope)

1. **Primary vs secondary commands**

   * “Primary dev command”
   * “CI-only commands (not recommended locally)”

2. **Entry point hint**

   * “Application entry point detected”
   * No explanation, just path(s)

This prevents juniors from spelunking blindly.

---

## 3. What is already sufficient (don’t overbuild)

You already have enough for:

* Correct environment detection
* Safe command discovery
* Noise suppression
* Token efficiency
* Auditability

You **do not** need:

* Dependency graphs
* Call graphs
* Explanations of frameworks
* Step-by-step tutorials in MCP

That belongs to Gemini or docs.

---

## 4. What’s missing to make it *sticky* (key insight)

This is the most important part.

### The missing piece: **roles**

Right now, the tool is *technically excellent* — but it’s **role-agnostic**.

You don’t need new features.
You need **role framing**.

#### Minimal addition (Phase 6-safe)

Add a top-level concept (not behavior):

```text
Intended usage:
- Maintainers: audit commands and update ONBOARDING.md
- Contributors: generate safe onboarding via Gemini
```

This helps teams adopt it correctly.

---

### Another missing piece: **failure clarity**

When MCP can’t detect something, that must be explicit.

Example:

* “No install command detected”
* “No test tooling detected”

This is crucial for juniors, and comforting for seniors.

---

## 5. What you should **not** add (even if requested)

This will protect the project long-term.

❌ Don’t add:

* “Recommended” tools
* Opinionated linting guidance
* “Best practices”
* Automatic fixes
* Dependency installation
* Runtime checks

These break trust and expand scope.

