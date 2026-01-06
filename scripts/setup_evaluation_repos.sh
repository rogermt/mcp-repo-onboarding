#!/bin/bash
set -euo pipefail

# ------------------------------------------------------------------------------
# Phase 10 eval repo: deterministic Node-primary minimal repo
# ------------------------------------------------------------------------------
NODE_REPO_NAME="node-primary-min"
NODE_REPO_PATH="$HOME/$NODE_REPO_NAME"

mkdir -p "$NODE_REPO_PATH"

# Minimal Node-primary evidence (no Python evidence)
cat > "$NODE_REPO_PATH/package.json" <<'JSON'
{
  "name": "node-primary-min",
  "version": "0.0.0",
  "private": true,
  "scripts": {
    "dev": "node -e \"console.log('dev')\"",
    "start": "node -e \"console.log('start')\"",
    "test": "node -e \"console.log('test')\"",
    "lint": "node -e \"console.log('lint')\"",
    "format": "node -e \"console.log('format')\""
  }
}
JSON

# Lockfile to force npm selection and npm ci
cat > "$NODE_REPO_PATH/package-lock.json" <<'JSON'
{}
JSON

# Minimal docs so docs section is non-trivial
cat > "$NODE_REPO_PATH/README.md" <<'MD'
# node-primary-min

Deterministic Node-primary repository used for evaluation.
MD

cat > "$NODE_REPO_PATH/LICENSE" <<'TXT'
MIT License
TXT

# ------------------------------------------------------------------------------
# Target repositories (relative to your home directory)
# ------------------------------------------------------------------------------
REPOS=(
  "searxng"
  "imgix-python"
  "Paper2Code"
  "wagtail"
  "connexion"
  "DeepCode"
  "gradio-bbox"
  "nanobanana"
  "gemmit"
  "gemini-cli"
  "mcp-repo-onboarding"
  "node-primary-min"
)

echo "Starting updates for specified repositories..."
echo ""

for REPO_NAME in "${REPOS[@]}"; do
    REPO_PATH="$HOME/${REPO_NAME}"
    GEMINI_DIR="${REPO_PATH}/.gemini"
    SETTINGS_FILE="${GEMINI_DIR}/settings.json"

    echo "Processing repository: ${REPO_PATH}"

    # Create the .gemini directory if it doesn't exist
    mkdir -p "${GEMINI_DIR}"

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
      }
    }
  }
}
EOF
)
    echo "${JSON_CONTENT}" > "${SETTINGS_FILE}"
    echo "  - Updated ${SETTINGS_FILE}"
    echo ""
done

echo "All specified repositories have been processed."