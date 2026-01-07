#!/usr/bin/env bash
set -euo pipefail

# Read repo list from file if no args provided
if [ "$#" -gt 0 ]; then
  repos=("$@")
else
  if [ -f "scripts/eval_repos.list" ]; then
    mapfile -t < scripts/eval_repos.list repos
  else
    echo "ERROR: No repositories provided and scripts/eval_repos.list not found."
    exit 1
  fi
fi

# Step 0: Setup target repositories (sync settings and prompts)
echo "=== Setting up evaluation repositories ==="
bash scripts/setup_evaluation_repos.sh
echo " "

export prompt="/generate_onboarding"
orig_dir="$PWD"
LOG_FILE="evaluation_results.log"
source "$orig_dir/scripts/eval_assertions.sh"

# Model configuration: default to gemini-2.5-flash but allow override via env var
MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"

{
  echo " "
  echo "=== Evaluation Started: $(date) ==="
  echo "=== Running evaluation for: ${repos[*]} ==="
  echo "=== Using Model: ${MODEL} ==="
  echo "Logging to: ${LOG_FILE}"
  echo " "

  # First loop: run gemini in each repo directory (fine)
  for repo in "${repos[@]}"; do
    echo "=== Running gemini for $repo ==="
    repo_abs_path="$HOME/$repo"

    if [ -d "$repo_abs_path" ]; then
      export REPO_ROOT="$repo_abs_path"
      pushd "$repo_abs_path" > /dev/null
      
      gemini -p "$prompt" -m "$MODEL" --yolo
      
      popd > /dev/null

      echo "Waiting 30 seconds for rate limits..."
      sleep 30
    else
      echo "Directory $repo_abs_path does not exist; skipping gemini for $repo"
    fi
  done

  # Second loop: print + validate
  validator_script="$orig_dir/scripts/validate_onboarding.py"
  validation_failures=0

  for repo in "${repos[@]}"; do
    echo " "
    echo "=== Showing ONBOARDING.md for $repo ==="

    onboarding_path="$HOME/$repo/ONBOARDING.md"
    if [ -f "$onboarding_path" ]; then
      pushd "$HOME/$repo" > /dev/null
      printf "=== Repo: %s ===\n" "$repo" | dd of=/dev/stdout 2>/dev/null
      cat ONBOARDING.md
      popd > /dev/null

      echo " "
      echo "--- Validating ONBOARDING.md for $repo ---"

      # IMPORTANT:
      # Use uv project from *this* repo (mcp-repo-onboarding), not the target repo.
      # This prevents uv from creating .venv inside $HOME/$repo.
      if ! uv run --project "$orig_dir" python "$validator_script" "$onboarding_path"; then
        echo "ERROR: Validation failed for $repo"
        validation_failures=$((validation_failures + 1))
      else
        echo "Validation passed for $repo"

        if [ "$repo" = "node-primary-min" ]; then
          if ! assert_node_primary_min "$onboarding_path"; then
            validation_failures=$((validation_failures + 1))
          else
            echo "Additional assertions passed for $repo"
          fi
        else
          echo "No additional assertions for $repo"
        fi

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