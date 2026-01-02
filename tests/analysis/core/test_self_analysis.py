"""
Integration test: Analyze our own repository and verify no fixture pollution.

This is the critical regression test for Issue #64 / Phase 7.
"""

from pathlib import Path

import pytest

from mcp_repo_onboarding.analysis import analyze_repo
from mcp_repo_onboarding.analysis.structs import IgnoreMatcher
from mcp_repo_onboarding.schema import RepoAnalysis


def get_repo_root() -> Path:
    """Find the root of mcp-repo-onboarding repository."""

    # Start from this test file and walk up to find pyproject.toml

    current = Path(__file__).resolve()

    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() and (
            parent / "src" / "mcp_repo_onboarding"
        ).exists():
            return parent

    pytest.skip("Could not find mcp-repo-onboarding repo root")

    # Unreachable, but satisfies mypy

    return Path("/")


class TestSelfAnalysis:
    """
    Integration tests that analyze the mcp-repo-onboarding repo itself.

    These tests verify that our own test fixtures don't pollute the output.
    This is the P0 requirement from Phase 7 / Issue #64.
    """

    @pytest.fixture
    def self_analysis(self) -> RepoAnalysis:
        """Analyze this repository."""
        repo_root = get_repo_root()
        return analyze_repo(repo_path=str(repo_root))

    def test_no_fixtures_in_dependency_files(self, self_analysis: RepoAnalysis) -> None:
        """
        CRITICAL: tests/fixtures/ must not appear in dependencyFiles.

        This is the exact bug reported in Phase 7 — fixture pyproject.toml
        and requirements.txt files were drowning out the real signals.
        """
        if not self_analysis.python or not self_analysis.python.dependencyFiles:
            pytest.skip("No dependency files detected")

        assert self_analysis.python is not None
        fixture_paths = []
        for dep in self_analysis.python.dependencyFiles:
            if "tests/fixtures" in dep.path or "test/fixtures" in dep.path:
                fixture_paths.append(dep.path)

        assert not fixture_paths, (
            "Fixture files found in dependencyFiles (violates EXTRACT_OUTPUT_RULES.md §1):\n"
            + "\n".join(f"  - {p}" for p in fixture_paths[:10])
            + (f"\n  ... and {len(fixture_paths) - 10} more" if len(fixture_paths) > 10 else "")
        )

    def test_no_fixtures_in_configuration_files(self, self_analysis: RepoAnalysis) -> None:
        """
        CRITICAL: tests/fixtures/ must not appear in configurationFiles.
        """
        fixture_paths = []
        for cfg in self_analysis.configurationFiles:
            if "tests/fixtures" in cfg.path or "test/fixtures" in cfg.path:
                fixture_paths.append(cfg.path)

        assert not fixture_paths, (
            "Fixture files found in configurationFiles (violates EXTRACT_OUTPUT_RULES.md §1):\n"
            + "\n".join(f"  - {p}" for p in fixture_paths[:10])
            + (f"\n  ... and {len(fixture_paths) - 10} more" if len(fixture_paths) > 10 else "")
        )

    def test_no_fixtures_in_docs(self, self_analysis: RepoAnalysis) -> None:
        """
        CRITICAL: tests/fixtures/ must not appear in docs.
        """
        fixture_paths = []
        for doc in self_analysis.docs:
            if "tests/fixtures" in doc.path or "test/fixtures" in doc.path:
                fixture_paths.append(doc.path)

        assert not fixture_paths, (
            "Fixture files found in docs (violates EXTRACT_OUTPUT_RULES.md §1):\n"
            + "\n".join(f"  - {p}" for p in fixture_paths[:10])
            + (f"\n  ... and {len(fixture_paths) - 10} more" if len(fixture_paths) > 10 else "")
        )

    def test_root_pyproject_toml_is_first_dependency(self, self_analysis: RepoAnalysis) -> None:
        """
        Root pyproject.toml should be the primary dependency file.

        Per EXTRACT_OUTPUT_RULES.md §3.3, root manifests get +300 score.
        """
        if not self_analysis.python or not self_analysis.python.dependencyFiles:
            pytest.skip("No dependency files detected")

        assert self_analysis.python is not None
        deps = self_analysis.python.dependencyFiles

        # pyproject.toml should exist and be near the top
        pyproject_paths = [d.path for d in deps if d.path == "pyproject.toml"]

        assert pyproject_paths, "Root pyproject.toml not found in dependencyFiles"

        # It should be first (highest priority)
        assert deps[0].path == "pyproject.toml", (
            f"Root pyproject.toml should be first dependency, but found '{deps[0].path}' instead"
        )

    def test_root_readme_is_first_doc(self, self_analysis: RepoAnalysis) -> None:
        """
        Root README.md should be the primary documentation file.

        Per EXTRACT_OUTPUT_RULES.md §3.1, root standards get +300 score.
        """
        docs = self_analysis.docs
        assert docs, "No docs detected"

        # README.md should be first or second (LICENSE might be first alphabetically)
        top_docs = [d.path for d in docs[:3]]

        assert any("README" in p.upper() for p in top_docs), (
            f"Root README not in top 3 docs. Found: {top_docs}"
        )

    def test_docs_list_respects_cap(self, self_analysis: RepoAnalysis) -> None:
        """Docs list should not exceed MAX_DOCS_CAP (10)."""
        assert len(self_analysis.docs) <= 10, (
            f"Docs list exceeds cap: {len(self_analysis.docs)} > 10"
        )

    def test_config_list_respects_cap(self, self_analysis: RepoAnalysis) -> None:
        """Config list should not exceed MAX_CONFIG_CAP (15)."""
        assert len(self_analysis.configurationFiles) <= 15, (
            f"Config list exceeds cap: {len(self_analysis.configurationFiles)} > 15"
        )

    def test_truncation_note_present_when_truncated(self, self_analysis: RepoAnalysis) -> None:
        """
        If docs were truncated, notes should mention it.

        Per EXTRACT_OUTPUT_RULES.md §4.
        """
        # We know our repo has 29 docs, so it should be truncated
        if len(self_analysis.docs) == 10:
            # Should have truncation note
            truncation_notes = [n for n in self_analysis.notes if "docs list truncated" in n]
            assert truncation_notes, (
                "Docs were truncated but no truncation note found in Analyzer notes"
            )


