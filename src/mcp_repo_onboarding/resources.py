from pathlib import Path

# Path to the internal prompt file (lives in same directory as this file)
PROMPT_FILE = Path(__file__).parent / "mcp_prompt.md"


def load_mcp_prompt() -> str:
    """Load the authoritative onboarding prompt text."""
    if not PROMPT_FILE.exists():
        return "Error: Internal prompt file 'mcp_prompt.md' not found."
    return PROMPT_FILE.read_text(encoding="utf-8")
