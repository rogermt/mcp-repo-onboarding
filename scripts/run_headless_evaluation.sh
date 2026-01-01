#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -gt 0 ]; then
  repos=("$@")
else
  repos=(searxng Paper2Code imgix-python wagtail connexion)
fi

# Step 0: Setup target repositories (sync settings and prompts)
echo "=== Setting up evaluation repositories ==="
bash scripts/setup_evaluation_repos.sh
echo " "

export prompt="/generate_onboarding"
orig_dir="$PWD"
LOG_FILE="evaluation_results.log"

{
  echo " "
  echo "=== Evaluation Started: $(date) ==="
  echo "=== Running evaluation for: ${repos[*]} ==="
  echo "Logging to: ${LOG_FILE}"
  echo " "

  # First loop: run gemini in each repo directory (fine)
  for repo in "${repos[@]}"; do
    echo "=== Running gemini for $repo ==="
    repo_abs_path="$HOME/$repo"

    if [ -d "$repo_abs_path" ]; then
      export REPO_ROOT="$repo_abs_path"
      pushd "$repo_abs_path" > /dev/null
      gemini -p "$prompt" -m gemini-2.5-flash --yolo
      popd > /dev/null

      echo "Waiting 30 seconds for rate limits..."
      sleep 30
    else
      echo "Directory $repo_abs_path does not exist; skipping gemini for $repo"
    fi
  done

  # Second loop: show + validate without letting uv treat target repos as projects
  validator_script="$orig_dir/scripts/validate_onboarding.py"
  validation_failures=0

  for repo in "${repos[@]}"; do
    echo " "
    echo "=== Showing ONBOARDING.md for $repo ==="

    onboarding_path="$HOME/$repo/ONBOARDING.md"
    if [ -f "$onboarding_path" ]; then
      printf "=== Repo: %s ===\n" "$repo" | dd of=/dev/stdout 2>/dev/null
      cat "$onboarding_path"

      echo " "
      echo "--- Validating ONBOARDING.md for $repo ---"

      # IMPORTANT:
      # Use uv project from *this* repo (mcp-repo-onboarding), not the target repo.
      # This prevents uv from creating .venv inside $HOME/$repo.
      if ! uv run --project "$orig_dir" python "$validator_script" "$onboarding_path"; then
        echo "ERROR: Validation failed for $repo"
        validation_failures=$((validation_failures + 1))
      fi
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
