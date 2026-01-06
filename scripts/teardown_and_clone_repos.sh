#!/bin/bash
set -euo pipefail

BASE_DIR="/home/rogermt"

REPOS=(
    "searxng|https://github.com/searxng/searxng.git|main"
    "imgix-python|https://github.com/imgix/imgix-python.git|main"
    "Paper2Code|https://github.com/rogermt/Paper2Code.git|feature/litellm-support"
    "DeepCode|https://github.com/rogermt/DeepCode.git|main"
    "wagtail|https://github.com/wagtail/wagtail.git|main"
    "connexion|https://github.com/spec-first/connexion.git|main"
    "gradio-bbox|https://github.com/chencn2020/gradio-bbox.git|main"
    "nanobanana|https://github.com/gemini-cli-extensions/nanobanana.git|main"
    "gemmit|https://github.com/tcmartin/gemmit.git|main"
    "gemini-cli|https://github.com/google-gemini/gemini-cli.git|main"
)

echo "Starting safe teardown and re-cloning..."

for REPO_INFO in "${REPOS[@]}"; do
    IFS='|' read -r REPO_NAME CLONE_URL BRANCH <<< "${REPO_INFO}"

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
done

echo "Done."