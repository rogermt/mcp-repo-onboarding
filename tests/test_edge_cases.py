from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_empty_repo(temp_repo: Callable[[str], Path]) -> None:
    """Test analysis on a completely empty repository."""
    repo_path = temp_repo("edge-cases")
    empty_dir = repo_path / "empty_project"
    empty_dir.mkdir()

    analysis = analyze_repo(str(empty_dir))

    assert analysis is not None
    assert len(analysis.docs) == 0
    assert len(analysis.configurationFiles) == 0
    assert analysis.python is None


def test_repo_only_binary_files(temp_repo: Callable[[str], Path]) -> None:
    """Test analysis on a repository containing only binary files (images)."""
    repo_path = temp_repo("edge-cases")
    bin_dir = repo_path / "binary_project"
    bin_dir.mkdir()

    # Create some dummy binary files
    (bin_dir / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (bin_dir / "data.bin").write_bytes(b"\x00\x01\x02\x03")

    analysis = analyze_repo(str(bin_dir))

    assert analysis is not None
    assert len(analysis.docs) == 0
    # Binary files should not be mistaken for text configs
