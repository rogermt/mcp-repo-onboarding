import logging
import os
from pathlib import Path

from .structs import IgnoreMatcher

logger = logging.getLogger(__name__)


def scan_repo_files(
    root: Path,
    ignore: IgnoreMatcher,
    max_files: int = 5000,
) -> tuple[list[str], list[str]]:
    """
    Scan the repository for files, respecting ignore rules.

    Args:
        root: The root directory to scan.
        ignore: The IgnoreMatcher instance.
        max_files: Maximum number of files to return.

    Returns:
        A tuple containing a list of all file paths and a list of Python file paths.
    """
    all_files: list[str] = []
    py_files: list[str] = []

    try:
        with os.scandir(root) as entries:
            sorted_entries = sorted(entries, key=lambda e: e.name)
            dirs_to_visit = []
            for entry in sorted_entries:
                entry_path = Path(entry.path)
                is_dir = entry.is_dir()

                if ignore.should_ignore(entry_path, is_dir=is_dir):
                    continue

                if is_dir:
                    dirs_to_visit.append(entry.path)
                elif entry.is_file():
                    rel_path = entry.name
                    all_files.append(rel_path)
                    if rel_path.endswith(".py"):
                        py_files.append(rel_path)
    except OSError as e:
        logger.warning(f"Error scanning directory {root}: {e}")
        return [], []

    queue = dirs_to_visit
    while queue and len(all_files) < max_files:
        current_dir = queue.pop(0)
        try:
            with os.scandir(current_dir) as entries:
                sorted_entries = sorted(entries, key=lambda e: e.name)
                for entry in sorted_entries:
                    if len(all_files) >= max_files:
                        break

                    entry_path = Path(entry.path)
                    is_dir = entry.is_dir()

                    if ignore.should_ignore(entry_path, is_dir=is_dir):
                        continue

                    if is_dir:
                        queue.append(entry.path)
                    elif entry.is_file():
                        try:
                            rel_path = str(entry_path.relative_to(root))
                            all_files.append(rel_path)
                            if rel_path.endswith(".py"):
                                py_files.append(rel_path)
                        except ValueError as e:
                            logger.debug(f"Skipping invalid path {entry_path}: {e}")
                            continue
        except OSError as e:
            logger.warning(f"Error scanning subdirectory {current_dir}: {e}")
            continue

    return all_files, py_files
