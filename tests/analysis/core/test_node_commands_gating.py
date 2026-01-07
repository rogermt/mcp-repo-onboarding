from __future__ import annotations

from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _all_script_commands(a) -> list[str]:
    groups = [
        a.scripts.install,
        a.scripts.dev,
        a.scripts.start,
        a.scripts.test,
        a.scripts.lint,
        a.scripts.format,
        a.scripts.other,
    ]
    out: list[str] = []
    for g in groups:
        if g:
            out.extend([c.command for c in g if getattr(c, "command", None)])
    return out


def test_node_commands_not_emitted_when_python_is_primary(tmp_path: Path) -> None:
    """
    Mixed repo where Python wins by score:
      Python: pyproject (+10) + requirements (+6) = 16
      Node: package.json (+5) + package-lock (+10) = 15
    Expect:
      - primaryTooling == Python
      - no npm commands appear in scripts.*
    """
    repo = tmp_path / "repo"
    repo.mkdir()

    (repo / "pyproject.toml").write_text(
        "[project]\nname='x'\nversion='0.0.0'\n",
        encoding="utf-8",
    )
    (repo / "requirements.txt").write_text("requests\n", encoding="utf-8")

    (repo / "package.json").write_text(
        '{"name":"x","version":"0.0.0","scripts":{"test":"echo test","lint":"echo lint"}}',
        encoding="utf-8",
    )
    (repo / "package-lock.json").write_text("{}", encoding="utf-8")

    a = analyze_repo(str(repo))

    assert a.primaryTooling == "Python"

    cmds = _all_script_commands(a)
    assert not any(c.startswith("npm ") for c in cmds), f"Unexpected npm commands: {cmds}"

    # Optional: verify Node evidence is still detected (polyglot support)
    names = {t.name for t in a.otherTooling}
    assert "Node.js" in names
