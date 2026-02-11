"""
edge_mapper.py

decompose 前後の .grh ファイルを比較し、
辺ラベルの対応表（旧 edge_id → 新 edge_id）を抽出する。
"""

from pathlib import Path
from typing import Dict, Tuple, Set


def normalize_edge(v1: int, v2: int) -> Tuple[int, int]:
    """
    辺を正規化する（無向グラフなので小さい頂点番号を先に）
    
    Args:
        v1: 頂点1
        v2: 頂点2
    
    Returns:
        (min(v1, v2), max(v1, v2)) のタプル
    """
    return (min(v1, v2), max(v1, v2))


def read_grh_edges(grh_path: Path) -> Dict[Tuple[int, int], int]:
    """
    .grh ファイルから辺を読み込み、辺 → edge_id のマッピングを作成
    
    Args:
        grh_path: .grh ファイルパス
    
    Returns:
        {(v1, v2): edge_id} の辞書（edge_id は 0-indexed）
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
    辺ラベル対応表を作成する
    
    Args:
        original_grh_path: 元の .grh ファイル（edge_id 順）
        decomposed_grh_path: decompose 後の .grh ファイル（最適化された順序）
    
    Returns:
        {旧 edge_id: 新 edge_id} の辞書
    
    Raises:
        ValueError: 辺数が一致しない、または対応する辺が見つからない場合
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
    マッピングの妥当性を検証する
    
    Args:
        mapping: {旧 edge_id: 新 edge_id} の辞書
    
    Raises:
        ValueError: マッピングが不正な場合
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
    辺ラベル対応表を JSON ファイルとして保存
    
    Args:
        mapping: {旧 edge_id: 新 edge_id} の辞書
        output_path: 出力ファイルパス
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
