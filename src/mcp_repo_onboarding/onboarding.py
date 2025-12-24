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
        ValueError: If mode is 'create' and file already exists.
    """
    target = resolve_path_inside_repo(repo_root, path)
    backup_path = None

    if target.exists():
        if mode == "create":
            raise ValueError(f"File {path} already exists")

        if mode == "overwrite" and create_backup:
            timestamp = int(time.time())
            # Create backup file: ONBOARDING.md.bak.1234567890
            backup_file = target.with_name(f"{target.name}.bak.{timestamp}")
            shutil.copy2(target, backup_file)
            backup_path = str(backup_file)

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
