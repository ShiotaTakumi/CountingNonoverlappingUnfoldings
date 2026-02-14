"""
Entry point for `python -m preprocess`.

Executes the preprocessing pipeline (Phase 1-3):
    Phase 1 (edge_relabeling)
    → Phase 2 (unfolding_expansion)
    → Phase 3 (graph_export)

前処理パイプライン（Phase 1-3）を実行します:
    Phase 1（辺ラベル貼り替え）
    → Phase 2（展開図展開）
    → Phase 3（グラフデータ変換）

Usage:
    PYTHONPATH=python python -m preprocess --poly data/polyhedra/<class>/<name>

Example:
    PYTHONPATH=python python -m preprocess --poly data/polyhedra/johnson/n20
    PYTHONPATH=python python -m preprocess --poly data/polyhedra/antiprism/a12
"""

import argparse
import subprocess
import sys
from pathlib import Path


def create_parser():
    parser = argparse.ArgumentParser(
        prog="preprocess",
        description="Run the preprocessing pipeline: Phase 1 → 2 → 3",
    )
    parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron directory (e.g., data/polyhedra/johnson/n20)",
    )
    return parser


def run_step(label, args):
    """
    Run a subprocess step. Exit immediately on failure.

    サブプロセスステップを実行。失敗時は即座に終了。
    """
    print(f"[preprocess] {label}", flush=True)
    result = subprocess.run(
        [sys.executable] + args,
        cwd=None,
    )
    if result.returncode != 0:
        print(f"[preprocess] FAILED at: {label} (exit code {result.returncode})", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    parser = create_parser()
    args = parser.parse_args()
    poly_dir = args.poly

    # Convert to Path for easier manipulation
    # パス操作を容易にするために Path に変換
    poly_path = Path(poly_dir)

    # Resolve paths for each phase
    # 各フェーズのパスを解決
    # Phase 1: polyhedron.json in RotationalUnfolding/data
    rotational_base = Path("/Users/tshiota/Github/RotationalUnfolding")
    polyhedron_json = rotational_base / "data" / "polyhedra" / poly_path.parts[-2] / poly_path.parts[-1] / "polyhedron.json"

    # Phase 2: exact.jsonl in RotationalUnfolding/output
    exact_jsonl = rotational_base / "output" / "polyhedra" / poly_path.parts[-2] / poly_path.parts[-1] / "exact.jsonl"

    # Phase 3: polyhedron_relabeled.json in CountingNonoverlappingUnfoldings/data
    polyhedron_relabeled = poly_path / "polyhedron_relabeled.json"

    print(f"[preprocess] Pipeline start: {poly_dir}")
    print(f"[preprocess] Python: {sys.executable}")
    print(f"[preprocess] Polyhedron (RotationalUnfolding): {polyhedron_json}")
    print(f"[preprocess] Exact unfoldings: {exact_jsonl}")
    print("")

    # Check prerequisites / 前提条件チェック
    if not polyhedron_json.exists():
        print(f"[preprocess] ERROR: polyhedron.json not found at {polyhedron_json}", file=sys.stderr)
        print(f"[preprocess] Please ensure RotationalUnfolding data exists for this polyhedron.", file=sys.stderr)
        sys.exit(1)

    if not exact_jsonl.exists():
        print(f"[preprocess] ERROR: exact.jsonl not found at {exact_jsonl}", file=sys.stderr)
        print(f"[preprocess] Please run RotationalUnfolding pipeline first (Phase 1-3).", file=sys.stderr)
        sys.exit(1)

    # Phase 1: Edge Relabeling / 辺ラベル貼り替え
    run_step(
        "Phase 1: edge_relabeling",
        ["-m", "edge_relabeling", "--poly", str(polyhedron_json)],
    )
    print("")

    # Phase 2: Unfolding Expansion / 展開図展開
    run_step(
        "Phase 2: unfolding_expansion",
        ["-m", "unfolding_expansion", "--exact", str(exact_jsonl)],
    )
    print("")

    # Phase 3: Graph Data Conversion / グラフデータ変換
    run_step(
        "Phase 3: graph_export",
        ["-m", "graph_export", "--poly", str(polyhedron_relabeled)],
    )
    print("")

    print(f"[preprocess] All preprocessing steps completed for: {poly_dir}")
    print(f"[preprocess] Phase 4-6 can now be run with:")
    print(f"  PYTHONPATH=python python -m counting --poly {poly_dir} [--no-overlap] [--noniso]")


if __name__ == "__main__":
    main()
