import statistics
import tempfile
import time
from pathlib import Path

from mcp_repo_onboarding.analysis import analyze_repo


def create_large_repo(root: Path, file_count: int, depth: int) -> None:
    """Create a dummy repo with many files."""
    root.mkdir(parents=True, exist_ok=True)

    # Create plain files
    for i in range(file_count):
        (root / f"file_{i}.txt").write_text(f"content {i}")
        (root / f"script_{i}.py").write_text(f"print({i})")

    # Create subdirs
    if depth > 0:
        for i in range(5):  # Branch factor
            create_large_repo(root / f"dir_{i}", file_count // 5, depth - 1)


def run_benchmark() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_root = Path(temp_dir)
        print("Generating synthetic large repo...")
        # ~1000 files: 200 base + 5 * (40 base)
        # Let's try to hit ~2000 files.
        # depth 2: 5 subdirs.
        # create_large_repo(root, 100, 2)

        start_gen = time.time()
        # Generates structure
        create_large_repo(repo_root, 200, 1)  # simple depth 1
        # root: 200 files.
        # 5 subdirs, each 40 files. Total 200 + 200 = 400. Too small.

        # Adjust: linear generation for control
        for i in range(2000):
            (repo_root / f"data_{i}.txt").write_text("x" * 100)

        for i in range(500):
            (repo_root / f"src_{i}.py").write_text("import os")

        for i in range(20):
            (repo_root / f"Makefile_{i}").write_text("test:\n\techo test")

        print(f"Generation took {time.time() - start_gen:.2f}s")

        print("Running analysis benchmark...")
        times = []
        for _ in range(5):
            start = time.perf_counter()
            analyze_repo(str(repo_root))
            end = time.perf_counter()
            times.append(end - start)

        print(f"Results (5 runs): {times}")
        print(f"Mean: {statistics.mean(times):.4f}s")
        print(f"Median: {statistics.median(times):.4f}s")
        print(f"Stdev: {statistics.stdev(times):.4f}s")


if __name__ == "__main__":
    run_benchmark()
