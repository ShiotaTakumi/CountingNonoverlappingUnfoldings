"""
GRH Generator - .grh File Generation

Handles:
- .grh file generation for lib/decompose input
- Vertex ID conversion from 0-indexed to 1-indexed
- Does NOT modify edge ordering (preserves edge_id order)

.grh ファイルの生成:
- lib/decompose 入力用の .grh ファイル生成
- 頂点 ID を 0-indexed から 1-indexed に変換
- 辺の順序は変更しない（edge_id の順序を保持）

Responsibility in Phase 1:
- Generates .grh file in the format expected by lib/decompose
- Outputs edges in edge_id ascending order
- Converts vertex IDs to 1-indexed format

Phase 1 における責務:
- lib/decompose が期待する形式で .grh ファイルを生成
- 辺を edge_id の昇順で出力
- 頂点 ID を 1-indexed 形式に変換
"""

from pathlib import Path
from typing import Dict, Tuple


def generate_grh(
    edge_to_vertices: Dict[int, Tuple[int, int]], 
    output_path: Path
) -> None:
    """
    Generate .grh file in lib/decompose input format.
    
    lib/decompose 入力形式の .grh ファイルを生成。
    
    Args:
        edge_to_vertices (dict): Mapping from edge_id to (vertex_i, vertex_j) (0-indexed)
        output_path (Path): Output file path
    
    Output format:
        p edge <num_vertices> <num_edges>
        e <v1> <v2>  (1-indexed)
        e <v1> <v2>
        ...
    
    Note:
        Vertices are converted to 1-indexed as lib/decompose expects 1-indexed input.
        出力は 1-indexed（lib/decompose が 1-indexed を期待）。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 頂点数を計算（0-indexed なので +1）
    num_vertices = max(max(v) for v in edge_to_vertices.values()) + 1
    num_edges = len(edge_to_vertices)
    
    with open(output_path, 'w') as f:
        # ヘッダー行
        f.write(f"p edge {num_vertices} {num_edges}\n")
        
        # 辺 ID の昇順で出力（1-indexed に変換）
        for edge_id in sorted(edge_to_vertices.keys()):
            v1, v2 = edge_to_vertices[edge_id]
            f.write(f"e {v1+1} {v2+1}\n")


if __name__ == "__main__":
    # テスト用
    import sys
    import json
    from .graph_builder import load_polyhedron, build_vertex_edge_graph
    
    if len(sys.argv) < 3:
        print("Usage: python grh_generator.py <polyhedron.json> <output.grh>")
        sys.exit(1)
    
    polyhedron_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    polyhedron_data = load_polyhedron(polyhedron_path)
    edge_to_vertices = build_vertex_edge_graph(polyhedron_data)
    
    generate_grh(edge_to_vertices, output_path)
    
    print(f"Generated {output_path}")
    print(f"  Edges: {len(edge_to_vertices)}")
    print(f"  Vertices: {max(max(v) for v in edge_to_vertices.values()) + 1}")