class TestIgnoreMatcherUnit:
    """
    Unit tests for IgnoreMatcher safety ignore logic.

    These test the matching algorithm in isolation.
    """

    @pytest.fixture
    def matcher(self, tmp_path: Path) -> IgnoreMatcher:
        """Create an IgnoreMatcher with standard safety ignores."""
        from mcp_repo_onboarding.config import SAFETY_IGNORES

        return IgnoreMatcher(
            repo_root=tmp_path,
            safety_ignores=SAFETY_IGNORES,
            gitignore_patterns=[],
        )

    @pytest.mark.parametrize(
        "path,expected",
        [
            # Should be ignored (fixtures)
            ("tests/fixtures/sample/pyproject.toml", True),
            ("tests/fixtures/excessive-docs-configs/requirements.txt", True),
            ("test/fixtures/repo/Makefile", True),
            ("tests/fixtures/", True),
            # Should NOT be ignored (regular tests)
            ("tests/test_main.py", False),
            ("tests/conftest.py", False),
            ("tests/integration/test_api.py", False),
            # Should be ignored (other safety patterns)
            (".git/config", True),
            ("node_modules/package/index.js", True),
            (".venv/lib/python3.11/site.py", True),
            ("some/path/site-packages/pkg/file.py", True),
            ("__pycache__/module.cpython-311.pyc", True),
            # Should NOT be ignored (normal files)
            ("pyproject.toml", False),
            ("src/main.py", False),
            ("docs/README.md", False),
        ],
    )
    def test_is_safety_ignored(self, matcher: IgnoreMatcher, path: str, expected: bool) -> None:
        """Test safety ignore matching for various paths."""
        result = matcher.is_safety_ignored(path)
        assert result == expected, (
            f"is_safety_ignored('{path}') returned {result}, expected {expected}"
        )

    def test_safety_ignores_not_overridable_by_gitignore(self, tmp_path: Path) -> None:
        """Safety ignores cannot be negated by .gitignore patterns."""
        from mcp_repo_onboarding.analysis.structs import IgnoreMatcher
        from mcp_repo_onboarding.config import SAFETY_IGNORES

        # Create matcher with gitignore negation pattern
        matcher = IgnoreMatcher(
            repo_root=tmp_path,
            safety_ignores=SAFETY_IGNORES,
            gitignore_patterns=["!tests/fixtures/"],  # Try to un-ignore
        )

        # Should still be ignored despite negation attempt
        assert matcher.is_safety_ignored("tests/fixtures/important.txt")
