"""
Edge Mapper - Edge Label Mapping Extraction

Handles:
- Comparison of .grh files before and after decompose
- Edge mapping extraction (old edge_id → new edge_id)
- Mapping validation and JSON export
- Does NOT modify the polyhedron data itself

辺ラベル対応表の抽出:
- decompose 前後の .grh ファイルの比較
- 辺ラベル対応表（旧 edge_id → 新 edge_id）の抽出
- マッピングの妥当性検証と JSON エクスポート
- 多面体データ自体は変更しない

Responsibility in Phase 1:
- Extracts edge mapping by matching vertex pairs between input.grh and output.grh
- Validates that the mapping is a bijection (all edge IDs are preserved)
- Exports mapping as JSON for use in Phase 2

Phase 1 における責務:
- input.grh と output.grh の頂点ペアを照合して辺ラベル対応を抽出
- マッピングが全単射であることを検証（すべての辺 ID が保存される）
- Phase 2 で使用するために対応表を JSON としてエクスポート
"""

from pathlib import Path
from typing import Dict, Tuple, Set


def normalize_edge(v1: int, v2: int) -> Tuple[int, int]:
    """
    Normalize edge representation (undirected graph: smaller vertex ID first).
    
    辺を正規化（無向グラフなので小さい頂点番号を先に）。
    
    Args:
        v1 (int): First vertex
        v2 (int): Second vertex
    
    Returns:
        tuple: (min(v1, v2), max(v1, v2))
    """
    return (min(v1, v2), max(v1, v2))


def read_grh_edges(grh_path: Path) -> Dict[Tuple[int, int], int]:
    """
    Read edges from .grh file and create edge → edge_id mapping.
    
    .grh ファイルから辺を読み込み、辺 → edge_id のマッピングを作成。
    
    Args:
        grh_path (Path): Path to .grh file
    
    Returns:
        dict: Mapping from (v1, v2) to edge_id (edge_id is 0-indexed)
    
    Note:
        Skips header lines (starting with 'p')
        Processes lines starting with 'e' as edges
    """
    edge_to_id = {}
    edge_id = 0
    
    with open(grh_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # ヘッダー行はスキップ
            if line.startswith('p '):
                continue
            
            # "e v1 v2" 形式の行を処理
            if line.startswith('e '):
                parts = line.split()
                if len(parts) == 3:
                    v1 = int(parts[1])
                    v2 = int(parts[2])
                    
                    # 自己ループはスキップ（不正なデータ）
                    if v1 == v2:
                        continue
                    
                    edge = normalize_edge(v1, v2)
                    edge_to_id[edge] = edge_id
                    edge_id += 1
    
    return edge_to_id


def create_edge_mapping(
    original_grh_path: Path,
    decomposed_grh_path: Path
) -> Dict[int, int]:
    """
    Create edge label mapping table.
    
    辺ラベル対応表を作成。
    
    Args:
        original_grh_path (Path): Original .grh file (in edge_id order)
        decomposed_grh_path (Path): Decomposed .grh file (optimized order)
    
    Returns:
        dict: Mapping from old edge_id to new edge_id
    
    Raises:
        ValueError: If edge counts don't match or corresponding edge not found
    
    Algorithm:
        Matches edges by vertex pairs (v1, v2) between input and output .grh files.
        アルゴリズム: 入出力の .grh ファイル間で頂点ペア (v1, v2) により辺を照合。
    """
    # 元の .grh を読み込む
    original_edges = read_grh_edges(original_grh_path)
    
    # decompose 後の .grh を読み込む
    decomposed_edges = read_grh_edges(decomposed_grh_path)
    
    # 辺数の確認
    if len(original_edges) != len(decomposed_edges):
        raise ValueError(
            f"辺数が一致しません: "
            f"original={len(original_edges)}, decomposed={len(decomposed_edges)}"
        )
    
    # 逆マッピングを作成（辺 → 旧 edge_id）
    edge_to_original_id = {edge: eid for edge, eid in original_edges.items()}
    
    # 辺ラベル対応表を作成
    mapping = {}
    for edge, new_edge_id in decomposed_edges.items():
        if edge not in edge_to_original_id:
            raise ValueError(
                f"decompose 後のファイルに元のファイルに存在しない辺が含まれています: {edge}"
            )
        old_edge_id = edge_to_original_id[edge]
        mapping[old_edge_id] = new_edge_id
    
    return mapping


def verify_mapping(mapping: Dict[int, int]) -> None:
    """
    Verify the validity of edge mapping (bijection check).
    
    辺ラベル対応表の妥当性を検証（全単射チェック）。
    
    Args:
        mapping (dict): Mapping from old edge_id to new edge_id
    
    Raises:
        ValueError: If mapping is not a valid bijection
    
    Verification:
    - Old edge_ids cover 0..(n-1)
    - New edge_ids cover 0..(n-1)
    - No duplicates in new edge_ids
    """
    # edge_id の範囲確認
    old_ids = set(mapping.keys())
    new_ids = set(mapping.values())
    
    num_edges = len(mapping)
    expected_ids = set(range(num_edges))
    
    if old_ids != expected_ids:
        raise ValueError(
            f"旧 edge_id が 0..{num_edges-1} の範囲を網羅していません: {old_ids}"
        )
    
    if new_ids != expected_ids:
        raise ValueError(
            f"新 edge_id が 0..{num_edges-1} の範囲を網羅していません: {new_ids}"
        )
    
    # 全単射であることを確認
    if len(new_ids) != num_edges:
        raise ValueError("新 edge_id に重複があります")


def save_edge_mapping(mapping: Dict[int, int], output_path: Path) -> None:
    """
    Save edge mapping table as JSON file.
    
    辺ラベル対応表を JSON ファイルとして保存。
    
    Args:
        mapping (dict): Mapping from old edge_id to new edge_id
        output_path (Path): Output file path
    
    Output format:
        JSON object with string keys (due to JSON spec) and integer values.
        JSON オブジェクト（JSON 仕様により文字列キー、整数値）。
    """
    import json
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(mapping, indent=2, sort_keys=True, fp=f)


if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) not in [3, 4]:
        print("Usage: python -m edge_relabeling.edge_mapper <original.grh> <decomposed.grh> [output.json]")
        sys.exit(1)
    
    original_path = Path(sys.argv[1])
    decomposed_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3]) if len(sys.argv) == 4 else None
    
    print(f"Creating edge mapping...")
    print(f"  Original:   {original_path}")
    print(f"  Decomposed: {decomposed_path}")
    if output_path:
        print(f"  Output:     {output_path}")
    
    try:
        # マッピングを作成
        mapping = create_edge_mapping(original_path, decomposed_path)
        
        # 妥当性を検証
        verify_mapping(mapping)
        
        # 統計情報を表示
        print(f"\n✓ Success!")
        print(f"  Total edges: {len(mapping)}")
        
        # マッピングの例を表示（最初の10個）
        print(f"\n  Mapping (first 10):")
        for old_id in sorted(mapping.keys())[:10]:
            new_id = mapping[old_id]
            print(f"    {old_id} → {new_id}")
        
        # JSON ファイルとして保存
        if output_path:
            save_edge_mapping(mapping, output_path)
            print(f"\n✓ Saved to {output_path}")
        else:
            # 出力先が指定されていない場合は標準出力
            print(f"\n  Full mapping (JSON):")
            print(json.dumps(mapping, indent=2, sort_keys=True))
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
