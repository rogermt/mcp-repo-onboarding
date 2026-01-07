#!/usr/bin/env bash
set -euo pipefail

################################################################################
# run_specific_repos.sh — Generate and print ONBOARDING for specific repos
#
# PURPOSE:
#   - Generate ONBOARDING.md for up to 3 repos by running Gemini locally
#   - Print the generated ONBOARDING.md to stdout + log file
#   - NO VALIDATION (use validate_onboarding_list.sh for that)
#   - NO ASSERTIONS (assertions are in validate_onboarding_list.sh)
#
# USAGE:
#   ./run_specific_repos.sh repo1 [repo2] [repo3]
#
# OPTIONAL ENVIRONMENT:
#   PRINT_ONLY=1  - Skip Gemini generation; only print existing ONBOARDING.md
#   GEMINI_MODEL  - Override Gemini model (default: gemini-2.5-flash)
#
# EXAMPLE:
#   # Generate + print for 2 repos
#   ./run_specific_repos.sh searxng wagtail
#
#   # Print only (skip Gemini if already generated)
#   PRINT_ONLY=1 ./run_specific_repos.sh searxng
################################################################################

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 repo1 [repo2] [repo3]"
  exit 1
fi

if [ "$#" -gt 3 ]; then
  echo "Error: Maximum 3 repositories allowed."
  exit 1
fi

repos=("$@")
export prompt="/generate_onboarding"
orig_dir="$PWD"
LOG_FILE="evaluation_results.log"
PRINT_ONLY="${PRINT_ONLY:-0}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

{
echo " "
echo "=== Running evaluation for: ${repos[*]} ==="
echo "Logging to: ${LOG_FILE}"
[ "$PRINT_ONLY" = "1" ] && echo "MODE: PRINT_ONLY (no generation)"
echo " "

# First loop: run gemini with pushd/popd (skip if PRINT_ONLY=1)
if [ "$PRINT_ONLY" != "1" ]; then
  for repo in "${repos[@]}"; do
    echo "=== Running gemini for $repo ==="
    repo_abs_path="$HOME/$repo"
    if [ -d "$repo_abs_path" ]; then
      export REPO_ROOT="$repo_abs_path"
      pushd "$repo_abs_path" > /dev/null
      gemini -p "$prompt" -m "$GEMINI_MODEL" --yolo
      popd > /dev/null
      echo "Waiting 30 seconds for rate limits..."
      sleep 30
    else
      echo "Directory $repo_abs_path does not exist; skipping gemini for $repo"
    fi
  done
fi

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
