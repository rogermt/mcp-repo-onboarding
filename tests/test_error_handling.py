import os

import pytest

from mcp_repo_onboarding.analysis import analyze_repo


def test_permission_denied_file(temp_repo):
    """Test that analysis gracefully handles files with no read permissions."""
    repo_path = temp_repo("error-scenarios")
    secret_file = repo_path / "secret.txt"
    secret_file.write_text("content")

    # Remove all permissions
    os.chmod(secret_file, 0o000)

    try:
        # Should not raise PermissionError
        _ = analyze_repo(str(repo_path))
        # File should be ignored or at least not cause crash
        # It won't be in all_files if scandir fails on it?
        # Actually scandir lists it, but reading it might fail.
        # analyze_repo doesn't read every file, but if it tries to identify it...
        pass
    finally:
        # Restore permissions so cleanup can delete it
        os.chmod(secret_file, 0o777)


def test_permission_denied_directory(temp_repo):
    """Test that analysis gracefully handles directories with no read/execute permissions."""
    repo_path = temp_repo("error-scenarios")
    secret_dir = repo_path / "secret_dir"
    secret_dir.mkdir()
    (secret_dir / "hidden.py").write_text("print('hidden')")

    # Remove read/execute permissions
    os.chmod(secret_dir, 0o000)

    try:
        # Should not raise PermissionError
        analysis = analyze_repo(str(repo_path))
        # Analysis should complete
        assert analysis is not None
    finally:
        os.chmod(secret_dir, 0o777)


def test_invalid_utf8_makefile(temp_repo):
    """Test processing a Makefile with invalid UTF-8 sequences."""
    repo_path = temp_repo("error-scenarios")
    makefile = repo_path / "Makefile"
    # Write invalid UTF-8 bytes
    makefile.write_bytes(b"build:\n\t\x80\xe0\xa0\x00echo 'bad encoding'")

    # Should not raise UnicodeDecodeError
    analysis = analyze_repo(str(repo_path))

    # We expect it to be processed partially or ignored, but definitely not crash
    assert analysis is not None
    # If extraction is robust, it might even find "build"
    # dependent on how replace/ignore errors works.


def test_invalid_utf8_shell_script(temp_repo):
    """Test processing a shell script with invalid UTF-8 sequences."""
    repo_path = temp_repo("error-scenarios")
    scripts_dir = repo_path / "scripts"
    scripts_dir.mkdir()
    script = scripts_dir / "bad.sh"

    content = b"#!/bin/bash\n# \x80\xff description\necho 'run'"
    script.write_bytes(content)

    analysis = analyze_repo(str(repo_path))
    assert analysis is not None
    # Verify we didn't crash


def test_symlink_loop(temp_repo):
    """Test that analysis doesn't get stuck in infinite recursion with symlink loops."""
    repo_path = temp_repo("error-scenarios")

    # create loop: dir_a/link_to_b -> dir_b, dir_b/link_to_a -> dir_a
    dir_a = repo_path / "dir_a"
    dir_b = repo_path / "dir_b"
    dir_a.mkdir()
    dir_b.mkdir()

    (dir_a / "file_a.py").write_text("a=1")
    (dir_b / "file_b.py").write_text("b=1")

    # Create circular symlinks
    try:
        os.symlink(dir_b, dir_a / "link_to_b")
        os.symlink(dir_a, dir_b / "link_to_a")
    except OSError:
        pytest.skip("Symlinks not supported or permission denied")

    # Set a timeout or rely on max_files to break loop?
    # analyze_repo has max_files=5000.
    # If it loops infinitely without adding files (if they are dupes?), it might hang.
    # Current implementation adds files to list.

    # We just want to ensure it terminates and returns
    analysis = analyze_repo(str(repo_path), max_files=100)
    assert analysis is not None
