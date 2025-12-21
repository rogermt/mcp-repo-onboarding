## IgnoreMatcher — Internal API (Phase 6)

### Design Intent

* Single responsibility: **answer “should this path be ignored?”**
* Stateless after construction
* Fast enough to be called on every path during traversal
* No filesystem mutation, no git execution

---

## Public Interface (Internal Module)

```python
class IgnoreMatcher:
    def __init__(
        self,
        repo_root: Path,
        safety_ignores: list[str],
        gitignore_paths: list[Path],
    ) -> None:
        ...
```

### Constructor Responsibilities

* Normalize `repo_root` (realpath, resolved)
* Load and compile ignore rules once
* Prepare for cheap repeated matching

---

## Core Methods

### `should_ignore(path: Path) -> bool`

**Primary API — used everywhere**

**Contract**

* `path` may be file or directory
* `path` must be inside `repo_root`
* Returns `True` if path is ignored by:

  1. Safety ignores **OR**
  2. Repo ignore rules (`pathspec`)

**Guarantees**

* Deterministic
* No I/O
* No exceptions (fail closed → ignore = False)

```python
def should_ignore(self, path: Path) -> bool:
    ...
```

---

### `should_descend(dir_path: Path) -> bool`

**Optimization hook for directory traversal**

**Contract**

* Called only for directories
* If returns `False`, walker must not recurse

```python
def should_descend(self, dir_path: Path) -> bool:
    ...
```

**Invariant**

```text
should_descend(p) == not should_ignore(p)
```

This exists purely for readability and future optimization.

---

## Safety Ignore Semantics

### Input

`safety_ignores: list[str]`

Example:

```python
[
    ".git/",
    ".venv/",
    "__pycache__/",
    "node_modules/",
    "site-packages/",
    "dist/",
    "build/",
]
```

### Rules

* Evaluated **before** pathspec
* Always relative to repo root
* Directory match excludes entire subtree
* Cannot be overridden by `.gitignore`

---

## Repo Ignore Semantics (`pathspec`)

### Loading Rules

* Patterns loaded from:

  * `<repo_root>/.gitignore`
  * `<repo_root>/.git/info/exclude` (optional)
* Missing files are silently ignored
* Invalid patterns are skipped, not fatal

### Matching

* Use `GitWildMatchPattern`
* Paths normalized to **POSIX-style, relative paths**
* Directory paths must include trailing `/` when tested

---

## Internal State (Suggested)

```python
self.repo_root: Path
self._safety_matchers: list[Callable[[str], bool]]
self._pathspec: PathSpec | None
```

Notes:

* Safety ignores can be compiled to prefix checks
* `pathspec` may be `None` if no ignore files found

---

## Expected Call Site Usage

### During Walk

```python
for root, dirs, files in os.walk(repo_root):
    root_path = Path(root)

    if ignore_matcher.should_ignore(root_path):
        dirs.clear()
        continue

    dirs[:] = [
        d for d in dirs
        if ignore_matcher.should_descend(root_path / d)
    ]

    for f in files:
        path = root_path / f
        if ignore_matcher.should_ignore(path):
            continue
        process(path)
```

This guarantees:

* Ignored dirs are never descended
* Ignored files never reach classification

---

## Failure Handling (Hard Rule)

* **Never raise** during ignore checks
* If ignore rules fail to load → behave as:

  * Safety ignores only
* Never log unless debug mode is explicitly enabled

---

## Why This API Is Correct

* Small surface area
* Impossible to misuse accidentally
* Forces ignore logic to happen **before everything else**
* Clean seam for future language ports (TS version later)

---

## Explicit Non-Features (By Design)

* No glob guessing
* No git index awareness
* No negation resolution beyond pathspec
* No per-category ignores

---


# Ignore Handling — Pseudo-Code (Phase 6)

## Inputs

* `repo_root: Path`
* `max_files: int`
* `SAFETY_IGNORES: list[str]`

---

## Step 1 — Initialize IgnoreMatcher

```python
def build_ignore_matcher(repo_root: Path) -> IgnoreMatcher:
    gitignore_paths = []

    gitignore = repo_root / ".gitignore"
    if gitignore.is_file():
        gitignore_paths.append(gitignore)

    info_exclude = repo_root / ".git" / "info" / "exclude"
    if info_exclude.is_file():
        gitignore_paths.append(info_exclude)

    return IgnoreMatcher(
        repo_root=repo_root,
        safety_ignores=SAFETY_IGNORES,
        gitignore_paths=gitignore_paths,
    )
```

---

## Step 2 — Directory Walk with Early Pruning

```python
def walk_repo(repo_root: Path, ignore: IgnoreMatcher):
    for root, dirs, files in os.walk(repo_root):
        root_path = Path(root)

        if ignore.should_ignore(root_path):
            dirs.clear()
            continue

        # mutate dirs in-place to prevent descent
        dirs[:] = [
            d for d in dirs
            if ignore.should_descend(root_path / d)
        ]

        for name in files:
            path = root_path / name

            if ignore.should_ignore(path):
                continue

            yield path
```

**Invariant:**
Ignored paths never reach classification.

---

## Step 3 — Classification Pipeline

```python
def analyze_repo(repo_root: Path, max_files: int) -> RepoAnalysis:
    ignore = build_ignore_matcher(repo_root)

    deps = []
    configs = []
    docs = []
    notes = []

    for path in walk_repo(repo_root, ignore):
        if len(deps) + len(configs) + len(docs) >= max_files:
            notes.append(f"file list truncated to {max_files} entries")
            break

        rel = path.relative_to(repo_root)

        if is_dependency_file(rel):
            deps.append(rel)
            continue

        if is_config_file(rel):
            configs.append(rel)
            continue

        if is_doc_file(rel):
            docs.append(rel)
            continue
```

