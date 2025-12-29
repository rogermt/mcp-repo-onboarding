# Development Plan - Phase 7 UX Automation

## Goal
Implement UX automation by exposing the onboarding prompt as an MCP Prompt and an MCP Resource.

## Tasks

1. **Test-Driven Development (TDD):**

    - Create `tests/test_server_features.py` to test the new prompt and tool.

    - Run tests and confirm failure.

2. **Implementation:**

    - Update `src/mcp_repo_onboarding/server.py` to include:

        - `generate_onboarding` prompt.

        - `get_onboarding_template` tool.

3. **Verification:**

    - Run tests and confirm they pass.

    - Verify with `uv run pytest`.



## Verification Plan

- `test_generate_onboarding_prompt`: Verifies that the prompt is registered and returns the correct text.

- `test_get_onboarding_template_tool`: Verifies that the tool is registered and returns the correct text.
