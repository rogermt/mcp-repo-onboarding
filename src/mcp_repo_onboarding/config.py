"""
Configuration constants for the repository analysis module.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

# Maximum number of documentation files to include in the analysis report
MAX_DOCS_CAP: Final[int] = 10

# Maximum number of configuration files to include in the analysis report
MAX_CONFIG_CAP: Final[int] = 15

# Default maximum number of files to scan if not specified
DEFAULT_MAX_FILES: Final[int] = 5000

# Patterns to always ignore for safety and noise reduction
SAFETY_IGNORES: Final[list[str]] = [
    "tests/fixtures/",
    "test/fixtures/",
    ".git/",
    ".hg/",
    ".svn/",
    ".venv/",
    "venv/",
    "env/",
    "__pycache__/",
    "node_modules/",
    "site-packages/",
    "dist/",
    "build/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".coverage",
]

# =============================================================================
# File classification (Single Source of Truth)
#
# Goal for #78:
# - Replace duplicated/manual overlapping sets with a single authoritative mapping.
# - Derive CONFIG_FILE_TYPES and DEPENDENCY_FILE_TYPES from that mapping.
# - Keep behavior unchanged.
#
# Contract: dependency files must never appear in configurationFiles output.
# =============================================================================

FileCategory = Literal["config", "dependency"]


@dataclass(frozen=True)
class FileKind:
    category: FileCategory


# Authoritative mapping for exact filename classification (lowercase keys).
# NOTE: Keep this aligned with existing behavior (no surprise additions).
FILE_KINDS: Final[dict[str, FileKind]] = {
    # -------------------------
    # Config files
    # -------------------------
    "makefile": FileKind(category="config"),
    "tox.ini": FileKind(category="config"),
    "noxfile.py": FileKind(category="config"),
    ".pre-commit-config.yaml": FileKind(category="config"),
    ".pre-commit-config.yml": FileKind(category="config"),
    "pytest.ini": FileKind(category="config"),
    "pytest.cfg": FileKind(category="config"),
    # NOTE: pyproject.toml/setup.py/setup.cfg intentionally NOT config (deps only)
    # -------------------------
    # Dependency files
    # -------------------------
    "requirements.txt": FileKind(category="dependency"),
    "requirements-dev.txt": FileKind(category="dependency"),
    "requirements-server.txt": FileKind(category="dependency"),
    "pyproject.toml": FileKind(category="dependency"),
    "setup.py": FileKind(category="dependency"),
    "setup.cfg": FileKind(category="dependency"),
    "pipfile": FileKind(category="dependency"),
    "environment.yml": FileKind(category="dependency"),
    "environment.yaml": FileKind(category="dependency"),
}

# Derived disjoint sets used throughout the codebase (exact filenames only).
CONFIG_FILE_TYPES: Final[frozenset[str]] = frozenset(
    name for name, kind in FILE_KINDS.items() if kind.category == "config"
)
DEPENDENCY_FILE_TYPES: Final[frozenset[str]] = frozenset(
    name for name, kind in FILE_KINDS.items() if kind.category == "dependency"
)

_overlap = CONFIG_FILE_TYPES & DEPENDENCY_FILE_TYPES
if _overlap:
    raise RuntimeError(f"config.py invariant violated: overlapping file types: {_overlap}")

# Prefix-based dependency detection (preserve existing behavior in catalog.py):
# - requirements*.txt / requirements*.in
DEPENDENCY_PREFIXES: Final[tuple[str, ...]] = ("requirements",)
DEPENDENCY_SUFFIXES: Final[tuple[str, ...]] = (".txt", ".in")


def classify_filename(name: str) -> FileCategory | None:
    """
    Classify a repo file *name* (not a path), case-insensitive.

    Returns:
        "config" | "dependency" | None

    Behavior is designed to match existing logic:
    - Exact-name matches via FILE_KINDS
    - requirements*.txt / requirements*.in treated as dependency manifests
    """
    n = name.lower()

    kind = FILE_KINDS.get(n)
    if kind is not None:
        return kind.category

    if any(n.startswith(pfx) for pfx in DEPENDENCY_PREFIXES) and any(
        n.endswith(sfx) for sfx in DEPENDENCY_SUFFIXES
    ):
        return "dependency"

    return None


# Extensions to exclude from documentation entirely
DOC_EXCLUDED_EXTENSIONS: Final[set[str]] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".mp4",
    ".mov",
    ".mp3",
    ".css",
    ".js",
    ".map",
}

# Extensions considered "human documentation" under docs/ directory
DOC_HUMAN_EXTENSIONS: Final[set[str]] = {
    ".md",
    ".rst",
    ".txt",
    ".adoc",
}

# Mapping of tool keys and build backend identifiers to package manager names
KNOWN_PACKAGE_MANAGERS: Final[dict[str, str]] = {
    "poetry": "poetry",
    "hatch": "hatch",
    "pdm": "pdm",
    "flit": "flit",
}
