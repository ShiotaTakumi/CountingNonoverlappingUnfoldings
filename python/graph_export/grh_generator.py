"""
GRH file generator — Generate .grh files for TdZdd input

Handles:
- Converting vertex-edge graph to .grh format
- TdZdd-compatible format (no header, 0-indexed vertices)
- Preserving edge ordering from input

.grh ファイル生成 — TdZdd 入力用の .grh ファイル生成:
- 頂点-辺グラフを .grh 形式に変換
- TdZdd 互換形式（ヘッダーなし、0-indexed 頂点）
- 入力からの辺順序の保持
"""

from typing import List, Tuple
from pathlib import Path


def generate_grh_file(edges: List[Tuple[int, int]], output_path: Path) -> None:
    """
    Generate .grh file for TdZdd input.
    
    Format:
    - No header line
    - Each line: "v1 v2" (space-separated, 0-indexed vertices)
    - Edges are output in the order provided (preserves edge_id order)
    - Final newline at end of file
    
    Args:
        edges: List of (v1, v2) tuples in edge_id order
        output_path: Path to output .grh file
    
    TdZdd 入力用の .grh ファイルを生成。
    
    形式:
    - ヘッダー行なし
    - 各行: "v1 v2"（空白区切り、0-indexed 頂点）
    - 辺は提供された順序で出力（edge_id 順を保持）
    - ファイル末尾に改行
    
    引数:
        edges: edge_id 順の (v1, v2) タプルのリスト
        output_path: 出力 .grh ファイルのパス
    """
    # Ensure parent directory exists
    # 親ディレクトリの存在を確認
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for v1, v2 in edges:
            f.write(f"{v1} {v2}\n")
    
    print(f"Generated .grh file: {output_path}")
    print(f"  Edges: {len(edges)}")
