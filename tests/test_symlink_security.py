import os
from pathlib import Path

import pytest

from mcp_repo_onboarding.analysis import analyze_repo


def test_symlink_traversal_outside_repo(tmp_path: Path) -> None:
    """Verify that symlinks pointing outside the repo are ignored by analyze_repo."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Create a secret file outside the repo
    secret_dir = tmp_path / "secrets"
    secret_dir.mkdir()
    secret_file = secret_dir / "passwords.txt"
    secret_file.write_text("root:x:0:0:root:/root:/bin/bash")

    # Create a symlink inside the repo pointing to the secret file
    traversal_link = repo_path / "README_TRAVERSAL.md"
    try:
        os.symlink(secret_file, traversal_link)
    except OSError:
        pytest.skip("Symlinks not supported on this platform")

    # Analyze the repo
    analysis = analyze_repo(str(repo_path))

    # The traversal link should NOT be in the results
    all_found_paths = [d.path for d in analysis.docs] + [
        c.path for c in analysis.configurationFiles
    ]

    assert "README_TRAVERSAL.md" not in all_found_paths


def test_symlink_directory_traversal(tmp_path: Path) -> None:
    """Verify that symlinks pointing to directories outside the repo are ignored."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Create an external directory with an interesting file
    ext_dir = tmp_path / "external_docs"
    ext_dir.mkdir()
    (ext_dir / "secret_doc.md").write_text("Secret content")

    # Create a symlink to this directory inside the repo
    # If we name it 'docs', it matches startswith('docs/') in _categorize_files
    docs_link = repo_path / "docs"
    try:
        os.symlink(ext_dir, docs_link)
    except OSError:
        pytest.skip("Symlinks not supported on this platform")

    # Analysis should not find files inside the linked directory
    analysis = analyze_repo(str(repo_path))

    all_found_paths = [d.path for d in analysis.docs] + [
        c.path for c in analysis.configurationFiles
    ]

    # If it descends into docs/, it might find docs/secret_doc.md
    assert not any("secret_doc.md" in p for p in all_found_paths)


def test_internal_symlink_allowed(tmp_path: Path) -> None:
    """Verify that symlinks pointing inside the repo are NOT ignored."""
    repo_path = tmp_path / "repo"
    repo_path.mkdir()

    # Create a real file
    real_doc = repo_path / "README.md"
    real_doc.write_text("Real content")

    # Create a symlink pointing to it
    internal_link = repo_path / "README_LINK.md"
    try:
        os.symlink(real_doc, internal_link)
    except OSError:
        pytest.skip("Symlinks not supported on this platform")

    # Analyze the repo
    analysis = analyze_repo(str(repo_path))

    all_found_paths = [d.path for d in analysis.docs] + [
        c.path for c in analysis.configurationFiles
    ]

    # Both the real file and the link should be found (if they match categories)
    assert "README.md" in all_found_paths
    assert "README_LINK.md" in all_found_paths
