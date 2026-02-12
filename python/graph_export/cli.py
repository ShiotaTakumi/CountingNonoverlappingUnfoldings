"""
CLI for Phase 3: Graph Data Conversion (Block A + Block B)

Handles:
- Block A: Generate polyhedron.grh from polyhedron structure
- Block B: Extract edge sets from unfoldings
- Orchestration of both blocks in sequence

Phase 3 の CLI: グラフデータ変換（Block A + Block B）:
- Block A: 多面体構造から polyhedron.grh を生成
- Block B: 展開図から辺集合を抽出
- 両ブロックの順次実行のオーケストレーション
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from .graph_builder import build_vertex_edge_graph_for_tdzdd
from .grh_generator import generate_grh_file
from .edge_set_extractor import extract_edge_sets_from_jsonl, write_edge_sets_jsonl


def resolve_paths(polyhedron_json_path: str) -> Dict[str, Path]:
    """
    Resolve all input and output paths for Phase 3.
    
    Expected input path format:
        data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    
    Outputs in same directory:
        - polyhedron.grh
        - unfoldings_edge_sets.jsonl
    
    Args:
        polyhedron_json_path: Path to polyhedron_relabeled.json
    
    Returns:
        Dict with keys:
        - polyhedron_json: Input polyhedron_relabeled.json
        - unfoldings_jsonl: Input unfoldings_overlapping_all.jsonl
        - output_grh: Output polyhedron.grh
        - output_edge_sets: Output unfoldings_edge_sets.jsonl
        - poly_class, poly_name
    
    Raises:
        ValueError: If path format is invalid or files not found
    
    Phase 3 の全入出力パスを解決。
    
    期待される入力パス形式:
        data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    
    同じディレクトリへの出力:
        - polyhedron.grh
        - unfoldings_edge_sets.jsonl
    
    引数:
        polyhedron_json_path: polyhedron_relabeled.json へのパス
    
    戻り値:
        以下のキーを持つ辞書:
        - polyhedron_json: 入力 polyhedron_relabeled.json
        - unfoldings_jsonl: 入力 unfoldings_overlapping_all.jsonl
        - output_grh: 出力 polyhedron.grh
        - output_edge_sets: 出力 unfoldings_edge_sets.jsonl
        - poly_class, poly_name
    
    例外:
        ValueError: パス形式が無効またはファイルが見つからない場合
    """
    polyhedron_json = Path(polyhedron_json_path)
    
    if not polyhedron_json.exists():
        raise ValueError(f"Input file not found: {polyhedron_json}")
    
    if polyhedron_json.name != "polyhedron_relabeled.json":
        raise ValueError(f"Input must be polyhedron_relabeled.json, got: {polyhedron_json.name}")
    
    # Extract class and name from path
    # パスから class と name を抽出
    # Expected: data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    parts = polyhedron_json.parts
    
    try:
        # Find "polyhedra" in path
        # パス中の "polyhedra" を検索
        polyhedra_idx = parts.index("polyhedra")
        poly_class = parts[polyhedra_idx + 1]
        poly_name = parts[polyhedra_idx + 2]
    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid path format. Expected: data/polyhedra/<class>/<name>/polyhedron_relabeled.json\n"
            f"Got: {polyhedron_json}"
        )
    
    # Resolve other paths in same directory
    # 同じディレクトリ内の他のパスを解決
    base_dir = polyhedron_json.parent
    unfoldings_jsonl = base_dir / "unfoldings_overlapping_all.jsonl"
    output_grh = base_dir / "polyhedron.grh"
    output_edge_sets = base_dir / "unfoldings_edge_sets.jsonl"
    
    # Check required input files exist
    # 必要な入力ファイルの存在確認
    if not unfoldings_jsonl.exists():
        raise ValueError(f"Required input file not found: {unfoldings_jsonl}")
    
    return {
        'polyhedron_json': polyhedron_json,
        'unfoldings_jsonl': unfoldings_jsonl,
        'output_grh': output_grh,
        'output_edge_sets': output_edge_sets,
        'poly_class': poly_class,
        'poly_name': poly_name
    }


def run_block_a(paths: Dict[str, Path]) -> None:
    """
    Run Block A: Generate polyhedron.grh
    
    Args:
        paths: Path dictionary from resolve_paths
    
    Block A を実行: polyhedron.grh を生成
    
    引数:
        paths: resolve_paths からのパス辞書
    """
    print("=" * 60)
    print("Block A: Polyhedron Graph Generation")
    print(f"  Input:  {paths['polyhedron_json']}")
    print(f"  Output: {paths['output_grh']}")
    print("=" * 60)
    print()
    
    # Load polyhedron data
    # 多面体データを読み込み
    print("Loading polyhedron data...")
    with open(paths['polyhedron_json'], 'r') as f:
        polyhedron_data = json.load(f)
    
    # Verify schema version
    # スキーマバージョンを検証
    schema_version = polyhedron_data.get("schema_version")
    if schema_version != 1:
        print(f"Warning: Expected schema_version 1, got {schema_version}", file=sys.stderr)
    
    # Build vertex-edge graph
    # 頂点-辺グラフを構築
    print("Building vertex-edge graph...")
    num_vertices, edges = build_vertex_edge_graph_for_tdzdd(polyhedron_data)
    
    print(f"  Vertices: {num_vertices}")
    print(f"  Edges:    {len(edges)}")
    print()
    
    # Generate .grh file
    # .grh ファイルを生成
    print("Generating .grh file...")
    generate_grh_file(edges, paths['output_grh'])
    print()
    
    print("Block A complete!")
    print()


def run_block_b(paths: Dict[str, Path]) -> None:
    """
    Run Block B: Extract edge sets from unfoldings
    
    Args:
        paths: Path dictionary from resolve_paths
    
    Block B を実行: 展開図から辺集合を抽出
    
    引数:
        paths: resolve_paths からのパス辞書
    """
    print("=" * 60)
    print("Block B: Edge Set Extraction")
    print(f"  Input:  {paths['unfoldings_jsonl']}")
    print(f"  Output: {paths['output_edge_sets']}")
    print("=" * 60)
    print()
    
    # Extract edge sets
    # 辺集合を抽出
    print("Extracting edge sets from unfoldings...")
    edge_sets = extract_edge_sets_from_jsonl(paths['unfoldings_jsonl'])
    print(f"  Extracted {len(edge_sets)} edge sets")
    print()
    
    # Write output
    # 出力を書き込み
    print("Writing edge sets to JSONL...")
    write_edge_sets_jsonl(edge_sets, paths['output_edge_sets'])
    print()
    
    print("Block B complete!")
    print()


def main():
    """
    Main entry point for Phase 3: Graph Data Conversion.
    
    Runs Block A and Block B in sequence.
    
    Phase 3 のメインエントリーポイント: グラフデータ変換。
    
    Block A と Block B を順次実行。
    """
    parser = argparse.ArgumentParser(
        description="Phase 3: Graph Data Conversion for ZDD input"
    )
    parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron_relabeled.json (e.g., data/polyhedra/johnson/n20/polyhedron_relabeled.json)"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    # パスを解決
    try:
        paths = resolve_paths(args.poly)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("Phase 3: Graph Data Conversion")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print("=" * 60)
    print()
    
    # Run Block A
    # Block A を実行
    try:
        run_block_a(paths)
    except Exception as e:
        print(f"Error in Block A: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run Block B
    # Block B を実行
    try:
        run_block_b(paths)
    except Exception as e:
        print(f"Error in Block B: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Summary
    # サマリー
    print("=" * 60)
    print("Phase 3 Complete!")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print(f"  Outputs:")
    print(f"    - {paths['output_grh']}")
    print(f"    - {paths['output_edge_sets']}")
    print("=" * 60)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
