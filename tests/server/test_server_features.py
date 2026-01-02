import json

import pytest

from mcp_repo_onboarding.server import mcp


@pytest.mark.anyio
async def test_generate_onboarding_prompt_exists() -> None:
    """Verify that the generate_onboarding prompt is registered."""
    prompts = await mcp.list_prompts()
    names = [p.name for p in prompts]
    assert "generate_onboarding" in names or "generate-onboarding" in names


@pytest.mark.anyio
async def test_get_onboarding_template_tool_exists() -> None:
    """Verify that the get_onboarding_template tool is registered."""
    tools = await mcp.list_tools()
    names = [t.name for t in tools]
    assert "get_onboarding_template" in names or "get-onboarding-template" in names


@pytest.mark.anyio
async def test_prompt_content() -> None:
    """Verify that the prompt returns the expected content."""
    from mcp_repo_onboarding.resources import load_mcp_prompt

    expected = load_mcp_prompt()

    from mcp_repo_onboarding.server import generate_onboarding

    assert generate_onboarding() == expected


@pytest.mark.anyio
async def test_tool_content() -> None:
    """Verify that the tool returns the expected content."""
    from mcp_repo_onboarding.resources import load_mcp_prompt

    expected = load_mcp_prompt()

    from mcp_repo_onboarding.server import get_onboarding_template

    assert get_onboarding_template() == expected


def test_analyze_repo_includes_blueprint(tmp_path: pytest.TempPathFactory) -> None:
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
