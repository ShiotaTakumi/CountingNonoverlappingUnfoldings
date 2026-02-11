"""
GRH Generator - .grh ファイルの生成

頂点–辺グラフから .grh ファイルを生成する。
Research2024/GraphData と同じ形式を出力。
"""

from pathlib import Path
from typing import Dict, Tuple


def generate_grh(
    edge_to_vertices: Dict[int, Tuple[int, int]], 
    output_path: Path
) -> None:
    """
    .grh ファイルを生成（decompose 入力形式）
    
    Args:
        edge_to_vertices: {edge_id: (vertex_i, vertex_j)} の辞書（0-indexed）
        output_path: 出力ファイルパス
    
    Note:
        出力は 1-indexed（lib/decompose が 1-indexed を期待しているため）
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
