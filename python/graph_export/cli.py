"""
CLI for graph export

Handles:
- Command-line argument parsing
- Path resolution for input/output files
- Orchestration of graph building and .grh generation

グラフエクスポートの CLI:
- コマンドライン引数の解析
- 入出力ファイルのパス解決
- グラフ構築と .grh 生成のオーケストレーション
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict

from .graph_builder import build_vertex_edge_graph
from .grh_generator import generate_grh_file


def resolve_paths(polyhedron_json_path: str) -> Dict[str, Path]:
    """
    Resolve input and output paths from polyhedron_relabeled.json path.
    
    Expected input path format:
        data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    
    Output path:
        data/polyhedra/<class>/<name>/polyhedron.grh
    
    Args:
        polyhedron_json_path: Path to polyhedron_relabeled.json
    
    Returns:
        Dict with keys: 'polyhedron_json', 'output_grh', 'poly_class', 'poly_name'
    
    Raises:
        ValueError: If path format is invalid
    
    polyhedron_relabeled.json のパスから入出力パスを解決。
    
    期待される入力パス形式:
        data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    
    出力パス:
        data/polyhedra/<class>/<name>/polyhedron.grh
    
    引数:
        polyhedron_json_path: polyhedron_relabeled.json へのパス
    
    戻り値:
        キーを持つ辞書: 'polyhedron_json', 'output_grh', 'poly_class', 'poly_name'
    
    例外:
        ValueError: パス形式が無効な場合
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
    
    # Output path: same directory, different filename
    # 出力パス: 同じディレクトリ、異なるファイル名
    output_grh = polyhedron_json.parent / "polyhedron.grh"
    
    return {
        'polyhedron_json': polyhedron_json,
        'output_grh': output_grh,
        'poly_class': poly_class,
        'poly_name': poly_name
    }


def main():
    """
    Main entry point for graph_export CLI.
    
    Generates .grh file from polyhedron_relabeled.json.
    
    graph_export CLI のメインエントリーポイント。
    
    polyhedron_relabeled.json から .grh ファイルを生成。
    """
    parser = argparse.ArgumentParser(
        description="Generate .grh file for TdZdd from polyhedron data / "
                    "多面体データから TdZdd 用 .grh ファイルを生成"
    )
    parser.add_argument(
        "--poly",
        required=True,
        help="Path to polyhedron_relabeled.json / "
             "polyhedron_relabeled.json へのパス"
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
    print("Graph Export: Generate .grh for TdZdd")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print(f"  Input:      {paths['polyhedron_json']}")
    print(f"  Output:     {paths['output_grh']}")
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
    num_vertices, edges = build_vertex_edge_graph(polyhedron_data)
    
    print(f"  Vertices: {num_vertices}")
    print(f"  Edges:    {len(edges)}")
    print()
    
    # Generate .grh file
    # .grh ファイルを生成
    print("Generating .grh file...")
    generate_grh_file(edges, paths['output_grh'])
    print()
    
    print("=" * 60)
    print("Graph export complete!")
    print(f"  Output: {paths['output_grh']}")
    print("=" * 60)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
