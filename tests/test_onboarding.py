import pytest
import shutil
import tempfile
from pathlib import Path
from mcp_repo_onboarding.onboarding import write_onboarding

def test_write_overwrite_backup():
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
            create_backup=True
        )
        
        # Check Main File
        assert (temp_dir / "ONBOARDING.md").read_text() == "New Content"
        
        # Check Backup
        assert result.backupPath is not None
        assert Path(result.backupPath).exists()
        assert Path(result.backupPath).read_text() == "Old Content"
        
    finally:
        shutil.rmtree(temp_dir)

def test_sandbox_security():
    """
    Asserts that writing outside repo root is forbidden.
    """
    temp_dir = Path(tempfile.mkdtemp())
    try:
        # Try to write to parent directory
        with pytest.raises(ValueError, match="escapes repo root"):
            write_onboarding(
                repo_root=str(temp_dir),
                content="Evil",
                path="../evil.md"
            )
    finally:
        shutil.rmtree(temp_dir)
