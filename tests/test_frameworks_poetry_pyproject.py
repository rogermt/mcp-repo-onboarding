from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_detects_flask_from_poetry_dependencies(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("fw-poetry-flask")
    _write(
        repo / "pyproject.toml",
        """
[tool.poetry]
name = "connexion"
version = "0.0.0"

[tool.poetry.dependencies]
python = "^3.9"
flask = { version = ">= 2.2", extras = ["async"], optional = true }

[build-system]
requires = ["poetry-core>=1.2.0"]
build-backend = "poetry.core.masonry.api"
""".lstrip(),
    )

    a = analyze_repo(repo_path=str(repo))
    fw = {f.name: f for f in a.frameworks}

    assert "Flask" in fw
    assert fw["Flask"].evidencePath == "pyproject.toml"
    assert fw["Flask"].keySymbols == ["tool.poetry.dependencies.flask"]
    # optional=true in Poetry deps should be reflected in the detection reason (neutral, non-prescriptive)
    reason = fw["Flask"].detectionReason
    assert "pyproject.toml" in reason
    assert "Poetry" in reason
    assert "dependency key 'flask'" in reason
    assert "(optional)" in reason
