from mcp_repo_onboarding.resources import load_mcp_prompt


def test_prompt_loads_and_contains_anchors() -> None:
    text = load_mcp_prompt()
    assert "PROMPT_VERSION = blueprint-v2-renderer-2025-12-31" in text
    assert "Step 1 — Call MCP tools" in text
    assert "write_onboarding" in text
    assert "PRIMARY PATH — Blueprint v2 (hard rule)" in text
