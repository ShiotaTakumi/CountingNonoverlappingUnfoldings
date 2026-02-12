"""
Edge relabeling for exact.jsonl records.

exact.jsonl のレコードに対する辺ラベル貼り替え処理。

This module implements Step 2 of Phase 2:
- Reads exact.jsonl from Rotational Unfolding
- Applies edge_mapping.json to update edge_id fields
- Removes geometric information (x, y, angle_deg)
- Removes search control information (base_pair, symmetric_used)
- Preserves combinatorial structure (face_id, gon, edge_id)

Phase 2 の Step 2 を実装：
- Rotational Unfolding の exact.jsonl を読み込み
- edge_mapping.json を適用して edge_id を更新
- 幾何情報（x, y, angle_deg）を削除
- 探索制御情報（base_pair, symmetric_used）を削除
- 組合せ構造（face_id, gon, edge_id）を保持
"""

import json
from pathlib import Path
from typing import Dict, Any, List


def load_edge_mapping(edge_mapping_path: Path) -> Dict[int, int]:
    """
    Load edge mapping from JSON file.
    
    JSON ファイルから辺ラベル対応表を読み込む。
    
    Args:
        edge_mapping_path: Path to edge_mapping.json
        
    Returns:
        dict: {old_edge_id (int): new_edge_id (int)}
        
    Note:
        JSON keys are strings, so we convert them to integers.
        JSON のキーは文字列なので、整数に変換する。
    """
    with open(edge_mapping_path, 'r', encoding='utf-8') as f:
        mapping_str = json.load(f)
    
    # Convert string keys to integers
    # 文字列キーを整数に変換
    mapping = {int(k): v for k, v in mapping_str.items()}
    
    return mapping


def relabel_record(record: Dict[str, Any], edge_mapping: Dict[int, int]) -> Dict[str, Any]:
    """
    Apply edge relabeling to a single exact.jsonl record.
    
    exact.jsonl の 1 レコードに辺ラベル貼り替えを適用する。
    
    Args:
        record: Original record from exact.jsonl (schema_version: 1)
        edge_mapping: {old_edge_id: new_edge_id}
        
    Returns:
        dict: Relabeled record with:
            - Updated edge_id fields (new label system)
            - Geometric info removed (x, y, angle_deg)
            - Search info removed (base_pair, symmetric_used)
            - Combinatorial structure preserved (face_id, gon, edge_id)
            
    Raises:
        KeyError: If an edge_id is not found in edge_mapping
    """
    # Create new record with only essential fields
    # 必須フィールドのみを持つ新しいレコードを作成
    relabeled = {
        "faces": [],
        "exact_overlap": record["exact_overlap"]
    }
    
    # Process each face: update edge_id, remove geometric info
    # 各面を処理: edge_id を更新、幾何情報を削除
    for face in record["faces"]:
        old_edge_id = face["edge_id"]
        
        # Check if edge_id exists in mapping
        # edge_id がマッピングに存在するか確認
        if old_edge_id not in edge_mapping:
            raise KeyError(
                f"Edge ID {old_edge_id} not found in edge_mapping. "
                f"This may indicate a mismatch between Phase 1 and Rotational Unfolding data."
            )
        
        new_edge_id = edge_mapping[old_edge_id]
        
        # Keep only combinatorial structure
        # 組合せ構造のみを保持
        relabeled_face = {
            "face_id": face["face_id"],
            "gon": face["gon"],
            "edge_id": new_edge_id
        }
        
        relabeled["faces"].append(relabeled_face)
    
    return relabeled


def relabel_exact_jsonl(
    exact_jsonl_path: Path,
    edge_mapping_path: Path,
    output_path: Path
) -> int:
    """
    Relabel all records in exact.jsonl and write to output.
    
    exact.jsonl の全レコードに辺ラベル貼り替えを行い、出力する。
    
    Args:
        exact_jsonl_path: Path to input exact.jsonl (Rotational Unfolding output)
        edge_mapping_path: Path to edge_mapping.json (Phase 1 output)
        output_path: Path to output file (exact_relabeled.jsonl)
        
    Returns:
        int: Number of records processed
        
    Processing:
        - Reads exact.jsonl line by line (JSONL format)
        - Applies edge relabeling to each record
        - Removes geometric and search control information
        - Writes to output as JSONL
        
    処理:
        - exact.jsonl を 1 行ずつ読み込み（JSONL 形式）
        - 各レコードに辺ラベル貼り替えを適用
        - 幾何情報と探索制御情報を削除
        - JSONL として出力に書き出し
    """
    # Load edge mapping
    # 辺ラベル対応表を読み込み
    edge_mapping = load_edge_mapping(edge_mapping_path)
    
    # Ensure output directory exists
    # 出力ディレクトリが存在することを確認
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    record_count = 0
    
    with open(exact_jsonl_path, 'r', encoding='utf-8') as fin, \
         open(output_path, 'w', encoding='utf-8') as fout:
        
        for line_num, line in enumerate(fin, start=1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse JSON record
                # JSON レコードを解析
                record = json.loads(line)
                
                # Verify schema version
                # スキーマバージョンを検証
                if record.get("schema_version") != 1:
                    raise ValueError(
                        f"Line {line_num}: Unsupported schema_version: {record.get('schema_version')}. "
                        f"Expected schema_version: 1"
                    )
                
                # Apply relabeling
                # 辺ラベル貼り替えを適用
                relabeled_record = relabel_record(record, edge_mapping)
                
                # Write to output (compact JSON, one per line)
                # 出力に書き出し（コンパクト JSON、1 行 1 レコード）
                fout.write(json.dumps(relabeled_record, ensure_ascii=False) + '\n')
                
                record_count += 1
                
            except json.JSONDecodeError as e:
                raise ValueError(f"Line {line_num}: JSON parse error: {e}")
            except KeyError as e:
                raise ValueError(f"Line {line_num}: {e}")
    
    return record_count
