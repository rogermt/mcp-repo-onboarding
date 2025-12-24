#!/usr/bin/env bash
set -euo pipefail

# This script runs the evaluation for specific repositories (up to 3).
# Usage: ./run_specific_repos.sh repo1 repo2 repo3

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 repo1 [repo2] [repo3]"
  exit 1
fi

if [ "$#" -gt 3 ]; then
  echo "Error: Maximum 3 repositories allowed."
  exit 1
fi

repos=("$@")
export prompt="Follow instructions in file: .gemini/B-prompt.txt"
orig_dir="$PWD"
LOG_FILE="evaluation_results.log"

{
echo " "
echo "=== Running evaluation for: ${repos[*]} ==="
echo "Logging to: ${LOG_FILE}"
echo " "

# First loop: run gemini with pushd/popd
for repo in "${repos[@]}"; do
  echo "=== Running gemini for $repo ==="
  export repo="$repo"
  if [ -d "$HOME/$repo" ]; then
    pushd "$HOME/$repo" > /dev/null
    gemini -p "$prompt" -m gemini-2.5-flash --yolo
    popd > /dev/null
    echo "Waiting 30 seconds for rate limits..."
    sleep 30
  else
    echo "Directory $HOME/$repo does not exist; skipping gemini for $repo"
  fi
done

# Second loop: print dd header and cat ONBOARDING.md
for repo in "${repos[@]}"; do
  echo " "
  echo "=== Showing ONBOARDING.md for $repo ==="
  if [ -f "$HOME/$repo/ONBOARDING.md" ]; then
    pushd "$HOME/$repo" > /dev/null
    printf "=== Repo: %s ===\n" "$repo" | dd of=/dev/stdout 2>/dev/null
    cat ONBOARDING.md
    popd > /dev/null
  else
    echo "No ONBOARDING.md in $HOME/$repo; skipping"
  fi
done

echo " "
echo "=== Evaluation complete ==="
echo " "
} 2>&1 | tee "${LOG_FILE}"
