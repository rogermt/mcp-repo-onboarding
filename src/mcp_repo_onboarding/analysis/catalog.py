"""
Canonical definitions for file categorization.

This module breaks a circular dependency between core and other modules
by providing a neutral location for classification functions.
"""

from pathlib import Path

from ..config import DEPENDENCY_FILE_TYPES


def is_dependency_file(path: str) -> bool:
    """Check if a file is canonically a dependency manifest."""
    path = path.replace("\\", "/").lstrip("/")
    name = Path(path).name.lower()
    return name in DEPENDENCY_FILE_TYPES or (
        name.startswith("requirements") and name.endswith((".txt", ".in"))
    )
