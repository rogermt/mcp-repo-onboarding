from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def flatten_files(analysis):
    """Helper to get a set of all file paths found in analysis."""
    files = set()
    for doc in analysis.docs:
        files.add(doc.path)
    for config in analysis.configurationFiles:
        files.add(config.path)
    if analysis.python:
        for dep in analysis.python.dependencyFiles:
            files.add(dep.path)
    return files


# Existing tests...


def test_integration_targeted_signals_not_blocked():
    """
    Test that targeted signal files are detected even if ignored by .gitignore,
    while other gitignored files are still ignored.
    This test is expected to FAIL initially because the current scan_repo_files
    prevents all ignored files from reaching classification.
    """
    repo_root = FIXTURES_DIR / "repo_signal_file_gitignored"

    # Ensure fixture exists for this test
    if not repo_root.exists():
        repo_root.mkdir(parents=True, exist_ok=True)

    (repo_root / ".gitignore").write_text("pyproject.toml\n*.log\n")
    (repo_root / "pyproject.toml").write_text('[project]\nname = "test"')
    (repo_root / "error.log").write_text("an error occurred")
    (repo_root / "README.md").write_text("My project")

    analysis = analyze_repo(str(repo_root))

    found_files = flatten_files(analysis)

    # pyproject.toml should be detected (targeted signal)
    assert "pyproject.toml" in found_files
    # error.log should be ignored (normal gitignore)
    assert "error.log" not in found_files
    # README.md should be detected
    assert "README.md" in found_files

    # Cleanup the temporary fixture
    import shutil

    shutil.rmtree(repo_root)
