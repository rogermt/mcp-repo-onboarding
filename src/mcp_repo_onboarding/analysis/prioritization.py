from __future__ import annotations

from pathlib import Path, PurePosixPath

__all__ = ["get_config_priority", "get_doc_priority", "get_dep_priority"]

# Preserve exact existing scoring behavior.

_CONFIG_EXACT: dict[str, int] = {
    "makefile": 300,
    "justfile": 300,
    "tox.ini": 200,
    "noxfile.py": 200,
    ".pre-commit-config.yaml": 200,
    ".pre-commit-config.yml": 200,
    "pytest.ini": 200,
}
_CONFIG_ROOT_BONUS = 100


def get_config_priority(path: str) -> int:
    p = _norm(path)
    name = Path(p).name.lower()

    score = 10
    if p.startswith(".github/workflows/"):
        score = 150

    score = max(score, _CONFIG_EXACT.get(name, 0))

    if "/" not in p:
        score += _CONFIG_ROOT_BONUS

    return score


_DOC_ROOT_PREFIXES = ("readme", "contributing", "license", "security")
_DOC_KEYWORDS = ("quickstart", "install", "setup", "tutorial")
_DOC_PENALTY_DIRS = ("tests/", "test/", "examples/", "scripts/", "src/")


def get_doc_priority(path: str) -> int:
    p = _norm(path)
    name = Path(p).name.lower()

    score = 50

    if "/" not in p and name.startswith(_DOC_ROOT_PREFIXES):
        score = 300

    if score < 300:
        if p.startswith("docs/") and "/" not in p[5:]:
            score = 250
        elif any(kw in p.lower() for kw in _DOC_KEYWORDS):
            score = 200
        elif p.startswith("docs/"):
            score = 150

    if "admin" in p.lower():
        score -= 20

    if any(seg in p.lower() for seg in _DOC_PENALTY_DIRS):
        score -= 200

    return score


_DEP_PENALTY_DIRS = ("tests/", "test/", "examples/", "scripts/")


def get_dep_priority(path: str) -> int:
    p = _norm(path)
    name = Path(p).name.lower()

    score = 100

    is_manifest = name == "pyproject.toml" or name.startswith("requirements")

    if "/" not in p:
        if is_manifest:
            score = 300
    else:
        if is_manifest:
            score = 150

    if any(seg in p.lower() for seg in _DEP_PENALTY_DIRS):
        score -= 200

    return score


def _norm(path: str) -> str:
    return str(PurePosixPath(str(path).replace("\\", "/").lstrip("/")))