---

## Step 4 — Post-Ignore Truncation (Per Section)

```python
deps, deps_note = cap_list(deps, 15, "dependency files")
configs, configs_note = cap_list(configs, 15, "configuration files")
docs, docs_note = cap_list(docs, 10, "docs")

notes.extend(n for n in [deps_note, configs_note, docs_note] if n)
```

**Critical rule:**
Caps and counts are applied **after ignore filtering**.

---

## Step 5 — RepoAnalysis Assembly

```python
return RepoAnalysis(
    repoPath=str(repo_root),
    python=PythonSignals(
        dependencyFiles=[FileRef(p) for p in deps],
        ...
    ),
    configurationFiles=[FileRef(p) for p in configs],
    docs=[FileRef(p) for p in docs],
    notes=notes or None,
)
```

---

## Error Handling (Global Rule)

```text
Ignore failures → degrade silently
Classification failures → skip file
Traversal failures → skip subtree
```

No errors leak into user-facing output.

---

## Guarantees (Restated in Code Terms)

* `walk_repo()` yields only non-ignored paths
* Ignore logic runs **before**:

  * classification
  * caps
  * truncation notes
* Safety ignores cannot be overridden
* `.gitignore` semantics match git behavior (via pathspec)
* Performance improves by directory pruning

---

## Minimal Test Hooks

You only need to assert:

* `walk_repo()` never yields ignored paths
* Truncation counts exclude ignored files
* Missing `.gitignore` behaves identically to today

---

# Ignore Handling — Test Fixture Design (Phase 6)

## Goals of the Fixtures

* Prove ignores are applied **before classification**
* Prove safety ignores cannot be overridden
* Prove truncation counts are post-ignore
* Stay fast (no giant repos, no mocks)

---

## Directory Layout

```
tests/
└── fixtures/
    └── ignore_handling/
        ├── repo_no_gitignore/
        ├── repo_basic_gitignore/
        ├── repo_safety_override/
        ├── repo_nested_ignores/
        ├── repo_large_noise/
```

Each fixture is a **real filesystem tree**, not mocked paths.

---

## Fixture 1 — No `.gitignore` (Baseline)

### Path

```
repo_no_gitignore/
├── requirements.txt
├── docs/
│   └── index.md
├── build/
│   └── generated.txt
├── .venv/
│   └── lib.py
```

### Expectations

* `requirements.txt` → included
* `docs/index.md` → included
* `build/generated.txt` → ❌ excluded (safety ignore)
* `.venv/lib.py` → ❌ excluded (safety ignore)

### Assertion

```python
assert paths == {
    "requirements.txt",
    "docs/index.md",
}
```

---

## Fixture 2 — Basic `.gitignore`

### `.gitignore`

```
build/
.env
```

### Path

```
repo_basic_gitignore/
├── .gitignore
├── requirements.txt
├── build/
│   └── out.txt
├── .env
├── docs/
│   └── guide.md
```

### Expectations

* `build/out.txt` → ❌ excluded (gitignore)
* `.env` → ❌ excluded (gitignore)
* `docs/guide.md` → included
* `requirements.txt` → included

---

## Fixture 3 — Safety Ignore Cannot Be Overridden

### `.gitignore`

```
!.venv/
```

### Path

```
repo_safety_override/
├── .gitignore
├── .venv/
│   └── fake.py
├── pyproject.toml
```

### Expectations

* `.venv/fake.py` → ❌ excluded (safety wins)
* `pyproject.toml` → included

### Assertion

```python
assert ".venv/fake.py" not in results
```

---

## Fixture 4 — Nested Ignore Rules

### `.gitignore`

```
docs/_build/
```

### Path

```
repo_nested_ignores/
├── .gitignore
├── docs/
│   ├── index.md
│   └── _build/
│       └── html/
│           └── index.html
```

### Expectations

* `docs/index.md` → included
* `docs/_build/html/index.html` → ❌ excluded
* Directory pruning prevents deep traversal

---

## Fixture 5 — Large Noise + Truncation

### `.gitignore`

```
dist/
```

### Path

```
repo_large_noise/
├── .gitignore
├── dist/
│   └── many_files_*.txt (50 files)
├── docs/
│   └── doc_*.md (20 files)
```

### Analyzer Config

```python
DOCS_CAP = 10
```

### Expectations

* Only **10 docs** listed
* Truncation note:

  ```
  docs list truncated to 10 entries (total=20)
  ```
* `dist/` files do not affect counts

---

## Test API Shape (Example)

```python
def run_fixture(name: str) -> RepoAnalysis:
    repo = FIXTURES / name
    return analyze_repo(repo, max_files=1000)
```

---

## Core Assertions (Reusable)

```python
def assert_not_present(analysis, *paths):
    for p in paths:
        assert p not in flatten_paths(analysis)

def assert_only_present(analysis, expected):
    assert set(flatten_paths(analysis)) == set(expected)
```

---

## What You Do *Not* Test (On Purpose)

* git CLI behavior
* global gitignore
* symlinks
* pathological glob patterns

Those are explicitly out of scope.

---

## Exit Criteria for Issue #9

This issue is **done** when:

* All fixtures pass
* Ignore logic is impossible to bypass accidentally
* Truncation math is post-ignore
* No performance regression observed


