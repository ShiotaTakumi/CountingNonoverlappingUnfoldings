"""
CLI for edge set extraction

Handles:
- Command-line argument parsing
- Path resolution for input/output files
- Orchestration of edge set extraction

辺集合抽出の CLI:
- コマンドライン引数の解析
- 入出力ファイルのパス解決
- 辺集合抽出のオーケストレーション
"""

import argparse
import sys
from pathlib import Path
from typing import Dict

from .edge_set_extractor import extract_edge_sets_from_jsonl, write_edge_sets_jsonl


def resolve_edgeset_paths(unfoldings_path: str) -> Dict[str, Path]:
    """
    Resolve input and output paths from unfoldings_overlapping_all.jsonl path.
    
    Expected input path format:
        data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
    
    Output path:
        data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
    
    Args:
        unfoldings_path: Path to unfoldings_overlapping_all.jsonl
    
    Returns:
        Dict with keys: 'input_jsonl', 'output_jsonl', 'poly_class', 'poly_name'
    
    Raises:
        ValueError: If path format is invalid
    
    unfoldings_overlapping_all.jsonl のパスから入出力パスを解決。
    
    期待される入力パス形式:
        data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
    
    出力パス:
        data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
    
    引数:
        unfoldings_path: unfoldings_overlapping_all.jsonl へのパス
    
    戻り値:
        キーを持つ辞書: 'input_jsonl', 'output_jsonl', 'poly_class', 'poly_name'
    
    例外:
        ValueError: パス形式が無効な場合
    """
    input_jsonl = Path(unfoldings_path)
    
    if not input_jsonl.exists():
        raise ValueError(f"Input file not found: {input_jsonl}")
    
    if input_jsonl.name != "unfoldings_overlapping_all.jsonl":
        raise ValueError(f"Input must be unfoldings_overlapping_all.jsonl, got: {input_jsonl.name}")
    
    # Extract class and name from path
    # パスから class と name を抽出
    # Expected: data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
    parts = input_jsonl.parts
    
    try:
        # Find "polyhedra" in path
        # パス中の "polyhedra" を検索
        polyhedra_idx = parts.index("polyhedra")
        poly_class = parts[polyhedra_idx + 1]
        poly_name = parts[polyhedra_idx + 2]
    except (ValueError, IndexError):
        raise ValueError(
            f"Invalid path format. Expected: data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl\n"
            f"Got: {input_jsonl}"
        )
    
    # Output path: same directory, different filename
    # 出力パス: 同じディレクトリ、異なるファイル名
    output_jsonl = input_jsonl.parent / "unfoldings_edge_sets.jsonl"
    
    return {
        'input_jsonl': input_jsonl,
        'output_jsonl': output_jsonl,
        'poly_class': poly_class,
        'poly_name': poly_name
    }


def main_edgeset():
    """
    Main entry point for edge set extraction CLI.
    
    Extracts edge sets from unfoldings_overlapping_all.jsonl.
    
    辺集合抽出 CLI のメインエントリーポイント。
    
    unfoldings_overlapping_all.jsonl から辺集合を抽出。
    """
    parser = argparse.ArgumentParser(
        description="Extract edge sets from unfolding data / "
                    "展開図データから辺集合を抽出"
    )
    parser.add_argument(
        "--unfoldings",
        required=True,
        help="Path to unfoldings_overlapping_all.jsonl / "
             "unfoldings_overlapping_all.jsonl へのパス"
    )
    
    args = parser.parse_args()
    
    # Resolve paths
    # パスを解決
    try:
        paths = resolve_edgeset_paths(args.unfoldings)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 60)
    print("Edge Set Extraction: Block B")
    print(f"  Polyhedron: {paths['poly_class']}/{paths['poly_name']}")
    print(f"  Input:      {paths['input_jsonl']}")
    print(f"  Output:     {paths['output_jsonl']}")
    print("=" * 60)
    print()
    
    # Extract edge sets
    # 辺集合を抽出
    print("Extracting edge sets from unfoldings...")
    edge_sets = extract_edge_sets_from_jsonl(paths['input_jsonl'])
    print(f"  Extracted {len(edge_sets)} edge sets")
    print()
    
    # Write output
    # 出力を書き込み
    print("Writing edge sets to JSONL...")
    write_edge_sets_jsonl(edge_sets, paths['output_jsonl'])
    print()
    
    print("=" * 60)
    print("Edge set extraction complete!")
    print(f"  Output: {paths['output_jsonl']}")
    print("=" * 60)
    
    sys.exit(0)


if __name__ == "__main__":
    main_edgeset()
