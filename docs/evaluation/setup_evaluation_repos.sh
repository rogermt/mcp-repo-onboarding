#!/bin/bash

# Source B-prompt.txt path from the current working directory
B_PROMPT_SOURCE="$(pwd)/docs/evaluation/B-prompt.txt"

# Target repositories (relative to your home directory)
REPOS=("searxng" "imgix-python" "Paper2Code" "wagtail" "connexion")

echo "Starting updates for specified repositories..."
echo "Using B-prompt source: ${B_PROMPT_SOURCE}"
echo ""

for REPO_NAME in "${REPOS[@]}"; do
    # Construct the full path to the repository
    REPO_PATH="/home/rogermt/${REPO_NAME}"
    GEMINI_DIR="${REPO_PATH}/.gemini"
    SETTINGS_FILE="${GEMINI_DIR}/settings.json"

    # Corrected destination for B-prompt.txt: inside .gemini folder
    B_PROMPT_DEST_DIR="${GEMINI_DIR}"
    B_PROMPT_DEST_FILE="${B_PROMPT_DEST_DIR}/B-prompt.txt"

    echo "Processing repository: ${REPO_PATH}"

    # 1. Update .gemini/settings.json
    # Create the .gemini directory if it doesn't exist
    mkdir -p "${GEMINI_DIR}"

    # Construct the JSON content, dynamically setting REPO_ROOT
    JSON_CONTENT=$(cat <<EOF
{
  "mcpServers": {
    "repo-onboarding": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/rogermt/mcp-repo-onboarding",
        "run",
        "mcp-repo-onboarding"
      ],
      "env": {
        "REPO_ROOT": "${REPO_PATH}"
      },
      "tooling": {
        "disableTools": ["run_shell_command", "web_fetch", "google_web_search"]
      }
    }
  }
}
EOF
)
    # Write the JSON content to the settings file
    echo "${JSON_CONTENT}" > "${SETTINGS_FILE}"
    echo "  - Updated ${SETTINGS_FILE}"

    # 2. Copy B-prompt.txt
    if [ -f "${B_PROMPT_SOURCE}" ]; then
        # Create the destination directory (already exists from .gemini mkdir, but good to be explicit)
        mkdir -p "${B_PROMPT_DEST_DIR}"
        # Copy the B-prompt.txt file
        cp "${B_PROMPT_SOURCE}" "${B_PROMPT_DEST_FILE}"
        echo "  - Copied B-prompt.txt to ${B_PROMPT_DEST_FILE}"
    else
        echo "  - Error: B-prompt.txt source file not found at ${B_PROMPT_SOURCE}. Skipping copy."
    fi
    echo ""
done

echo "All specified repositories have been processed."
