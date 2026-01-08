from __future__ import annotations

from mcp_repo_onboarding.resources import load_mcp_prompt


def test_prompt_is_v2_first_renderer() -> None:
    prompt = load_mcp_prompt()

    # Must clearly prioritize v2 markdown verbatim rendering
    assert "PRIMARY PATH — Blueprint v2" in prompt
    assert "onboarding_blueprint_v2.render.markdown" in prompt
    assert "EXACTLY" in prompt and "that string" in prompt

    # v1 must not be the primary path
    assert "SECONDARY PATH — Blueprint v1" in prompt

    # Hard bans to prevent shell/python emulation loops
    assert "use the Shell tool" in prompt and "DO NOT" in prompt
    assert "attempt tool emulation" in prompt and "MUST NOT" in prompt
    assert "No Retries + Circuit Breaker" in prompt

    # Version marker prevents "which prompt is actually shipped" confusion
    assert "blueprint-v2-renderer-2025-12-31" in prompt
