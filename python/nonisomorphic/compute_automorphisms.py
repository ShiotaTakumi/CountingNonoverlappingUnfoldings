"""
Compute Automorphisms - Graph Automorphism Group Computation

Handles:
- Reading polyhedron.grh (Phase 3 output, 0-indexed, no header)
- Computing all graph automorphisms using networkx
- Converting vertex permutations to edge permutations
- Exporting automorphism data as JSON for C++ Phase 6

グラフ自己同型群の計算:
- polyhedron.grh（Phase 3 出力、0-indexed、ヘッダーなし）の読み込み
- networkx を用いた全グラフ自己同型の計算
- 頂点置換から辺置換への変換
- C++ Phase 6 用に自己同型データを JSON としてエクスポート

Responsibility in Phase 6:
- Computes Aut(Γ) for the polyhedron's 1-skeleton graph
- Each automorphism is expressed as an edge permutation
- Output is consumed by the C++ spanning_tree_zdd binary

Phase 6 における責務:
- 多面体の 1-skeleton グラフの Aut(Γ) を計算
- 各自己同型は辺置換として表現
- 出力は C++ の spanning_tree_zdd バイナリによって消費
"""

import json
import sys
from pathlib import Path

import networkx as nx
from networkx.algorithms import isomorphism


def load_grh(grh_path: Path) -> list:
    """
    Load .grh file (Phase 3 / tdzdd format: 0-indexed, no header).

    .grh ファイルを読み込み（Phase 3 / tdzdd 形式: 0-indexed、ヘッダーなし）。

    Args:
        grh_path (Path): Path to polyhedron.grh

    Returns:
        list: List of (v1, v2) tuples, in file order (= edge index order)
    """
    edges = []
    with open(grh_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) == 2:
                v1, v2 = int(parts[0]), int(parts[1])
                edges.append((v1, v2))
    return edges


def build_graph(edges: list) -> nx.Graph:
    """
    Build a networkx Graph from edge list.

    辺リストから networkx グラフを構築。

    Args:
        edges (list): List of (v1, v2) tuples

    Returns:
        nx.Graph: Undirected graph
    """
    G = nx.Graph()
    for v1, v2 in edges:
        G.add_edge(v1, v2)
    return G


def vertex_perm_to_edge_perm(vertex_perm: dict, edges: list) -> list:
    """
    Convert a vertex permutation to an edge permutation.

    頂点置換を辺置換に変換。

    Args:
        vertex_perm (dict): Vertex permutation {v: g(v)}
        edges (list): Edge list from .grh file (defines edge indices)

    Returns:
        list: Edge permutation as list [σ(0), σ(1), ..., σ(E-1)]
              where σ(i) is the new edge index for edge i
    """
    # Build edge lookup: normalized (min, max) vertex pair -> edge index
    # 辺の検索テーブル: 正規化された (min, max) 頂点ペア → 辺インデックス
    edge_to_idx = {}
    for idx, (u, v) in enumerate(edges):
        key = (min(u, v), max(u, v))
        edge_to_idx[key] = idx

    # For each edge, compute where it maps under the vertex permutation
    # 各辺が頂点置換でどこに写るかを計算
    edge_perm = [0] * len(edges)
    for idx, (u, v) in enumerate(edges):
        new_u = vertex_perm[u]
        new_v = vertex_perm[v]
        key = (min(new_u, new_v), max(new_u, new_v))
        if key not in edge_to_idx:
            raise ValueError(
                f"Edge ({u},{v}) maps to ({new_u},{new_v}) which doesn't exist in graph"
            )
        edge_perm[idx] = edge_to_idx[key]

    return edge_perm


def is_zero_by_theorem2(vertex_perm: dict, G: nx.Graph) -> bool:
    """
    Determine if |T_g| = 0 using Theorem 2 Cases 3 and 4 (HS13).

    HS13 の Theorem 2 Case 3/4 を用いて |T_g| = 0 かを判定。

    Case 3: Fix(g) ≠ ∅ and Fix(g) is not connected → |T_g| = 0
    Case 4: Fix(g) = ∅ and ι(g) = 0 → |T_g| = 0

    Args:
        vertex_perm (dict): Vertex permutation {v: g(v)}
        G (nx.Graph): The polyhedron graph

    Returns:
        bool: True if |T_g| = 0 is guaranteed
    """
    # Compute Fix(g): vertices fixed by g
    # Fix(g) を計算: g で固定される頂点
    fixed_vertices = {v for v in G.nodes() if vertex_perm[v] == v}

    if fixed_vertices:
        # Case 3: Fix(g) ≠ ∅ — check if Fix(g) is connected
        # Case 3: Fix(g) ≠ ∅ — Fix(g) が連結かチェック
        fix_subgraph = G.subgraph(fixed_vertices)
        if not nx.is_connected(fix_subgraph):
            return True
        return False
    else:
        # Fix(g) = ∅ — check ι(g)
        # Fix(g) = ∅ — ι(g) をチェック
        #
        # ι(g) = number of g-invariant edges
        # An edge (u,v) is g-invariant if {g(u), g(v)} = {u, v}
        # ι(g) = g-不変辺の数
        # 辺 (u,v) が g-不変 ⟺ {g(u), g(v)} = {u, v}
        iota = 0
        for u, v in G.edges():
            gu, gv = vertex_perm[u], vertex_perm[v]
            if (gu == u and gv == v) or (gu == v and gv == u):
                iota += 1

        # Case 4: ι(g) = 0 → |T_g| = 0
        if iota == 0:
            return True
        return False


def compute_all_automorphisms(G: nx.Graph) -> list:
    """
    Compute all automorphisms of graph G.

    グラフ G の全自己同型を計算。

    Args:
        G (nx.Graph): Input graph

    Returns:
        list: List of vertex permutation dicts {v: g(v)}
    """
    GM = isomorphism.GraphMatcher(G, G)
    automorphisms = []
    for mapping in GM.isomorphisms_iter():
        automorphisms.append(mapping)
    return automorphisms


def main():
    if len(sys.argv) < 3:
        print("Usage: python compute_automorphisms.py <polyhedron.grh> <output.json>")
        sys.exit(1)

    grh_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    if not grh_path.exists():
        print(f"Error: File not found: {grh_path}", file=sys.stderr)
        sys.exit(1)

    # Load graph from .grh file
    # .grh ファイルからグラフを読み込み
    edges = load_grh(grh_path)
    G = build_graph(edges)

    print(f"Graph: {G.number_of_nodes()} vertices, {G.number_of_edges()} edges",
          file=sys.stderr)

    # Compute all automorphisms (vertex permutations)
    # 全自己同型（頂点置換）を計算
    vertex_automorphisms = compute_all_automorphisms(G)
    group_order = len(vertex_automorphisms)
    print(f"Automorphism group order: {group_order}", file=sys.stderr)

    # Convert to edge permutations
    # 辺置換に変換
    edge_permutations = []
    for vperm in vertex_automorphisms:
        eperm = vertex_perm_to_edge_perm(vperm, edges)
        edge_permutations.append(eperm)

    # Verify: first should be identity
    # 検証: 最初の1つは恒等置換であるべき
    identity_found = False
    for eperm in edge_permutations:
        if eperm == list(range(len(edges))):
            identity_found = True
            break
    if not identity_found:
        print("Warning: Identity permutation not found in automorphisms",
              file=sys.stderr)

    # Output JSON
    # JSON 出力
    output = {
        "num_vertices": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
        "group_order": group_order,
        "edge_permutations": edge_permutations
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(output, f)

    print(f"Saved {group_order} automorphisms to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
