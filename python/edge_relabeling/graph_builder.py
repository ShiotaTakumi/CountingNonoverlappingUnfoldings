"""
Graph Builder - Vertex-Edge Graph Construction

Handles:
- Vertex reconstruction from face-adjacency data using Union-Find
- Building vertex-edge correspondence for .grh file generation
- Does NOT handle geometric information or coordinates

頂点–辺グラフの構築:
- Union-Find を用いた面隣接データからの頂点再構成
- .grh ファイル生成のための頂点–辺対応の構築
- 幾何情報や座標は扱わない

Responsibility in Phase 1:
- Reconstructs implicit vertex IDs from polyhedron.json (which only stores face-edge adjacency)
- Ensures each edge is connected to exactly two vertices
- Outputs 0-indexed vertex IDs for internal use

Phase 1 における責務:
- polyhedron.json（面と辺の隣接のみを保持）から暗黙的な頂点 ID を再構成
- 各辺が正確に 2 つの頂点に接続されることを保証
- 内部使用のための 0-indexed 頂点 ID を出力
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Set


class UnionFind:
    """
    Union-Find data structure for vertex identity determination.
    
    頂点の同一性判定のための Union-Find データ構造。
    
    Responsibility:
    - Manages disjoint sets of virtual vertices
    - Merges vertices that share the same edge
    
    責務:
    - 仮頂点の素集合を管理
    - 同じ辺を共有する頂点を統合
    """
    
    def __init__(self, n: int):
        """
        Initialize Union-Find with n elements.
        
        n 個の要素で Union-Find を初期化。
        
        Args:
            n: Number of elements (int)
        """
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """
        Find the representative of element x (with path compression).
        
        要素 x の代表元を取得（経路圧縮あり）。
        
        Args:
            x: Element to find (int)
            
        Returns:
            int: Representative element
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> None:
        """
        Merge the sets containing x and y (union by rank).
        
        要素 x と y を含む集合を統合（ランクによる統合）。
        
        Args:
            x: First element (int)
            y: Second element (int)
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
    Build vertex-edge graph from polyhedron.json using Union-Find.
    
    polyhedron.json から Union-Find を用いて頂点–辺グラフを構築。
    
    Args:
        polyhedron_data (dict): Content of polyhedron.json
    
    Returns:
        dict: Mapping from edge_id to (vertex_i, vertex_j) tuple (0-indexed)
    
    Algorithm:
    1. Assign virtual vertex pairs to each edge from face-adjacency data
    2. Assign unique IDs to all virtual vertices
    3. Merge vertices that share the same edge using Union-Find
    4. Map representatives to final vertex IDs (0-indexed)
    5. Output edge-to-vertex mapping
    
    アルゴリズム:
    1. 面隣接データから各辺に仮頂点ペアを割り当て
    2. すべての仮頂点に一意な ID を割り当て
    3. Union-Find で同じ辺を共有する頂点を統合
    4. 代表元を最終頂点 ID（0-indexed）にマッピング
    5. 辺–頂点対応を出力
    """
    faces = polyhedron_data["faces"]
    
    # Step 1: 各面の各辺に仮の頂点ペアを割り当て
    # Assign virtual vertex pairs to each edge
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
    Load polyhedron data from JSON file.
    
    JSON ファイルから多面体データを読み込む。
    
    Args:
        polyhedron_path (Path): Path to polyhedron.json
        
    Returns:
        dict: Polyhedron data
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
