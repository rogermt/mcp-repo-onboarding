#!/bin/bash

# Source B-prompt.txt path from the current working directory

# Target repositories (relative to your home directory)
REPOS=("searxng" "imgix-python" "Paper2Code" "wagtail" "connexion")

echo "Starting updates for specified repositories..."
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

        echo "  - Copied B-prompt.txt to ${B_PROMPT_DEST_FILE}"
    else
    fi
    echo ""
done

echo "All specified repositories have been processed."
