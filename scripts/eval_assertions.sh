#!/usr/bin/env bash
set -euo pipefail

# Python helper to extract section content
_extract_section_py() {
  local heading="$1"
  local file="$2"
  uv run python -c "
import sys
path = '$file'
heading = '$heading'
try:
    with open(path, 'r') as f:
        lines = f.readlines()
    in_section = False
    for line in lines:
        if line.strip() == heading:
            in_section = True
            continue
        if line.startswith('## ') and in_section:
            break
        if in_section:
            print(line, end='')
except Exception:
    pass
"
}

assert_node_primary_min() {
  local onboarding_path="$1"
  local repo="node-primary-min"

  # Extract using Python helper (robust)
  local md_content
  md_content=$(cat "$onboarding_path")

  local install_section dev_section test_section lint_section notes_section env_section
  
  env_section=$(_extract_section_py "## Environment setup" "$onboarding_path")
  install_section=$(_extract_section_py "## Install dependencies" "$onboarding_path")
  dev_section=$(_extract_section_py "## Run / develop locally" "$onboarding_path")
  test_section=$(_extract_section_py "## Run tests" "$onboarding_path")
  lint_section=$(_extract_section_py "## Lint / format" "$onboarding_path")
  notes_section=$(_extract_section_py "## Analyzer notes" "$onboarding_path")

  # 1) Must NOT show Python venv snippet
  if echo "$env_section" | grep -Eq "uv run python -m venv \.venv|python -m venv \.venv|\(Generic suggestion\)"; then
    echo "ERROR: $repo contains Python venv snippet or generic suggestion label"
    return 1
  fi

  # 2) Must include Node commands
  if ! echo "$install_section" | grep -Fq "* \`npm ci\`"; then
    echo "ERROR: $repo missing \`npm ci\` in Install dependencies"
    return 1
  fi

  if ! echo "$dev_section" | grep -Fq "* \`npm run dev\`"; then
    echo "ERROR: $repo missing \`npm run dev\` in Run / develop locally"
    return 1
  fi

  if ! echo "$test_section" | grep -Fq "* \`npm run test\`"; then
    echo "ERROR: $repo missing \`npm run test\` in Run tests"
    return 1
  fi

  if ! echo "$lint_section" | grep -Fq "* \`npm run lint\`"; then
    echo "ERROR: $repo missing \`npm run lint\` in Lint / format"
    return 1
  fi

  if ! echo "$lint_section" | grep -Fq "* \`npm run format\`"; then
    echo "ERROR: $repo missing \`npm run format\` in Lint / format"
    return 1
  fi

  # 3) Must include Primary tooling note
  if ! echo "$notes_section" | grep -Fq "* Primary tooling: Node.js"; then
    echo "ERROR: $repo missing Primary tooling note in Analyzer notes"
    return 1
  fi
}