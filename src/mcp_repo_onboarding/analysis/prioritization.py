from __future__ import annotations

from pathlib import PurePosixPath

__all__ = ["get_config_priority", "get_doc_priority", "get_dep_priority"]

# NOTE: Inputs are expected to be normalized repo-relative POSIX paths (contract rule).

# ----------------------------
# Config prioritization
# ----------------------------

_CONFIG_BASE_SCORE = 10
_CONFIG_ROOT_BONUS = 100

_CONFIG_EXACT_SCORES: dict[str, int] = {
    "makefile": 300,
    "justfile": 300,
    "tox.ini": 200,
    "noxfile.py": 200,
    ".pre-commit-config.yaml": 200,
    ".pre-commit-config.yml": 200,
    "pytest.ini": 200,
}

_CONFIG_WORKFLOWS_PREFIX = ".github/workflows/"


def get_config_priority(path: str) -> int:
    """
    Registry-driven implementation of configuration scoring.

    Preserves legacy semantics:
    - default score 10
    - exact-name rules win over workflows prefix
    - workflows prefix applies only when no exact-name match
    - root bonus +100 if path has no '/'
    """
    p = str(PurePosixPath(path))
    name = PurePosixPath(p).name.lower()

    score = _CONFIG_BASE_SCORE

    exact = _CONFIG_EXACT_SCORES.get(name)
    if exact is not None:
        score = exact
    elif p.startswith(_CONFIG_WORKFLOWS_PREFIX):
        score = 150

    if "/" not in p:
        score += _CONFIG_ROOT_BONUS

    return score


# ----------------------------
# Docs prioritization
# ----------------------------

_DOC_BASE_SCORE = 50
_DOC_ROOT_PREFIXES = ("readme", "contributing", "license", "security")
_DOC_KEYWORDS = ("quickstart", "install", "setup", "tutorial")
_DOC_DEPRIORITIZED_SEGMENTS = ("tests/", "test/", "examples/", "scripts/", "src/")


def get_doc_priority(path: str) -> int:
    """
    Registry-driven implementation of docs scoring.

    Preserves legacy semantics:
    - base 50
    - root standards only if path has no '/' and name startswith root prefixes -> 300
    - if not root-standard:
      - docs/<file> direct child -> 250
      - keywords anywhere -> 200
      - docs/ nested -> 150
    - penalties:
      - contains 'admin' -> -20
      - if under tests/test/examples/scripts/src -> -200
    """
    p = str(PurePosixPath(path))
    p_lower = p.lower()
    name = PurePosixPath(p).name.lower()

    score = _DOC_BASE_SCORE

    # Root standards
    if "/" not in p and name.startswith(_DOC_ROOT_PREFIXES):
        score = 300

    # Other buckets (only if not root-standard)
    if score < 300:
        if p.startswith("docs/") and "/" not in p[5:]:
            score = 250
        elif any(kw in p_lower for kw in _DOC_KEYWORDS):
            score = 200
        elif p.startswith("docs/"):
            score = 150

    # Penalties
    if "admin" in p_lower:
        score -= 20

    if any(seg in p_lower for seg in _DOC_DEPRIORITIZED_SEGMENTS):
        score -= 200

    return score


# ----------------------------
# Dependency prioritization
# ----------------------------

_DEP_BASE_SCORE = 100
_DEP_DEPRIORITIZED_SEGMENTS = ("tests/", "test/", "examples/", "scripts/")


def get_dep_priority(path: str) -> int:
    """
    Registry-driven implementation of dependency file scoring.

    Preserves legacy semantics:
    - base 100
    - manifest definition: name == pyproject.toml OR name startswith requirements
    - if manifest and root -> 300
    - if manifest and nested -> 150
    - penalties: under tests/test/examples/scripts -> -200
    """
    p = str(PurePosixPath(path))
    p_lower = p.lower()
    name = PurePosixPath(p).name.lower()

    score = _DEP_BASE_SCORE

    is_manifest = name == "pyproject.toml" or name.startswith("requirements")
    is_root = "/" not in p

    if is_manifest:
        score = 300 if is_root else 150

    if any(seg in p_lower for seg in _DEP_DEPRIORITIZED_SEGMENTS):
        score -= 200

    return score
