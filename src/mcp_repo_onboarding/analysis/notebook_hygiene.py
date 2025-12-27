from __future__ import annotations

from pathlib import Path

# Keep this list tightly scoped to acceptance criteria.
_NOTEBOOK_HYGIENE_MARKERS = (
    "nbstripout",
    "nb-clean",
    "jupyter-notebook-cleanup",
)

# Safety cap: pre-commit config should be small; avoid reading huge files.
_MAX_BYTES = 256_000  # 256 KB


def precommit_has_notebook_hygiene(repo_root: Path, rel_path: str) -> bool:
    """
    Detect notebook hygiene tooling in a pre-commit config.

    Static, deterministic:
    - read file content (size capped)
    - case-insensitive substring search for known markers

    Returns True if any marker is found; otherwise False.
    """
    p = (repo_root / rel_path).resolve()
    try:
        # Must remain under root
        p.relative_to(repo_root.resolve())
    except Exception:
        return False

    try:
        if not p.is_file():
            return False
        if p.stat().st_size > _MAX_BYTES:
            return False
        text = p.read_text(encoding="utf-8", errors="ignore").lower()
    except OSError:
        return False

    return any(marker in text for marker in _NOTEBOOK_HYGIENE_MARKERS)
