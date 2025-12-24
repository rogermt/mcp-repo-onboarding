import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

from mcp_repo_onboarding.analysis import analyze_repo


def test_permission_error_logs_warning(temp_repo: Callable[[str], Path], caplog: Any) -> None:
    """Verify that permission errors during analysis log a warning instead of just passing."""
    repo_path = temp_repo("logging-scenarios")
    secret_dir = repo_path / "secret"
    secret_dir.mkdir()

    # Trigger a permission error (mocking might be easier but let's try real fs)
    # Using a non-existent path to force an early error if chmod doesn't work well
    # in test environments, but we specifically want to test the try/except blocks.

    # We'll use a mocked approach or relying on the file system if chmod works.
    # Given previous tests failed on fixtures, we need to be robust.
    # Let's verify that a missing directory simply returns empty analysis (no crash),
    # but specific "unreadable" files should log.

    # Setup logging capture
    caplog.set_level(logging.WARNING, logger="mcp_repo_onboarding")
    # Force an OSError against a file we know is READ, not just scanned.
    # scan_repo_files doesn't read file content, but extract_makefile_commands does.
    # But wait, test_config_read_error_logs_warning tests Makefile specifically.
    # Let's try to target a file causing scan_repo_files to fail if possible,
    # OR just test that specific read errors log.

    # If we make the directory unreadable, os.scandir(root) should fail.
    # But we must do it on a subdirectory so the test setup itself doesn't fail before analysis.

    subdir = repo_path / "subdir"
    subdir.mkdir()
    (subdir / "foo.py").write_text("print(1)")

    try:
        os.chmod(subdir, 0o000)
        analyze_repo(str(repo_path))
        assert "Error scanning subdirectory" in caplog.text
    finally:
        os.chmod(subdir, 0o777)


def test_config_read_error_logs_warning(temp_repo: Callable[[str], Path], caplog: Any) -> None:
    """Verify that failing to read a makefile logs a warning."""
    repo_path = temp_repo("logging-scenarios")
    makefile = repo_path / "Makefile"
    makefile.write_text("test:")

    if hasattr(os, "chmod"):
        os.chmod(makefile, 0o000)
        try:
            caplog.set_level(logging.WARNING, logger="mcp_repo_onboarding")
            analyze_repo(str(repo_path))

            # Currently analysis.py just returns {} silently.
            # We want to verify it LOGS an error now.
            # This test will FAIL until we add the logging code.
            assert "Failed to read Makefile" in caplog.text or "Permission denied" in caplog.text
        finally:
            os.chmod(makefile, 0o777)
