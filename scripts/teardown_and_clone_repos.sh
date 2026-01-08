#!/bin/bash
set -euo pipefail

BASE_DIR="/home/rogermt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOS_LIST="${SCRIPT_DIR}/eval_repos.list"

# Verify eval_repos.list exists
if [[ ! -f "${REPOS_LIST}" ]]; then
    echo "ERROR: ${REPOS_LIST} not found"
    exit 1
fi

echo "Starting safe teardown and re-cloning..."

# Parse eval_repos.list and process each repo
while IFS='|' read -r REPO_NAME CLONE_URL BRANCH DOWNLOAD; do
    # Skip empty lines and comments
    [[ -z "$REPO_NAME" || "$REPO_NAME" =~ ^# ]] && continue
    
    # Trim whitespace
    REPO_NAME=$(echo "$REPO_NAME" | xargs)
    CLONE_URL=$(echo "$CLONE_URL" | xargs)
    BRANCH=$(echo "$BRANCH" | xargs)
    DOWNLOAD=$(echo "$DOWNLOAD" | xargs)
    
    # Skip if download flag is N
    if [[ "$DOWNLOAD" != "Y" ]]; then
        echo "Skipping ${REPO_NAME} (download=N)"
        continue
    fi
    
    # Skip local repos
    if [[ "$CLONE_URL" == "local" ]]; then
        echo "Skipping ${REPO_NAME} (local repo)"
        continue
    fi
    
    # Validate repo name
    if [[ -z "${REPO_NAME}" ]]; then
        echo "ERROR: Empty REPO_NAME detected. Aborting."
        exit 1
    fi
    
    REPO_PATH="${BASE_DIR}/${REPO_NAME}"
    
    # Safety checks
    case "${REPO_PATH}" in
        "/"|"/home"|"/home/"*"/"|"${BASE_DIR}"|"${BASE_DIR}/")
            echo "ERROR: Unsafe REPO_PATH '${REPO_PATH}'. Aborting."
            exit 1
            ;;
    esac
    
    echo "Processing ${REPO_NAME}"
    
    # Only delete if it's a git repo
    if [[ -d "${REPO_PATH}" ]]; then
        if [[ -d "${REPO_PATH}/.git" ]]; then
            echo "  - Removing existing repo at ${REPO_PATH}"
            rm -rf "${REPO_PATH}"
        else
            echo "  - WARNING: ${REPO_PATH} exists but is NOT a git repo. Skipping deletion."
        fi
    fi
    
    echo "  - Cloning ${CLONE_URL} (branch: ${BRANCH})"
    if [[ "${BRANCH}" == "main" ]]; then
        git clone "${CLONE_URL}" "${REPO_PATH}"
    else
        git clone -b "${BRANCH}" "${CLONE_URL}" "${REPO_PATH}"
    fi
    
    echo ""
done < "$REPOS_LIST"

echo "Done."
