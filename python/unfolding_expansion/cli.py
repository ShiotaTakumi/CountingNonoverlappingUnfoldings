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
import json
from pathlib import Path

from .relabeler import relabel_exact_jsonl
from .isomorphism_expander import (
    PolyhedronData,
    expand_to_isomorphic_unfoldings
)


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
            "polyhedron_relabeled": Path to polyhedron_relabeled.json,
            "exact_relabeled": Path to intermediate exact_relabeled.jsonl,
            "output_jsonl": Path to final output unfoldings_overlapping_all.jsonl,
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
    
    data_dir = counting_root / "data" / "polyhedra" / poly_class / poly_name
    
    # Inputs
    # 入力
    edge_mapping = data_dir / "edge_mapping.json"
    polyhedron_relabeled = data_dir / "polyhedron_relabeled.json"
    
    # Intermediate output (Step 1)
    # 中間出力（Step 1）
    exact_relabeled = data_dir / "exact_relabeled.jsonl"
    
    # Final output (Phase 2 complete)
    # 最終出力（Phase 2 完了）
    output_jsonl = data_dir / "unfoldings_overlapping_all.jsonl"
    
    return {
        "exact_jsonl": exact_jsonl_path,
        "edge_mapping": edge_mapping,
        "polyhedron_relabeled": polyhedron_relabeled,
        "exact_relabeled": exact_relabeled,
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
    print("Phase 2: Unfolding Expansion")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print(f"  Input:      {paths['exact_jsonl']}")
    print("=" * 60)
    print()
    
    # ========================================
    # Step 1: Edge relabeling
    # Step 1: 辺ラベル貼り替え
    # ========================================
    print("[Step 1/2] Relabeling edge IDs in exact.jsonl...")
    print(f"  Mapping: {paths['edge_mapping']}")
    print(f"  Output:  {paths['exact_relabeled']}")
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
            paths["exact_relabeled"]
        )
        
        print(f"  Processed: {record_count} records")
        print(f"  Output written: {paths['exact_relabeled']}")
        print()
        
    except Exception as e:
        print(f"Error during edge relabeling: {e}", file=sys.stderr)
        sys.exit(1)
    
    # ========================================
    # Step 2: Isomorphism expansion
    # Step 2: 同型展開復元
    # ========================================
    print("[Step 2/2] Expanding to all isomorphic unfoldings...")
    print(f"  Polyhedron: {paths['polyhedron_relabeled']}")
    print(f"  Input:      {paths['exact_relabeled']}")
    print(f"  Output:     {paths['output_jsonl']}")
    print()
    
    # Check polyhedron_relabeled exists
    # polyhedron_relabeled の存在を確認
    if not paths["polyhedron_relabeled"].exists():
        print(f"Error: polyhedron_relabeled.json not found: {paths['polyhedron_relabeled']}", file=sys.stderr)
        print("  → Run Phase 1 first to generate polyhedron_relabeled.json", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Load polyhedron data
        # 多面体データを読み込む
        with open(paths["polyhedron_relabeled"], "r", encoding="utf-8") as f:
            polyhedron_json = json.load(f)
        
        poly = PolyhedronData.from_json(polyhedron_json)
        print(f"  Loaded polyhedron: {poly.num_faces} faces")
        
        # Process each record from exact_relabeled.jsonl
        # exact_relabeled.jsonl の各レコードを処理
        all_expanded = []
        input_record_count = 0
        
        with open(paths["exact_relabeled"], "r", encoding="utf-8") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                
                unfolding_record = json.loads(line)
                
                # Expand to all isomorphic variants
                # 全ての同型変種に展開
                expanded = expand_to_isomorphic_unfoldings(
                    unfolding_record,
                    poly,
                    line_idx
                )
                
                all_expanded.extend(expanded)
                input_record_count += 1
        
        print(f"  Input records:  {input_record_count}")
        print(f"  Expanded to:    {len(all_expanded)} unfoldings")
        print()
        
        # Write output
        # 出力を書き出す
        with open(paths["output_jsonl"], "w", encoding="utf-8") as f:
            for record in all_expanded:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        
        print(f"  Output written: {paths['output_jsonl']}")
        print()
        
        print("=" * 60)
        print("Phase 2 Complete!")
        print(f"  Final output: {paths['output_jsonl']}")
        print(f"  Total unfoldings: {len(all_expanded)}")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error during isomorphism expansion: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
