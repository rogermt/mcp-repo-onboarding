#!/usr/bin/env python3
import re
from pathlib import Path


def summarize_log(log_path: str = "evaluation_results.log") -> None:
    path = Path(log_path)
    if not path.exists():
        print(f"Log file not found: {log_path}")
        return

    content = path.read_text(encoding="utf-8")

    # Simple regex to find repo results and validation status
    # Matches: "=== Repo: [name] ===" and "Validation passed/failed"
    repo_sections = re.split(r"=== Repo: (.*?) ===", content)

    results = []
    if len(repo_sections) > 1:
        for i in range(1, len(repo_sections), 2):
            repo_name = repo_sections[i].strip()
            section_content = repo_sections[i + 1]

            status = "❓ Unknown"
            if "Validation passed" in section_content:
                status = "✅ PASS"
            elif "Validation failed" in section_content:
                status = "❌ FAIL"

            results.append((repo_name, status))

    if not results:
        print("No evaluation results found in log.")
        return

    print("## Evaluation Summary")
    print("| Repository | Status |")
    print("|------------|--------|")
    for repo, status in results:
        print(f"| {repo} | {status} |")

    print("\n> *Summary generated from evaluation_results.log*")


if __name__ == "__main__":
    summarize_log()
