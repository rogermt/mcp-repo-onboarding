from __future__ import annotations

from mcp_repo_onboarding.config import (
    CONFIG_FILE_TYPES,
    DEPENDENCY_FILE_TYPES,
    classify_filename,
)


def test_config_and_dependency_sets_are_disjoint() -> None:
    assert CONFIG_FILE_TYPES.isdisjoint(DEPENDENCY_FILE_TYPES)


def test_pyproject_is_dependency_only() -> None:
    # Classification API
    assert classify_filename("pyproject.toml") == "dependency"

    # Derived sets (exact-name lists)
    assert "pyproject.toml" in DEPENDENCY_FILE_TYPES
    assert "pyproject.toml" not in CONFIG_FILE_TYPES


def test_known_configs_are_config() -> None:
    assert classify_filename("tox.ini") == "config"
    assert classify_filename(".pre-commit-config.yaml") == "config"
    assert classify_filename("Makefile") == "config"


def test_requirements_prefix_is_dependency() -> None:
    # These are not necessarily in DEPENDENCY_FILE_TYPES (only exact names are),
    # but they must be classified as dependencies for categorization.
    assert classify_filename("requirements.txt") == "dependency"
    assert classify_filename("requirements-dev.txt") == "dependency"
    assert classify_filename("requirements.in") == "dependency"
    assert classify_filename("requirements-dev.in") == "dependency"
