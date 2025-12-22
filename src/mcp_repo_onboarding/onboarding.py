import shutil
import time
from pathlib import Path
from .schema import WriteOnboardingResult, OnboardingDocument


def resolve_path_inside_repo(repo_root: str, sub_path: str) -> Path:
    """
    Resolves path and ensures it does not escape repo root.
    Strict security check to prevent ../ traversal.
    """
    root = Path(repo_root).resolve()
    # Join and resolve
    target = (root / sub_path).resolve()

    # Python 3.9+ method to check containment
    try:
        target.relative_to(root)
    except ValueError:
        raise ValueError(f"Path {sub_path} escapes repo root {repo_root}")

    return target


def read_onboarding(repo_root: str, path: str = "ONBOARDING.md") -> OnboardingDocument:
    try:
        target = resolve_path_inside_repo(repo_root, path)
        if not target.exists():
            return OnboardingDocument(exists=False, path=str(target))

        content = target.read_text(encoding="utf-8")
        return OnboardingDocument(
            exists=True,
            path=str(target),
            content=content,
            sizeBytes=len(content.encode("utf-8")),
        )
    except Exception:
        # Fallback for permission errors etc
        return OnboardingDocument(exists=False, path=path)


def write_onboarding(
    repo_root: str,
    content: str,
    path: str = "ONBOARDING.md",
    mode: str = "overwrite",
    create_backup: bool = True,
) -> WriteOnboardingResult:
    target = resolve_path_inside_repo(repo_root, path)
    backup_path = None

    if target.exists():
        if mode == "create":
            raise ValueError(f"File {path} already exists")

        if mode == "overwrite" and create_backup:
            timestamp = int(time.time())
            # Create backup file: ONBOARDING.md.bak.1234567890
            backup_file = target.with_name(f"{target.name}.bak.{timestamp}")
            shutil.copy2(target, backup_file)
            backup_path = str(backup_file)

    # Create parent directories if they don't exist
    target.parent.mkdir(parents=True, exist_ok=True)

    final_content = content
    if mode == "append" and target.exists():
        original = target.read_text(encoding="utf-8")
        # Ensure newline separation
        sep = "\n\n" if not original.endswith("\n") else "\n"
        final_content = original + sep + content

    target.write_text(final_content, encoding="utf-8")

    return WriteOnboardingResult(
        path=str(target),
        bytesWritten=len(final_content.encode("utf-8")),
        backupPath=backup_path,
    )
