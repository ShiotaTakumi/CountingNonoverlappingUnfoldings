"""
GRH Generator - .grh File Generation for TdZdd

Handles:
- Converting vertex-edge graph to TdZdd .grh format
- Writing edges in 0-indexed format without header
- Preserving edge_id ordering from Phase 1
- Does NOT modify edge ordering or vertex IDs

.grh ファイル生成 — TdZdd 用の .grh ファイル生成:
- 頂点-辺グラフを TdZdd .grh 形式に変換
- ヘッダーなしの 0-indexed 形式で辺を書き込み
- Phase 1 の edge_id 順序を保持
- 辺の順序や頂点 ID は変更しない

Responsibility in Phase 3 (Block A):
- Generates .grh file in format expected by TdZdd
- Outputs edges in edge_id ascending order
- Uses 0-indexed vertex IDs (no conversion needed)
- Creates parent directories if needed

Phase 3（Block A）における責務:
- TdZdd が期待する形式で .grh ファイルを生成
- 辺を edge_id の昇順で出力
- 0-indexed 頂点 ID を使用（変換不要）
- 必要に応じて親ディレクトリを作成
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
