"""
Graph builder — Extract graph structure from polyhedron data

Handles:
- Edge-face adjacency extraction from polyhedron_relabeled.json
- Vertex reconstruction using Union-Find algorithm
- Building vertex-edge graph representation

グラフ構築 — 多面体データからグラフ構造を抽出:
- polyhedron_relabeled.json からの辺-面隣接情報抽出
- Union-Find アルゴリズムによる頂点再構成
- 頂点-辺グラフ表現の構築
"""

from typing import Dict, List, Tuple, Any, Set


class UnionFind:
    """
    Union-Find data structure for vertex reconstruction.
    
    Vertices are identified by tracking which edges share common vertices.
    Two edges share a vertex if they are adjacent on the same face.
    
    頂点再構成のための Union-Find データ構造。
    
    どの辺が共通の頂点を持つかを追跡することで頂点を識別します。
    2つの辺が同じ面上で隣接している場合、それらは頂点を共有します。
    """
    
    def __init__(self, n: int):
        """Initialize Union-Find with n elements (edges).
        
        n 要素（辺）で Union-Find を初期化。
        """
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        """Find root of x with path compression.
        
        経路圧縮を用いて x のルートを検索。
        """
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> None:
        """Union sets containing x and y by rank.
        
        x と y を含む集合をランクによって統合。
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


def build_vertex_edge_graph(polyhedron_data: Dict[str, Any]) -> Tuple[int, List[Tuple[int, int]]]:
    """
    Build vertex-edge graph from polyhedron data using Union-Find.
    
    Algorithm (from Phase 1):
    1. Assign virtual vertex pairs to each edge from face-adjacency data
    2. Assign unique IDs to all virtual vertices (face_id, index)
    3. Merge vertices that share the same edge using Union-Find
    4. Map representatives to final vertex IDs (0-indexed)
    5. Output edge list in edge_id order
    
    Args:
        polyhedron_data: Loaded polyhedron_relabeled.json data
    
    Returns:
        Tuple of (num_vertices, edges) where:
        - num_vertices: Total number of vertices
        - edges: List of (v1, v2) tuples in edge_id order (0-indexed vertices)
    
    Union-Find を用いて多面体データから頂点-辺グラフを構築。
    
    アルゴリズム（Phase 1 より）:
    1. 面隣接データから各辺に仮頂点ペアを割り当て
    2. すべての仮頂点（face_id, index）に一意な ID を割り当て
    3. Union-Find で同じ辺を共有する頂点を統合
    4. 代表元を最終頂点 ID（0-indexed）にマッピング
    5. edge_id 順に辺リストを出力
    
    引数:
        polyhedron_data: 読み込んだ polyhedron_relabeled.json データ
    
    戻り値:
        (num_vertices, edges) のタプル:
        - num_vertices: 頂点の総数
        - edges: edge_id 順の (v1, v2) タプルのリスト（0-indexed 頂点）
    """
    faces = polyhedron_data["faces"]
    
    # Step 1: Assign virtual vertex pairs to each edge
    # 各辺に仮頂点ペアを割り当て
    # Virtual vertex ID = (face_id, neighbor_index)
    edge_to_virtual_vertices: Dict[int, List[Tuple[Tuple[int, int], Tuple[int, int]]]] = {}
    
    for face in faces:
        face_id = face["face_id"]
        neighbors = face["neighbors"]
        gon = face["gon"]
        
        for i, neighbor in enumerate(neighbors):
            edge_id = neighbor["edge_id"]
            
            # This edge connects vertex i and (i+1) % gon of face face_id
            # この辺は面 face_id の i 番目と (i+1) % gon 番目の頂点を結ぶ
            vertex_start = (face_id, i)
            vertex_end = (face_id, (i + 1) % gon)
            
            if edge_id not in edge_to_virtual_vertices:
                edge_to_virtual_vertices[edge_id] = []
            
            edge_to_virtual_vertices[edge_id].append((vertex_start, vertex_end))
    
    # Step 2: Assign unique IDs to all virtual vertices
    # すべての仮頂点に一意な ID を割り当て
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
    
    # Step 3: Merge vertices that share the same edge using Union-Find
    # Union-Find で同じ辺を共有する頂点を統合
    uf = UnionFind(next_id)
    
    for edge_id, vertex_pairs in edge_to_virtual_vertices.items():
        if len(vertex_pairs) != 2:
            # Boundary edge (belongs to only one face)
            # 境界辺（1つの面にのみ属する辺）
            continue
        
        # Two faces sharing the same edge
        # 同じ辺を共有する2つの面
        (v1_start, v1_end) = vertex_pairs[0]
        (v2_start, v2_end) = vertex_pairs[1]
        
        v1_start_id = virtual_vertex_to_id[v1_start]
        v1_end_id = virtual_vertex_to_id[v1_end]
        v2_start_id = virtual_vertex_to_id[v2_start]
        v2_end_id = virtual_vertex_to_id[v2_end]
        
        # Consider edge orientation: edge (u, v) in face A and edge (v, u) in face B represent the same edge
        # A's end connects to B's start, A's start connects to B's end
        # 辺の向きを考慮: 面 A の辺 (u, v) と面 B の辺 (v, u) が同じ辺を表す
        # A の終点と B の始点を統合、A の始点と B の終点を統合
        uf.union(v1_start_id, v2_end_id)
        uf.union(v1_end_id, v2_start_id)
    
    # Step 4: Get representatives and map to final vertex IDs
    # 各仮頂点の代表元を取得し、最終的な頂点 ID に変換
    from typing import Set
    representatives: Set[int] = set()
    for virtual_vertex_id in range(next_id):
        representatives.add(uf.find(virtual_vertex_id))
    
    # Map representatives to consecutive IDs 0, 1, 2, ...
    # 代表元を 0, 1, 2, ... の連続した ID に変換
    rep_to_final_id: Dict[int, int] = {}
    for i, rep in enumerate(sorted(representatives)):
        rep_to_final_id[rep] = i
    
    # Step 5: Build edge list in edge_id order
    # edge_id 順に辺リストを構築
    edges: List[Tuple[int, int]] = []
    num_edges = max(edge_to_virtual_vertices.keys()) + 1 if edge_to_virtual_vertices else 0
    
    for edge_id in range(num_edges):
        if edge_id not in edge_to_virtual_vertices or len(edge_to_virtual_vertices[edge_id]) == 0:
            # Edge not found (should not happen in valid data)
            # 辺が見つからない（有効なデータでは発生しないはず）
            edges.append((0, 0))
            continue
        
        # Use the first face's edge information
        # 最初の面の辺情報を使用
        (v_start, v_end) = edge_to_virtual_vertices[edge_id][0]
        v_start_id = virtual_vertex_to_id[v_start]
        v_end_id = virtual_vertex_to_id[v_end]
        
        # Get Union-Find representatives
        # Union-Find の代表元を取得
        v_start_rep = uf.find(v_start_id)
        v_end_rep = uf.find(v_end_id)
        
        # Convert to final vertex IDs
        # 最終的な頂点 ID に変換
        v_start_final = rep_to_final_id[v_start_rep]
        v_end_final = rep_to_final_id[v_end_rep]
        
        # Normalize (smaller vertex first)
        # 正規化（小さい方を先に）
        if v_start_final > v_end_final:
            v_start_final, v_end_final = v_end_final, v_start_final
        
        edges.append((v_start_final, v_end_final))
    
    num_vertices = len(representatives)
    return num_vertices, edges
