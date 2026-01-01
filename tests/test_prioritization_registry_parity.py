from __future__ import annotations

import pytest

from mcp_repo_onboarding.analysis import prioritization as prio


@pytest.mark.parametrize(
    "path",
    [
        # root configs
        "Makefile",
        "Justfile",
        "tox.ini",
        "pytest.ini",
        ".pre-commit-config.yaml",
        # workflows
        ".github/workflows/ci.yml",
        ".github/workflows/release.yaml",
        # nested configs
        "docs/tox.ini",
        "subdir/pytest.ini",
    ],
)
def test_config_priority_parity(path: str) -> None:
    assert prio.get_config_priority(path) == prio._legacy_get_config_priority(path)


@pytest.mark.parametrize(
    "path",
    [
        # root standard docs
        "README.md",
        "README.rst",
        "CONTRIBUTING.md",
        "LICENSE",
        "SECURITY.md",
        # docs direct children
        "docs/index.md",
        "docs/README.md",
        # docs nested
        "docs/api/v1/intro.md",
        # keyword hits
        "guides/install.md",
        "setup/guide.md",
        "tutorials/quickstart.md",
        # penalties: deprioritized dirs
        "tests/README.md",
        "examples/install.md",
        "src/quickstart.md",
        # admin penalty
        "docs/admin/installation.md",
    ],
)
def test_doc_priority_parity(path: str) -> None:
    assert prio.get_doc_priority(path) == prio._legacy_get_doc_priority(path)


@pytest.mark.parametrize(
    "path",
    [
        # root manifests
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        # nested manifests
        "examples/requirements.txt",
        "subproj/pyproject.toml",
        # penalties
        "tests/requirements.txt",
        "examples/requirements-dev.txt",
        "scripts/requirements.txt",
        # non-manifest
        "constraints.txt",  # should remain base score in legacy
    ],
)
def test_dep_priority_parity(path: str) -> None:
    assert prio.get_dep_priority(path) == prio._legacy_get_dep_priority(path)
