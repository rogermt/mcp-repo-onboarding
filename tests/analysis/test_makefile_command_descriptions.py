from collections.abc import Callable
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def _write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


def test_make_install_has_description(temp_repo: Callable[[str], Path]) -> None:
    repo = temp_repo("makefile-with-recipes")
    _write(
        repo / "Makefile",
        """
install:
\t@echo "Installing dependencies..."
\tpython setup.py install

.PHONY: install
""".lstrip(),
    )
    a = analyze_repo(repo_path=str(repo))
    assert a.scripts.install[0].description is not None
    assert len(a.scripts.install[0].description) > 0
