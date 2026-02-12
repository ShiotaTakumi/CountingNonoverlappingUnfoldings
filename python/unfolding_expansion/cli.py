"""
CLI for unfolding expansion (Phase 2: Edge relabeling and isomorphism expansion).

展開図辺ラベル貼り替えと同型展開復元の CLI（Phase 2）。

Usage:
    PYTHONPATH=python python -m unfolding_expansion --exact <path_to_exact.jsonl>

Example:
    PYTHONPATH=python python -m unfolding_expansion \
      --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl
"""

import argparse
import sys
from pathlib import Path

from .relabeler import relabel_exact_jsonl


def resolve_paths(exact_jsonl_path: Path):
    """
    Resolve input/output paths for Phase 2.
    
    Phase 2 の入出力パスを解決する。
    
    Args:
        exact_jsonl_path: Path to exact.jsonl from Rotational Unfolding
        
    Returns:
        dict: {
            "exact_jsonl": Path to input exact.jsonl,
            "edge_mapping": Path to edge_mapping.json,
            "output_jsonl": Path to output exact_relabeled.jsonl,
            "poly_class": class name,
            "poly_name": polyhedron name
        }
        
    Raises:
        ValueError: If the path does not match expected structure
    """
    # Validate input path
    # 入力パスを検証
    if not exact_jsonl_path.exists():
        raise ValueError(f"Input file not found: {exact_jsonl_path}")
    
    if exact_jsonl_path.name != "exact.jsonl":
        raise ValueError(
            f"Expected file name 'exact.jsonl', got '{exact_jsonl_path.name}'. "
            f"Please specify the path to exact.jsonl."
        )
    
    # Extract class and name from path
    # パスから class と name を抽出
    # Expected: .../output/polyhedra/<class>/<name>/exact.jsonl
    parts = exact_jsonl_path.parts
    try:
        # Find 'polyhedra' in path
        polyhedra_idx = parts.index('polyhedra')
        poly_class = parts[polyhedra_idx + 1]
        poly_name = parts[polyhedra_idx + 2]
    except (ValueError, IndexError):
        raise ValueError(
            f"Cannot extract class/name from path: {exact_jsonl_path}. "
            f"Expected structure: .../polyhedra/<class>/<name>/exact.jsonl"
        )
    
    # Counting repository root (this repo)
    # Counting リポジトリのルート（このリポジトリ）
    counting_root = Path(__file__).resolve().parent.parent.parent
    
    # Input: edge_mapping.json from Phase 1
    # 入力: Phase 1 の edge_mapping.json
    edge_mapping = counting_root / "data" / "polyhedra" / poly_class / poly_name / "edge_mapping.json"
    
    # Output: exact_relabeled.jsonl (Step 1 intermediate output)
    # 出力: exact_relabeled.jsonl（Step 1 中間出力）
    output_jsonl = counting_root / "data" / "polyhedra" / poly_class / poly_name / "exact_relabeled.jsonl"
    
    return {
        "exact_jsonl": exact_jsonl_path,
        "edge_mapping": edge_mapping,
        "output_jsonl": output_jsonl,
        "poly_class": poly_class,
        "poly_name": poly_name
    }


def main():
    """
    Main entry point for Phase 2 CLI.
    
    Phase 2 CLI のメインエントリポイント。
    """
    parser = argparse.ArgumentParser(
        prog="unfolding_expansion",
        description="Phase 2: Edge relabeling and isomorphism expansion for counting pipeline"
    )
    
    parser.add_argument(
        "--exact",
        type=Path,
        required=True,
        help="Path to exact.jsonl from Rotational Unfolding (e.g., .../output/polyhedra/johnson/n20/exact.jsonl)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    # パスを解決
    try:
        paths = resolve_paths(args.exact)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Print header
    # ヘッダーを出力
    print("=" * 60)
    print("Phase 2: Unfolding Expansion (Step 1: Edge Relabeling)")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print(f"  Input:      {paths['exact_jsonl']}")
    print("=" * 60)
    print()
    
    # Step 1: Edge relabeling
    # Step 1: 辺ラベル貼り替え
    print("[Step 1/1] Relabeling edge IDs in exact.jsonl...")
    print(f"  Mapping: {paths['edge_mapping']}")
    print(f"  Output:  {paths['output_jsonl']}")
    print()
    
    # Check edge_mapping exists
    # edge_mapping の存在を確認
    if not paths["edge_mapping"].exists():
        print(f"Error: edge_mapping.json not found: {paths['edge_mapping']}", file=sys.stderr)
        print("  → Run Phase 1 first to generate edge_mapping.json", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Execute relabeling
        # 辺ラベル貼り替えを実行
        record_count = relabel_exact_jsonl(
            paths["exact_jsonl"],
            paths["edge_mapping"],
            paths["output_jsonl"]
        )
        
        print(f"  Processed: {record_count} records")
        print(f"  Output written: {paths['output_jsonl']}")
        print()
        
        print("=" * 60)
        print("Phase 2 Step 1 Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during relabeling: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
