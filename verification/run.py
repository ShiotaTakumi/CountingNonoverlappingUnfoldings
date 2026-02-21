"""
Phase 6 (Burnside) independent verification script.

Builds and runs the C++ verification program that enumerates all
non-overlapping spanning trees and counts nonisomorphic ones via
canonical form, then compares against the pipeline result.

Usage:
    python verification/run.py <polyhedron_data_dir> [<polyhedron_data_dir> ...]

Example:
    python verification/run.py data/polyhedra/johnson/n54
    python verification/run.py data/polyhedra/johnson/n54 data/polyhedra/johnson/n55
"""

import subprocess
import sys
import os
import json


def build_verify():
    """Build the C++ verification binary if needed."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(script_dir, "build")
    binary = os.path.join(build_dir, "verify")

    if os.path.exists(binary):
        return binary

    print("Building verification binary...")
    os.makedirs(build_dir, exist_ok=True)
    subprocess.run(["cmake", ".."], cwd=build_dir, check=True)
    subprocess.run(["make"], cwd=build_dir, check=True)
    print("Build complete.")
    return binary


def find_result_json(data_dir):
    """Find the corresponding result.json for a polyhedron data directory."""
    # data/polyhedra/johnson/n54 -> output/polyhedra/johnson/n54/spanning_tree/result.json
    parts = data_dir.rstrip("/").split("/")
    try:
        idx = parts.index("data")
        output_parts = ["output"] + parts[idx + 1:]
        return os.path.join(*output_parts, "spanning_tree", "result.json")
    except ValueError:
        return None


def verify_polyhedron(binary, data_dir):
    """Run verification for a single polyhedron and check result."""
    print(f"\n{'=' * 60}")
    print(f"Verifying: {data_dir}")
    print(f"{'=' * 60}")

    result = subprocess.run(
        [binary, data_dir],
        stdout=subprocess.PIPE,
        stderr=None,  # stderr goes to terminal
        text=True,
    )

    if result.returncode != 0:
        print(f"FAIL: verification binary returned {result.returncode}")
        return False

    verified_count = result.stdout.strip()
    print(f"\nVerified nonisomorphic count: {verified_count}")

    # Compare with pipeline result
    result_json = find_result_json(data_dir)
    if result_json and os.path.exists(result_json):
        with open(result_json) as f:
            pipeline = json.load(f)
        phase6 = pipeline.get("phase6", {})
        expected = phase6.get("nonisomorphic_count")
        if expected:
            if verified_count == expected:
                print(f"PASS: matches pipeline result ({expected})")
                return True
            else:
                print(f"FAIL: expected {expected}, got {verified_count}")
                return False
        else:
            print("No Phase 6 result in pipeline output to compare.")
            return True
    else:
        print(f"No pipeline result found at {result_json}")
        print("Run the pipeline first to enable automatic comparison.")
        return True


def main():
    if len(sys.argv) < 2:
        print("Usage: python verification/run.py <polyhedron_data_dir> [...]")
        print("Example: python verification/run.py data/polyhedra/johnson/n54")
        sys.exit(1)

    binary = build_verify()
    data_dirs = sys.argv[1:]

    results = {}
    for data_dir in data_dirs:
        if not os.path.isdir(data_dir):
            print(f"Error: {data_dir} is not a directory")
            results[data_dir] = False
            continue
        results[data_dir] = verify_polyhedron(binary, data_dir)

    # Summary
    if len(data_dirs) > 1:
        print(f"\n{'=' * 60}")
        print("Summary")
        print(f"{'=' * 60}")
        for d, ok in results.items():
            status = "PASS" if ok else "FAIL"
            print(f"  {status}: {d}")

    all_pass = all(results.values())
    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    main()
