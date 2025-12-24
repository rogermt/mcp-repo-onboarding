from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo

# This test file will be used to test the end-to-end integration
# of the description metadata. It is expected to fail until the implementation is complete.

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_description_metadata_in_repo_analysis():
    """
    Asserts that high-signal files and commands have their 'description' field populated.
    This test will FAIL until the describers and registry are integrated.
    """
    repo_root = FIXTURES_DIR / "searxng"
    # Ensure fixture exists or use a dummy if necessary, but searxng is a known fixture
    if not repo_root.exists():
        repo_root = Path("/home/rogermt/searxng")

    if not repo_root.exists():
        return  # Skip if environment doesn't have the repo

    analysis = analyze_repo(str(repo_root))

    # 1. Configuration File Description
    makefile = next((c for c in analysis.configurationFiles if c.path == "Makefile"), None)
    assert makefile is not None, "Makefile not found in configurationFiles"
    assert makefile.description == "Primary task runner for development and build orchestration."

    # 2. Command Description
    test_cmd = next((s for s in analysis.scripts.test if s.command == "make test"), None)
    assert test_cmd is not None, "'make test' not found in scripts.test"
    assert test_cmd.description == "Run the test suite via Makefile target."

    # 3. Dependency File Description
    reqs_file = next(
        (d for d in analysis.python.dependencyFiles if d.path == "requirements.txt"),
        None,
    )
    assert reqs_file is not None, "requirements.txt not found in dependencyFiles"
    assert reqs_file.description == "Python dependency manifest."
