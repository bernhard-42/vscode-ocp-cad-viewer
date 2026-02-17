"""
Run build123d examples with ocp_vscode viewer

This script runs all build123d examples and displays results in the viewer.
Run with a viewer open.

Usage:
    python examples/run_build123d_examples.py [example_name_filter]
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from ocp_vscode import set_viewer_config, Camera

# build123d examples relative to this script's location
_script_dir = Path(os.path.abspath(os.path.dirname(__file__)))
_build123d_examples_dir = _script_dir / "../../build123d/examples"
_build123d_ttt_dir = _script_dir / "../../build123d/docs/assets/ttt"


def run_example(path: Path) -> bool:
    """Run a single example and return True if successful."""
    print(f"\n{'='*60}")
    print(f"Running: {path.name}")
    print('='*60)

    with tempfile.TemporaryDirectory(prefix=f"build123d_example_{path.name}") as tmpdir:
        # Use examples dir for benchy (needs assets), otherwise temp dir
        cwd = tmpdir if "benchy" not in path.name else _build123d_examples_dir

        result = subprocess.run(
            [sys.executable, str(path)],
            cwd=cwd,
            check=False,
        )

        if result.returncode != 0:
            print(f"FAILED: {path.name} (exit code {result.returncode})")
            return False

        print(f"SUCCESS: {path.name}")

        # Reset camera and wait for key press
        set_viewer_config(reset_camera=Camera.ISO, zoom=1)
        input("Press Enter to continue...")

        return True


def main():
    if not _build123d_examples_dir.exists():
        print(f"Error: build123d examples directory not found at {_build123d_examples_dir}")
        sys.exit(1)

    # Optional filter from command line
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Collect examples
    examples = []
    for examples_dir in [_build123d_examples_dir, _build123d_ttt_dir]:
        if examples_dir.exists():
            for example in sorted(examples_dir.iterdir()):
                if example.name.startswith("_") or not example.name.endswith(".py"):
                    continue
                if name_filter and name_filter.lower() not in example.name.lower():
                    continue
                examples.append(example)

    if not examples:
        print("No examples found" + (f" matching '{name_filter}'" if name_filter else ""))
        sys.exit(1)

    print(f"Found {len(examples)} example(s)")

    # Run examples
    passed = 0
    failed = 0
    failed_names = []

    for example in examples:
        try:
            if run_example(example):
                passed += 1
            else:
                failed += 1
                failed_names.append(example.name)
        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"ERROR: {example.name}: {e}")
            failed += 1
            failed_names.append(example.name)

    # Summary
    print(f"\n{'='*60}")
    print(f"Summary: {passed} passed, {failed} failed")
    if failed_names:
        print(f"Failed: {', '.join(failed_names)}")
    print('='*60)


if __name__ == "__main__":
    main()
