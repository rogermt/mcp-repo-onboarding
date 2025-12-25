#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -gt 0 ]; then

  repos=("$@")

else

  repos=(searxng Paper2Code imgix-python wagtail connexion)

fi

# Step 0: Setup target repositories (sync settings and prompts)
echo "=== Setting up evaluation repositories ==="
bash docs/evaluation/setup_evaluation_repos.sh
echo " "



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

validator_script="$orig_dir/docs/evaluation/validate_onboarding.py"
validation_failures=0

for repo in "${repos[@]}"; do

  echo " "

  echo "=== Showing ONBOARDING.md for $repo ==="

  if [ -f "$HOME/$repo/ONBOARDING.md" ]; then

    pushd "$HOME/$repo" > /dev/null

    printf "=== Repo: %s ===\n" "$repo" | dd of=/dev/stdout 2>/dev/null

    cat ONBOARDING.md

    echo " "
    echo "--- Validating ONBOARDING.md for $repo ---"
    if ! uv run python3 "$validator_script" ONBOARDING.md; then
      echo "ERROR: Validation failed for $repo"
      validation_failures=$((validation_failures + 1))
    fi

    popd > /dev/null

  else

    echo "No ONBOARDING.md in $HOME/$repo; skipping"

  fi

done

if [ "$validation_failures" -gt 0 ]; then
  echo " "
  echo "!!! CRITICAL: $validation_failures repo(s) failed validation !!!"
  exit 1
fi



echo " "

echo "=== Evaluation complete ==="

echo " "

} 2>&1 | tee "${LOG_FILE}"
