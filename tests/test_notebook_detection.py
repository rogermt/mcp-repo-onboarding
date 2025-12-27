from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def test_notebook_detection_and_notes(temp_repo: Callable[[str], Path]) -> None:
    """
    Test that Jupyter notebooks trigger the required note and populate the notebooks field.
    """
    repo = temp_repo("edge-cases")

    # Create notebooks in different locations
    (repo / "analysis.ipynb").write_text("{}", encoding="utf-8")

    research_dir = repo / "research"
    research_dir.mkdir()
    (research_dir / "experiment.ipynb").write_text("{}", encoding="utf-8")
    (research_dir / "old_experiment.ipynb").write_text(
        "{}", encoding="utf-8"
    )  # Multiple in same dir

    deep_dir = repo / "src" / "deep" / "notebooks"
    deep_dir.mkdir(parents=True)
    (deep_dir / "test.ipynb").write_text("{}", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    # 1. Check notes
    expected_note = "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."
    assert expected_note in analysis.notes

    # 2. Check notebooks field (sorted directory paths)
    # Root is ".", others are relative POSIX paths with trailing slashes
    expected_notebook_dirs = [".", "research/", "src/deep/notebooks/"]
    assert sorted(analysis.notebooks) == sorted(expected_notebook_dirs)
    # Ensure they are sorted in the actual field
    assert analysis.notebooks == sorted(expected_notebook_dirs)


def test_no_notebooks_no_note(temp_repo: Callable[[str], Path]) -> None:
    """
    Test that absence of notebooks does not trigger the note or populate the field.
    """
    repo = temp_repo("edge-cases")
    (repo / "main.py").write_text("print('hello')", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    expected_note = "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."
    assert expected_note not in analysis.notes
    assert len(analysis.notebooks) == 0


def test_notebooks_respect_safety_ignores(temp_repo: Callable[[str], Path]) -> None:
    """
    Test that notebooks in ignored directories (like tests/fixtures) are not detected.
    """
    repo = temp_repo("edge-cases")

    # Notebook in a safety-ignored directory
    fixture_dir = repo / "tests" / "fixtures" / "data"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "ignored.ipynb").write_text("{}", encoding="utf-8")

    analysis = analyze_repo(str(repo))

    expected_note = "Notebook-centric repo detected; core logic may reside in Jupyter notebooks."
    assert expected_note not in analysis.notes
    assert len(analysis.notebooks) == 0
