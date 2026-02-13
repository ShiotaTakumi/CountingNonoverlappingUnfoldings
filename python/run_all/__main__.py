"""
Entry point for `python -m run_all`.

Executes the full counting non-overlapping unfoldings pipeline:
    Phase 1 (edge_relabeling)
    → Phase 2 (unfolding_expansion)
    → Phase 3 (graph_export)
    → Phase 4 & 5 (spanning_tree_zdd with filtering)

Usage:
    PYTHONPATH=python python -m run_all --poly data/polyhedra/<class>/<name>

Example:
    PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n20
    PYTHONPATH=python python -m run_all --poly data/polyhedra/antiprism/a12
"""

import argparse
import subprocess
import sys
from pathlib import Path


def create_parser():
    parser = argparse.ArgumentParser(
        prog="run_all",
        description="Run the full counting pipeline: Phase 1 → 2 → 3 → 4 & 5",
    )
    parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron directory (e.g., data/polyhedra/johnson/n20)",
    )
    return parser


def run_step(label, args):
    """Run a subprocess step. Exit immediately on failure."""
    print(f"[run_all] {label}", flush=True)
    result = subprocess.run(
        [sys.executable] + args,
        cwd=None,
    )
    if result.returncode != 0:
        print(f"[run_all] FAILED at: {label} (exit code {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    parser = create_parser()
    args = parser.parse_args()
    poly_dir = args.poly

    # Convert to Path for easier manipulation
    poly_path = Path(poly_dir)
    
    # Resolve paths for each phase
    # Phase 1: polyhedron.json in RotationalUnfolding/data
    rotational_base = Path("/Users/tshiota/Github/RotationalUnfolding")
    polyhedron_json = rotational_base / "data" / "polyhedra" / poly_path.parts[-2] / poly_path.parts[-1] / "polyhedron.json"
    
    # Phase 2: exact.jsonl in RotationalUnfolding/output
    exact_jsonl = rotational_base / "output" / "polyhedra" / poly_path.parts[-2] / poly_path.parts[-1] / "exact.jsonl"
    
    # Phase 3: polyhedron_relabeled.json in CountingNonoverlappingUnfoldings/data
    polyhedron_relabeled = poly_path / "polyhedron_relabeled.json"
    
    # Phase 4 & 5: polyhedron.grh and unfoldings_edge_sets.jsonl
    polyhedron_grh = poly_path / "polyhedron.grh"
    edge_sets_jsonl = poly_path / "unfoldings_edge_sets.jsonl"

    print(f"[run_all] Pipeline start: {poly_dir}")
    print(f"[run_all] Python: {sys.executable}")
    print(f"[run_all] Polyhedron (RotationalUnfolding): {polyhedron_json}")
    print(f"[run_all] Exact unfoldings: {exact_jsonl}")
    print("")

    # Check prerequisites
    if not polyhedron_json.exists():
        print(f"[run_all] ERROR: polyhedron.json not found at {polyhedron_json}", file=sys.stderr)
        print(f"[run_all] Please ensure RotationalUnfolding data exists for this polyhedron.", file=sys.stderr)
        sys.exit(1)
    
    if not exact_jsonl.exists():
        print(f"[run_all] ERROR: exact.jsonl not found at {exact_jsonl}", file=sys.stderr)
        print(f"[run_all] Please run RotationalUnfolding pipeline first (Phase 1-3).", file=sys.stderr)
        sys.exit(1)

    # Phase 1: Edge Relabeling
    run_step(
        "Phase 1: edge_relabeling",
        ["-m", "edge_relabeling", "--poly", str(polyhedron_json)],
    )
    print("")

    # Phase 2: Unfolding Expansion
    run_step(
        "Phase 2: unfolding_expansion",
        ["-m", "unfolding_expansion", "--exact", str(exact_jsonl)],
    )
    print("")

    # Phase 3: Graph Data Conversion
    run_step(
        "Phase 3: graph_export",
        ["-m", "graph_export", "--poly", str(polyhedron_relabeled)],
    )
    print("")

    # Phase 4 & 5: Spanning Tree ZDD with Filtering
    run_step(
        "Phase 4 & 5: spanning_tree_zdd (with filtering)",
        ["-m", "spanning_tree_zdd", "--grh", str(polyhedron_grh), "--edge-sets", str(edge_sets_jsonl)],
    )
    print("")

    print(f"[run_all] All steps completed for: {poly_dir}")
    print(f"[run_all] Results: {poly_path / 'spanning_tree' / 'result.json'}")


if __name__ == "__main__":
    main()
