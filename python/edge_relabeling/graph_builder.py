"""
Graph Builder - 頂点–辺グラフの構築

polyhedron.json から Union-Find を用いて頂点を再構成し、
辺と頂点の対応関係を構築する。
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Set


class UnionFind:
    """Union-Find データ構造（頂点の同一性判定用）"""
    
    def __init__(self, n: int):
        """
        Args:
            n: 要素数
        """
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """
        要素 x の代表元を取得
        
        Args:
            x: 要素
            
        Returns:
            代表元
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> None:
        """
        要素 x と y を統合
        
        Args:
            x: 要素1
            y: 要素2
        """
        root_x = self.find(x)
        root_y = self.find(y)
        
        if root_x == root_y:
            return
        
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1


def build_vertex_edge_graph(polyhedron_data: dict) -> Dict[int, Tuple[int, int]]:
    """
    polyhedron.json から頂点–辺グラフを構築
    
    Args:
        polyhedron_data: polyhedron.json の内容
        
    Returns:
        {edge_id: (vertex_i, vertex_j)} の辞書
    """
    faces = polyhedron_data["faces"]
    
    # Step 1: 各面の各辺に仮の頂点ペアを割り当て
    # 仮頂点 ID = (face_id, neighbor_index)
    edge_to_virtual_vertices: Dict[int, List[Tuple[int, int]]] = {}
    
    for face in faces:
        face_id = face["face_id"]
        neighbors = face["neighbors"]
        gon = face["gon"]
        
        for i, neighbor in enumerate(neighbors):
            edge_id = neighbor["edge_id"]
            
            # この辺は面 face_id の i 番目と (i+1) % gon 番目の頂点を結ぶ
            vertex_start = (face_id, i)
            vertex_end = (face_id, (i + 1) % gon)
            
            if edge_id not in edge_to_virtual_vertices:
                edge_to_virtual_vertices[edge_id] = []
            
            edge_to_virtual_vertices[edge_id].append((vertex_start, vertex_end))
    
    # Step 2: 仮頂点に一意な ID を割り当て
    virtual_vertex_to_id: Dict[Tuple[int, int], int] = {}
    next_id = 0
    
    for face in faces:
        face_id = face["face_id"]
        gon = face["gon"]
        for i in range(gon):
            virtual_vertex = (face_id, i)
            if virtual_vertex not in virtual_vertex_to_id:
                virtual_vertex_to_id[virtual_vertex] = next_id
                next_id += 1
    
    # Step 3: Union-Find で同じ辺を共有する頂点を統合
    uf = UnionFind(next_id)
    
    for edge_id, vertex_pairs in edge_to_virtual_vertices.items():
        if len(vertex_pairs) != 2:
            # 境界辺（1つの面にのみ属する辺）
            continue
        
        # 同じ辺を共有する2つの面
        (v1_start, v1_end) = vertex_pairs[0]
        (v2_start, v2_end) = vertex_pairs[1]
        
        v1_start_id = virtual_vertex_to_id[v1_start]
        v1_end_id = virtual_vertex_to_id[v1_end]
        v2_start_id = virtual_vertex_to_id[v2_start]
        v2_end_id = virtual_vertex_to_id[v2_end]
        
        # 辺の向きを考慮して頂点を統合
        # 面 A の辺 (u, v) と 面 B の辺 (v, u) が同じ辺を表す
        # A の終点と B の始点を統合、A の始点と B の終点を統合
        uf.union(v1_start_id, v2_end_id)
        uf.union(v1_end_id, v2_start_id)
    
    # Step 4: 各仮頂点の代表元を取得し、最終的な頂点 ID に変換
    representatives: Set[int] = set()
    for virtual_vertex_id in range(next_id):
        representatives.add(uf.find(virtual_vertex_id))
    
    # 代表元を 0, 1, 2, ... の連続した ID に変換
    rep_to_final_id: Dict[int, int] = {}
    for i, rep in enumerate(sorted(representatives)):
        rep_to_final_id[rep] = i
    
    # Step 5: 各辺について、最終的な頂点ペアを取得
    edge_to_vertices: Dict[int, Tuple[int, int]] = {}
    
    for edge_id, vertex_pairs in edge_to_virtual_vertices.items():
        if len(vertex_pairs) == 0:
            continue
        
        # 最初の面の辺情報を使用
        (v_start, v_end) = vertex_pairs[0]
        v_start_id = virtual_vertex_to_id[v_start]
        v_end_id = virtual_vertex_to_id[v_end]
        
        # Union-Find の代表元を取得
        v_start_rep = uf.find(v_start_id)
        v_end_rep = uf.find(v_end_id)
        
        # 最終的な頂点 ID に変換
        v_start_final = rep_to_final_id[v_start_rep]
        v_end_final = rep_to_final_id[v_end_rep]
        
        # 正規化（小さい方を先に）
        if v_start_final > v_end_final:
            v_start_final, v_end_final = v_end_final, v_start_final
        
        edge_to_vertices[edge_id] = (v_start_final, v_end_final)
    
    return edge_to_vertices


def load_polyhedron(polyhedron_path: Path) -> dict:
    """
    polyhedron.json を読み込む
    
    Args:
        polyhedron_path: polyhedron.json へのパス
        
    Returns:
        polyhedron データ
    """
    with open(polyhedron_path, 'r') as f:
        return json.load(f)


if __name__ == "__main__":
    # テスト用
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python graph_builder.py <polyhedron.json>")
        sys.exit(1)
    
    polyhedron_path = Path(sys.argv[1])
    polyhedron_data = load_polyhedron(polyhedron_path)
    
    edge_to_vertices = build_vertex_edge_graph(polyhedron_data)
    
    print(f"Number of edges: {len(edge_to_vertices)}")
    print(f"Number of vertices: {max(max(v) for v in edge_to_vertices.values()) + 1}")
    print("\nEdge to vertices mapping:")
    for edge_id in sorted(edge_to_vertices.keys()):
        v1, v2 = edge_to_vertices[edge_id]
        print(f"  edge {edge_id}: {v1} -- {v2}")
