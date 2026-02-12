"""
Edge set extractor — Extract edge sets from unfolding data

Handles:
- Reading unfoldings_overlapping_all.jsonl
- Collecting edge_id from face sequences
- Removing duplicates and sorting
- Does NOT handle geometric or overlap information

辺集合抽出器 — 展開図データからの辺集合抽出:
- unfoldings_overlapping_all.jsonl の読み込み
- 面列からの edge_id 収集
- 重複除去とソート
- 幾何情報や重なり情報は扱わない
"""

import json
from typing import List, Set, Dict, Any
from pathlib import Path


def extract_edge_set_from_unfolding(unfolding_record: Dict[str, Any]) -> List[int]:
    """
    Extract edge set from a single unfolding record.
    
    Collects all edge_id values from the faces array (except the first face,
    which has no edge_id as it's the root of the spanning tree).
    
    Args:
        unfolding_record: Single unfolding record from unfoldings_overlapping_all.jsonl
    
    Returns:
        Sorted list of unique edge_id values
    
    単一の展開図レコードから辺集合を抽出。
    
    faces 配列から全ての edge_id 値を収集します（最初の面を除く。
    最初の面は全域木の根なので edge_id を持ちません）。
    
    引数:
        unfolding_record: unfoldings_overlapping_all.jsonl からの単一展開図レコード
    
    戻り値:
        一意な edge_id 値のソート済みリスト
    """
    edge_set: Set[int] = set()
    
    faces = unfolding_record.get("faces", [])
    
    for face in faces:
        # First face has no edge_id (root of spanning tree)
        # 最初の面は edge_id を持たない（全域木の根）
        if "edge_id" in face:
            edge_set.add(face["edge_id"])
    
    # Return sorted list for consistency
    # 一貫性のためソート済みリストを返す
    return sorted(edge_set)


def extract_edge_sets_from_jsonl(input_path: Path) -> List[Dict[str, Any]]:
    """
    Extract edge sets from all unfoldings in unfoldings_overlapping_all.jsonl.
    
    Args:
        input_path: Path to unfoldings_overlapping_all.jsonl
    
    Returns:
        List of records, each containing:
        - edges: sorted list of edge_id values
    
    unfoldings_overlapping_all.jsonl の全展開図から辺集合を抽出。
    
    引数:
        input_path: unfoldings_overlapping_all.jsonl へのパス
    
    戻り値:
        レコードのリスト、各レコードは以下を含む:
        - edges: edge_id 値のソート済みリスト
    """
    edge_sets: List[Dict[str, Any]] = []
    
    with open(input_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                unfolding_record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line {line_num}: {e}")
                continue
            
            # Extract edge set
            # 辺集合を抽出
            edges = extract_edge_set_from_unfolding(unfolding_record)
            
            # Create output record
            # 出力レコードを作成
            edge_set_record = {
                "edges": edges
            }
            
            edge_sets.append(edge_set_record)
    
    return edge_sets


def write_edge_sets_jsonl(edge_sets: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Write edge sets to JSONL file.
    
    Args:
        edge_sets: List of edge set records
        output_path: Path to output unfoldings_edge_sets.jsonl
    
    辺集合を JSONL ファイルに書き込み。
    
    引数:
        edge_sets: 辺集合レコードのリスト
        output_path: 出力 unfoldings_edge_sets.jsonl へのパス
    """
    # Ensure parent directory exists
    # 親ディレクトリの存在を確認
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        for record in edge_sets:
            json.dump(record, f)
            f.write('\n')
    
    print(f"Generated edge sets file: {output_path}")
    print(f"  Total unfoldings: {len(edge_sets)}")
    if edge_sets:
        edge_counts = [len(record["edges"]) for record in edge_sets]
        print(f"  Edge count range: {min(edge_counts)} - {max(edge_counts)}")
