#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_LIST="${SCRIPT_DIR}/eval_repos.list"

# Verify eval_repos.list exists
if [[ ! -f "${REPOS_LIST}" ]]; then
    echo "ERROR: ${REPOS_LIST} not found"
    exit 1
fi

# Parse eval_repos.list and extract repo names (skip comments and blank lines)
REPOS=()
while IFS='|' read -r REPO_NAME CLONE_URL BRANCH DOWNLOAD; do
    # Skip empty lines and comments
    [[ -z "$REPO_NAME" || "$REPO_NAME" =~ ^# ]] && continue
    
    # Trim whitespace
    REPO_NAME=$(echo "$REPO_NAME" | xargs)
    
    # Add repo name (process all repos regardless of download flag)
    REPOS+=("$REPO_NAME")
done < "$REPOS_LIST"

# Special handling for node-primary-min (synthetic repo)
# Create it if it doesn't exist
NODE_REPO_NAME="node-primary-min"
NODE_REPO_PATH="$HOME/$NODE_REPO_NAME"

if [[ ! -d "$NODE_REPO_PATH" ]]; then
    echo "Creating synthetic Node-primary repo: $NODE_REPO_NAME"
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
fi

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
