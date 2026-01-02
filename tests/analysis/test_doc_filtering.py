from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_documentation_filtering_excludes_binaries(temp_repo: Callable[[str], Path]) -> None:
    """Verify that binary files and non-human docs are excluded from documentation list."""
    repo_path = temp_repo("docs-with-binaries")

    analysis = analyze_repo(str(repo_path))

    doc_paths = [d.path for d in analysis.docs]

    # Should include human docs
    assert "README.md" in doc_paths
    assert "docs/index.rst" in doc_paths
    assert "docs/getting_started.md" in doc_paths
    assert "docs/admin_guide.md" in doc_paths

    # Should EXCLUDE binaries/assets
    assert "docs/_static/images/a.png" not in doc_paths
    assert "docs/_static/images/b.jpg" not in doc_paths
    assert "docs/_static/css/custom.css" not in doc_paths
    assert "subproject/README.pdf" not in doc_paths


def test_documentation_prioritization(temp_repo: Callable[[str], Path]) -> None:
    """Verify that documentation is prioritized correctly."""
    repo_path = temp_repo("docs-with-binaries")

    analysis = analyze_repo(str(repo_path))

    doc_paths = [d.path for d in analysis.docs]

    # README should be first (priority 100)
    assert doc_paths[0] == "README.md"

    # getting_started should be before admin_guide
    # README (100)
    # getting_started (90)
    # docs/index.rst (50)
    # admin_guide (40)

    # Find indices
    readme_idx = doc_paths.index("README.md")
    gs_idx = doc_paths.index("docs/getting_started.md")
    index_idx = doc_paths.index("docs/index.rst")
    admin_idx = doc_paths.index("docs/admin_guide.md")

    assert readme_idx < gs_idx
    assert gs_idx < index_idx
    assert index_idx < admin_idx


def test_doc_truncation_excludes_binaries_from_total(temp_repo: Callable[[str], Path]) -> None:
    """Verify that the truncation note count only reflects filtered docs."""
    repo_path = temp_repo("docs-with-binaries")

    # Add many human docs to trigger truncation
    docs_dir = repo_path / "docs"
    for i in range(20):
        (docs_dir / f"extra_doc_{i}.md").write_text("content")

    # max_docs_cap is 10 in config.py
    analysis = analyze_repo(str(repo_path))

    # Total should be 20 (extra) + 4 (original human docs) = 24
    expected_total = 24

    # Check notes for truncation message
    truncation_note = next((n for n in analysis.notes if "docs list truncated" in n), None)
    assert truncation_note is not None
    assert f"total={expected_total}" in truncation_note
    assert len(analysis.docs) == 10
