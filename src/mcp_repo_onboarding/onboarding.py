import logging
import shutil
import time
from pathlib import Path

from .schema import OnboardingDocument, WriteOnboardingResult

"""
Onboarding module for reading and writing the ONBOARDING.md file.

This module provides safe file operations restricted to the repository root.
"""

logger = logging.getLogger(__name__)

ARCHIVE_DIRNAME = ".onboarding_archive"


def _backup_path(repo_root: str, rel_path: str, ts: int) -> Path:
    """
    Compute backup path in archive directory.

    Preserves subdirectory structure to avoid collisions.

    Args:
        repo_root: The root directory of the repository.
        rel_path: Relative path to the file being backed up.
        ts: Timestamp for backup suffix.

    Returns:
        Path object for the backup file (absolute path).
    """
    root = Path(repo_root).resolve()
    archive_root = root / ARCHIVE_DIRNAME
    return archive_root / f"{rel_path}.bak.{ts}"


def _create_backup(repo_root: str, rel_path: str) -> str:
    """
    Create a backup of the file in the archive directory.

    Args:
        repo_root: The root directory of the repository.
        rel_path: Relative path to the file being backed up.

    Returns:
        Repo-relative POSIX path to the backup file.

    Raises:
        FileNotFoundError: If source file does not exist.
    """
    root = Path(repo_root).resolve()
    src = (root / rel_path).resolve()

    if not src.exists():
        raise FileNotFoundError(f"Source file does not exist: {src}")

    ts = int(time.time())
    dst = _backup_path(repo_root, rel_path, ts)

    # Create archive parent directories
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Copy file with metadata
    shutil.copy2(src, dst)

    # Return repo-relative POSIX path
    return dst.relative_to(root).as_posix()


def resolve_path_inside_repo(repo_root: str, sub_path: str) -> Path:
    """
    Resolve path and ensure it does not escape repo root.

    Strict security check to prevent ../ traversal.

    Args:
        repo_root: The root directory of the repository.
        sub_path: The relative path to resolve.

    Returns:
        The resolved absolute path.

    Raises:
        ValueError: If the path escapes the repository root.
    """
    root = Path(repo_root).resolve()
    # Join and resolve
    target = (root / sub_path).resolve()

    # Python 3.9+ method to check containment
    try:
        target.relative_to(root)
    except ValueError as e:
        logger.warning(f"Path resolution error: {e}")
        raise ValueError(f"Path {sub_path} escapes repo root {repo_root}")

    return target


def read_onboarding(repo_root: str, path: str = "ONBOARDING.md") -> OnboardingDocument:
    """
    Read the content of the onboarding document.

    Args:
        repo_root: The root directory of the repository.
        path: Relative path to the onboarding file.

    Returns:
        OnboardingDocument object containing file status and content.
    """
    try:
        target = resolve_path_inside_repo(repo_root, path)
        if not target.exists():
            return OnboardingDocument(exists=False, path=str(target))

        content = target.read_text(encoding="utf-8")
        return OnboardingDocument(
            exists=True,
            path=str(target),
            content=content,
            sizeBytes=len(content.encode("utf-8")),
        )
    except Exception as e:
        # Fallback for permission errors etc
        logger.error(f"Failed to read onboarding file {path}: {e}")
        return OnboardingDocument(exists=False, path=path)


def write_onboarding(
    repo_root: str,
    content: str,
    path: str = "ONBOARDING.md",
    mode: str = "overwrite",
    create_backup: bool = True,
) -> WriteOnboardingResult:
    """
    Write content to the onboarding document.

    Args:
        repo_root: The root directory of the repository.
        content: The text content to write.
        path: Relative path to the onboarding file.
        mode: Write mode ('overwrite', 'append', or 'create').
        create_backup: Whether to create a backup if overwriting.

    Returns:
        WriteOnboardingResult containing write details.

    Raises:
        ValueError: If mode is invalid or if mode is 'create' and file already exists.
    """
    if mode not in ("overwrite", "append", "create"):
        raise ValueError(f"Invalid mode: {mode}. Must be 'overwrite', 'append', or 'create'")

    target = resolve_path_inside_repo(repo_root, path)
    backup_path = None

    if target.exists():
        if mode == "create":
            raise ValueError(f"File {path} already exists")

        if mode == "overwrite" and create_backup:
            # Create backup in archive directory
            rel_backup_path = _create_backup(repo_root, path)
            backup_path = str(Path(repo_root).resolve() / rel_backup_path)

    # Create parent directories if they don't exist
    target.parent.mkdir(parents=True, exist_ok=True)

    final_content = content
    if mode == "append" and target.exists():
        original = target.read_text(encoding="utf-8")
        # Ensure newline separation
        sep = "\n\n" if not original.endswith("\n") else "\n"
        final_content = original + sep + content

    target.write_text(final_content, encoding="utf-8")

    return WriteOnboardingResult(
        path=str(target),
        bytesWritten=len(final_content.encode("utf-8")),
        backupPath=backup_path,
    )
