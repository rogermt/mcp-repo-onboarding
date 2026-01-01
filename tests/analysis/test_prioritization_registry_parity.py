from __future__ import annotations

import pytest

from mcp_repo_onboarding.analysis.prioritization import (
    get_config_priority,
    get_dep_priority,
    get_doc_priority,
)

# =============================================================================
# Config Priority: Expected Values (Curated Test Vectors)
# =============================================================================

CONFIG_EXPECTED_VALUES = [
    # (path, expected_score, reason)
    ("makefile", 400, "exact match (300) + root bonus (100)"),
    ("justfile", 400, "exact match (300) + root bonus (100)"),
    ("tox.ini", 300, "exact match (300), root bonus does not apply when exact overrides"),
    ("src/tox.ini", 200, "exact match, nested, no root bonus"),
    (".github/workflows/ci.yml", 150, "workflows prefix"),
    (".github/workflows/test/nested.yml", 150, "workflows prefix nested"),
    ("unknown.txt", 110, "base score (10) + root bonus (100)"),
    ("root_unknown.txt", 110, "base score (10) + root bonus (100)"),
    (
        ".pre-commit-config.yaml",
        300,
        "exact match (200), root bonus does not apply when exact overrides",
    ),
    ("pytest.ini", 300, "exact match (200), root bonus does not apply when exact overrides"),
    ("noxfile.py", 300, "exact match (200), root bonus does not apply when exact overrides"),
]


@pytest.mark.parametrize("path,expected,reason", CONFIG_EXPECTED_VALUES)
def test_config_priority_expected_values(path: str, expected: int, reason: str) -> None:
    """Verify config scoring matches expected values (registered rules)."""
    actual = get_config_priority(path)
    assert actual == expected, f"{reason}: got {actual}, expected {expected}"


# =============================================================================
# Doc Priority: Expected Values (Curated Test Vectors)
# =============================================================================

DOC_EXPECTED_VALUES = [
    # (path, expected_score, reason)
    ("README.md", 300, "root prefix + root position"),
    ("readme.txt", 300, "root prefix + root position (case-insensitive)"),
    ("CONTRIBUTING.md", 300, "root prefix + root position"),
    ("LICENSE", 300, "root prefix + root position"),
    ("docs/guide.md", 250, "docs direct child"),
    ("docs/nested/guide.md", 150, "docs nested"),
    ("quickstart.md", 200, "keyword match"),
    ("INSTALL.rst", 200, "keyword match"),
    ("setup_guide.md", 200, "keyword match (setup)"),
    ("tutorial.md", 200, "keyword match"),
    ("admin_docs.md", 30, "base score (50) - admin penalty (20)"),
    (
        "tests/README.md",
        -150,
        "root prefix (300) - tests penalty (200) - but 300 is exceeded by penalty",
    ),
    ("src/README.md", -150, "root prefix but under src/ penalty"),
    ("unknown.md", 50, "base score only"),
    ("docs/admin/guide.md", 130, "docs nested (150) - admin penalty (20)"),
]


@pytest.mark.parametrize("path,expected,reason", DOC_EXPECTED_VALUES)
def test_doc_priority_expected_values(path: str, expected: int, reason: str) -> None:
    """Verify doc scoring matches expected values (registered rules)."""
    actual = get_doc_priority(path)
    assert actual == expected, f"{reason}: got {actual}, expected {expected}"


# =============================================================================
# Dep Priority: Expected Values (Curated Test Vectors)
# =============================================================================

DEP_EXPECTED_VALUES = [
    # (path, expected_score, reason)
    ("pyproject.toml", 300, "manifest at root"),
    ("src/pyproject.toml", 150, "manifest nested"),
    ("requirements.txt", 300, "manifest at root"),
    ("requirements-dev.txt", 300, "manifest at root"),
    ("sub/requirements.txt", 150, "manifest nested"),
    ("setup.py", 100, "not a manifest, base score"),
    ("tests/requirements.txt", -50, "manifest but under tests/ penalty"),
    ("test/pyproject.toml", -50, "manifest but under test/ penalty"),
    ("examples/requirements.txt", -50, "manifest but under examples/ penalty"),
    ("scripts/requirements.txt", -50, "manifest but under scripts/ penalty"),
]


@pytest.mark.parametrize("path,expected,reason", DEP_EXPECTED_VALUES)
def test_dep_priority_expected_values(path: str, expected: int, reason: str) -> None:
    """Verify dep scoring matches expected values (registered rules)."""
    actual = get_dep_priority(path)
    assert actual == expected, f"{reason}: got {actual}, expected {expected}"


# =============================================================================
# Registry Parity: Ensure scoring is deterministic and stable
# =============================================================================


def test_scoring_is_deterministic() -> None:
    """Call scoring functions multiple times; results must be identical."""
    test_paths = ["makefile", "docs/guide.md", "pyproject.toml", "src/README.md"]
    for path in test_paths:
        r1 = (
            get_config_priority(path),
            get_doc_priority(path),
            get_dep_priority(path),
        )
        r2 = (
            get_config_priority(path),
            get_doc_priority(path),
            get_dep_priority(path),
        )
        assert r1 == r2, f"Non-deterministic scoring for {path}"


def test_root_bonus_preserved() -> None:
    """Root files must consistently outrank nested files by bonus amount."""
    # Config: root makefile vs nested should differ by 100
    root_config = get_config_priority("makefile")
    nested_config = get_config_priority("src/makefile")
    assert root_config - nested_config == 100, "Root bonus not preserved for config"

    # Dep: root pyproject vs nested should differ by 150
    root_dep = get_dep_priority("pyproject.toml")
    nested_dep = get_dep_priority("sub/pyproject.toml")
    assert root_dep - nested_dep == 150, "Manifest scoring not preserved for dep"


def test_manifest_distinction_preserved() -> None:
    """Manifest files (pyproject.toml, requirements*) must score differently from non-manifest."""
    manifest_root = get_dep_priority("requirements.txt")
    non_manifest_root = get_dep_priority("setup.py")
    assert manifest_root > non_manifest_root, "Manifest scoring not distinct from non-manifest"

    manifest_nested = get_dep_priority("sub/requirements.txt")
    non_manifest_nested = get_dep_priority("sub/setup.py")
    assert manifest_nested > non_manifest_nested, "Manifest nested scoring not distinct"
