from mcp_repo_onboarding.resources import load_mcp_prompt


def test_prompt_loads_and_contains_anchors() -> None:
    text = load_mcp_prompt()
    assert "You are running the repository onboarding signal extraction" in text
    assert "Step 1 — Call MCP tools" in text
    assert "write_onboarding" in text
    assert "Frameworks bullet template (hard rule)" in text
