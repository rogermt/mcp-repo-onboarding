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
