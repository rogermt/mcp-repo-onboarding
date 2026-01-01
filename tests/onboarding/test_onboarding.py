import shutil
import tempfile
from pathlib import Path

import pytest

from mcp_repo_onboarding.onboarding import write_onboarding


def test_write_overwrite_backup() -> None:
    """
    Asserts that overwriting creates a .bak file.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create initial file
        (temp_dir / "ONBOARDING.md").write_text("Old Content")

        # Overwrite it (Function will fail to import initially)
        result = write_onboarding(
            repo_root=str(temp_dir),
            content="New Content",
            mode="overwrite",
            create_backup=True,
        )

        # Check Main File
        assert (temp_dir / "ONBOARDING.md").read_text() == "New Content"

        # Check Backup
        assert result.backupPath is not None
        assert Path(result.backupPath).exists()
        assert Path(result.backupPath).read_text() == "Old Content"

    finally:
        shutil.rmtree(temp_dir)


def test_sandbox_security() -> None:
    """
    Asserts that writing outside repo root is forbidden.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Try to write to parent directory
        with pytest.raises(ValueError, match="escapes repo root"):
            write_onboarding(repo_root=str(temp_dir), content="Evil", path="../evil.md")
    finally:
        shutil.rmtree(temp_dir)


def test_backup_goes_to_archive_directory() -> None:
    """
    Asserts that backup is created in .onboarding_archive/ subdirectory.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create initial file
        (temp_dir / "ONBOARDING.md").write_text("Old Content")

        # Overwrite it
        result = write_onboarding(
            repo_root=str(temp_dir),
            content="New Content",
            path="ONBOARDING.md",
            mode="overwrite",
            create_backup=True,
        )

        # Check backup is in archive directory
        assert result.backupPath is not None
        backup_file = Path(result.backupPath)
        assert ".onboarding_archive" in backup_file.parts
        assert backup_file.name.startswith("ONBOARDING.md.bak.")
        assert backup_file.exists()
        assert backup_file.read_text() == "Old Content"

    finally:
        shutil.rmtree(temp_dir)


def test_nested_file_backup_preserves_structure() -> None:
    """
    Asserts that nested file backups preserve directory structure under archive.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create nested file
        docs_dir = temp_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "ONBOARDING.md").write_text("Old Nested Content")

        # Overwrite it
        result = write_onboarding(
            repo_root=str(temp_dir),
            content="New Nested Content",
            path="docs/ONBOARDING.md",
            mode="overwrite",
            create_backup=True,
        )

        # Check backup preserves nested structure
        assert result.backupPath is not None
        backup_file = Path(result.backupPath)
        assert ".onboarding_archive" in backup_file.parts
        assert "docs" in backup_file.parts
        assert backup_file.name.startswith("ONBOARDING.md.bak.")
        assert backup_file.exists()
        assert backup_file.read_text() == "Old Nested Content"

    finally:
        shutil.rmtree(temp_dir)


def test_archive_directory_created_automatically() -> None:
    """
    Asserts that .onboarding_archive/ is created if it doesn't exist.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create initial file
        (temp_dir / "ONBOARDING.md").write_text("Old Content")

        # Verify archive doesn't exist yet
        archive_dir = temp_dir / ".onboarding_archive"
        assert not archive_dir.exists()

        # Overwrite it
        result = write_onboarding(
            repo_root=str(temp_dir),
            content="New Content",
            path="ONBOARDING.md",
            mode="overwrite",
            create_backup=True,
        )

        # Check archive directory was created
        assert archive_dir.exists()
        assert archive_dir.is_dir()
        assert result.backupPath is not None
        assert Path(result.backupPath).exists()

    finally:
        shutil.rmtree(temp_dir)


def test_no_backups_in_repo_root() -> None:
    """
    Asserts that backup files do not clutter the repo root.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Create initial file
        (temp_dir / "ONBOARDING.md").write_text("Old Content")

        # Overwrite it
        result = write_onboarding(
            repo_root=str(temp_dir),
            content="New Content",
            path="ONBOARDING.md",
            mode="overwrite",
            create_backup=True,
        )

        # Check no .bak files in repo root
        bak_files = list(temp_dir.glob("*.bak.*"))
        assert len(bak_files) == 0, f"Found backup files in repo root: {bak_files}"

        # Backup should be in archive
        assert result.backupPath is not None
        backup_file = Path(result.backupPath)
        assert ".onboarding_archive" in str(backup_file)

    finally:
        shutil.rmtree(temp_dir)
