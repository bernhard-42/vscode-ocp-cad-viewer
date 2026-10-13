"""
Run cadquery examples with ocp_vscode viewer

This script runs all cadquery examples and displays results in the viewer.
Run with a viewer open.

The cadquery examples call `show_object` without importing it (CQ-editor
provides it as a builtin), so each example is run with ocp_vscode's
`show_object` injected into its globals.

Usage:
    python examples/run_cadquery_examples.py [example_name_filter]
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from ocp_vscode import set_viewer_config, Camera

# cadquery examples relative to this script's location
_script_dir = Path(os.path.abspath(os.path.dirname(__file__)))
_cadquery_examples_dir = _script_dir / "../../cadquery/examples"

# Runs the example given as argv[1] with ocp_vscode's show_object as a global
_RUNNER = (
    "import runpy, sys\n"
    "from ocp_vscode import show_object\n"
    "runpy.run_path(sys.argv[1], init_globals={'show_object': show_object}, run_name='__main__')\n"
)


def run_example(path: Path) -> bool:
    """Run a single example and return True if successful."""
    print(f"\n{'='*60}")
    print(f"Running: {path.name}")
    print('='*60)

    with tempfile.TemporaryDirectory(prefix=f"cadquery_example_{path.name}") as tmpdir:
        # Run in a temp dir so exported files (e.g. DXF) don't land in the repo
        result = subprocess.run(
            [sys.executable, "-c", _RUNNER, str(path)],
            cwd=tmpdir,
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
    if not _cadquery_examples_dir.exists():
        print(f"Error: cadquery examples directory not found at {_cadquery_examples_dir}")
        sys.exit(1)

    # Optional filter from command line
    name_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Collect examples
    examples = []
    for example in sorted(_cadquery_examples_dir.iterdir()):
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
