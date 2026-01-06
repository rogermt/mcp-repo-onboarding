#!/usr/bin/env bash
set -euo pipefail

# Phase 10: Node-primary repo fixture (ensure it exists)
FIXTURE_DIR="evaluation_repos/node-primary-min"
if [ ! -d "$HOME/$FIXTURE_DIR" ]; then
  echo "INFO: Creating local fixture for $FIXTURE_DIR..."
  mkdir -p "$HOME/$FIXTURE_DIR"
  if [ ! -f "$HOME/$FIXTURE_DIR/package.json" ]; then
    echo "{}" > "$HOME/$FIXTURE_DIR/package.json"
  fi
  touch "$HOME/$FIXTURE_DIR/package-lock.json"
fi

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

# Configuration
orig_dir="$PWD"
LOG_FILE="validation_results.log"
source "$orig_dir/scripts/eval_assertions.sh"

# Step 0: Setup target repositories (optional, ensures settings.json is fresh if running against real repos)
# NOTE: If you are only validating generated files and want to skip setup, comment this out.
# However, for the Phase 10 fixture, we keep it.
if [ -f "scripts/setup_evaluation_repos.sh" ]; then
  echo "=== Setting up evaluation repositories ==="
  bash scripts/setup_evaluation_repos.sh
  echo " "
fi

export prompt="/generate_onboarding"

{
  echo " "
  echo "=== Validation Started: $(date) ==="
  echo "=== Validating ONBOARDING.md for: ${repos[*]} ==="
  echo "Logging to: ${LOG_FILE}"
  echo " "

  validator_script="$orig_dir/scripts/validate_onboarding.py"
  validation_failures=0

  # Loop: show + validate (no gemini, no sleep)
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
      if ! uv run --project "$orig_dir" python "$validator_script" "$onboarding_path"; then
        echo "ERROR: Validation failed for $repo"
        validation_failures=$((validation_failures + 1))
      else
        echo "Validation passed for $repo"

        # Phase 10 / #128: Node-primary specific assertions for node-primary-min
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
  echo "=== Validation complete ==="
  echo " "
} 2>&1 | tee "${LOG_FILE}"