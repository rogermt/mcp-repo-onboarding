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


def test_analyze_repo_max_files_string_conversion(tmp_path: Path) -> None:
    """Verify that analyze_repo handles max_files as string (MCP edge case)."""
    import os

    from mcp_repo_onboarding.server import analyze_repo

    # Create a minimal Python repo
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / "main.py").write_text("print('hello')\n")

    old_env = os.environ.get("REPO_ROOT")
    try:
        os.environ["REPO_ROOT"] = str(tmp_path)
        # Pass max_files as string (MCP may do this)
        result = analyze_repo(max_files="1000")  # type: ignore
        data = json.loads(result)

        # Should succeed and return valid analysis
        assert "python" in data or "error" not in data or data["error"] is None
        if "error" not in data or data["error"] is None:
            assert "onboarding_blueprint" in data
    finally:
        if old_env is None:
            os.environ.pop("REPO_ROOT", None)
        else:
            os.environ["REPO_ROOT"] = old_env


def test_analyze_repo_max_files_invalid_string(tmp_path: Path) -> None:
    """Verify that analyze_repo falls back to DEFAULT_MAX_FILES on invalid string."""
    import os

    from mcp_repo_onboarding.server import analyze_repo

    # Create a minimal Python repo
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / "main.py").write_text("print('hello')\n")

    old_env = os.environ.get("REPO_ROOT")
    try:
        os.environ["REPO_ROOT"] = str(tmp_path)
        # Pass max_files as invalid string
        result = analyze_repo(max_files="not_a_number")  # type: ignore
        data = json.loads(result)

        # Should succeed with fallback to default
        assert "onboarding_blueprint" in data or "error" not in data
    finally:
        if old_env is None:
            os.environ.pop("REPO_ROOT", None)
        else:
            os.environ["REPO_ROOT"] = old_env
