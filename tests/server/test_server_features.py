import json
from pathlib import Path

# ... existing code ...


def test_analyze_repo_includes_blueprint(tmp_path: Path) -> None:
    """Verify that analyze_repo includes onboarding_blueprint in output."""
    import os

    from mcp_repo_onboarding.server import analyze_repo

    # Create a minimal Python repo
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / "main.py").write_text("print('hello')\n")

    old_env = os.environ.get("REPO_ROOT")
    try:
        os.environ["REPO_ROOT"] = str(tmp_path)
        result = analyze_repo()
        data = json.loads(result)

        assert "onboarding_blueprint" in data
        bp = data["onboarding_blueprint"]
        assert bp["format"] == "onboarding_blueprint_v2"
        assert bp["render"]["mode"] == "verbatim"
        assert isinstance(bp["render"]["markdown"], str)
        assert "# ONBOARDING.md" in bp["render"]["markdown"]
    finally:
        if old_env is None:
            os.environ.pop("REPO_ROOT", None)
        else:
            os.environ["REPO_ROOT"] = old_env
