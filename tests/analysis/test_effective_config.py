from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo
from mcp_repo_onboarding.effective_config import REQUIRED_SAFETY_IGNORES, EffectiveConfig


def test_effective_config_default_matches_none(temp_repo: Callable[[str], Path]) -> None:
    """
    Acceptance: with no overrides, behavior is unchanged.
    We assert: analyze_repo(None) == analyze_repo(EffectiveConfig()).
    """
    repo = temp_repo("phase3-2-tox-nox-make")

    a1 = analyze_repo(str(repo))
    a2 = analyze_repo(str(repo), effective_config=EffectiveConfig())

    assert a1.model_dump(exclude_none=True) == a2.model_dump(exclude_none=True)


def test_required_fixture_ignores_are_always_present() -> None:
    cfg = EffectiveConfig()
    for p in REQUIRED_SAFETY_IGNORES:
        assert p in cfg.safety_ignores


def test_fixtures_ignore_cannot_be_disabled_even_with_empty_overrides(tmp_path: Path) -> None:
    """
    Safety acceptance: tests/fixtures/ ignore cannot be disabled by any override mechanism.

    This repo contains ONLY dependency signals under tests/fixtures/.
    If fixtures were not ignored, analysis.python would be populated.
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    noise = repo / "tests" / "fixtures" / "noise"
    noise.mkdir(parents=True)

    (noise / "pyproject.toml").write_text(
        "[project]\nname='noise'\nversion='0.0.0'\n",
        encoding="utf-8",
    )
    (noise / "requirements.txt").write_text("requests\n", encoding="utf-8")

    a = analyze_repo(str(repo), effective_config=EffectiveConfig())

    assert a.docs == []
    assert a.configurationFiles == []
    assert a.python is None
