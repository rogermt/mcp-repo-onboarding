import json

from mcp_repo_onboarding.server import write_onboarding


def test_write_onboarding_missing_content() -> None:
    """Test that write_onboarding returns ErrorResponse when content is missing."""
    # We call the tool function directly
    result_json = write_onboarding(content=None)
    result = json.loads(result_json)

    assert "error" in result
    assert result["error"] == "Content is required"
    assert result["error_code"] == "INVALID_ARGUMENT"


def test_write_onboarding_invalid_mode() -> None:
    """Test that write_onboarding returns ErrorResponse for invalid mode."""
    # Mode 'invalid' should trigger a ValueError in write_onboarding_svc
    result_json = write_onboarding(content="some content", mode="invalid")
    result = json.loads(result_json)

    assert "error" in result
    assert "mode" in result["error"].lower()
    assert result["error_code"] == "INVALID_ARGUMENT"
    assert "path" in result.get("details", {})
