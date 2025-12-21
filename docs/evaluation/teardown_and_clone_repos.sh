#!/bin/bash

# Define the base directory where repositories are located
BASE_DIR="/home/rogermt"

# Define repositories and their clone URLs/branches
# Format: "REPO_NAME|CLONE_URL|BRANCH"
REPOS=(
    "searxng|https://github.com/searxng/searxng.git|main"
    "imgix-python|https://github.com/imgix/imgix-python.git|main"
    "Paper2Code|https://github.com/rogermt/Paper2Code.git|feature/litellm-support"
    "DeepCode|https://github.com/rogermt/DeepCode.git|main"
)

echo "Starting teardown and re-cloning of repositories in ${BASE_DIR}..."
echo ""

for REPO_INFO in "${REPOS[@]}"; do
    # Parse REPO_INFO into name, URL, and branch using '|' as delimiter
    IFS='|' read -r REPO_NAME CLONE_URL BRANCH <<< "${REPO_INFO}"
    REPO_PATH="${BASE_DIR}/${REPO_NAME}"

    echo "Processing repository: ${REPO_NAME}"

    # 1. Teardown (delete existing directory)
    if [ -d "${REPO_PATH}" ]; then
        echo "  - Deleting existing directory: ${REPO_PATH}"
        rm -rf "${REPO_PATH}"
    else
        echo "  - Directory not found, skipping deletion: ${REPO_PATH}"
    fi

    # 2. Clone the repository
    echo "  - Cloning ${CLONE_URL} (branch: ${BRANCH}) into ${REPO_PATH}"
    # Check if the branch is "main" to use the default clone, otherwise specify branch
    if [ "${BRANCH}" == "main" ]; then
        git clone "${CLONE_URL}" "${REPO_PATH}"
    else
        git clone -b "${BRANCH}" "${CLONE_URL}" "${REPO_PATH}"
    fi

    if [ $? -eq 0 ]; then
        echo "  - Successfully cloned ${REPO_NAME}"
    else
        echo "  - Error cloning ${REPO_NAME}"
    fi
    echo ""
done

echo "Teardown and re-cloning process complete."