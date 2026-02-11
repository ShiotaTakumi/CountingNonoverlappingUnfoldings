"""
Relabeler - Polyhedron Edge Relabeling

Handles:
- Edge label replacement in polyhedron.json according to edge_mapping
- Generation of polyhedron_relabeled.json with new edge labels
- Validation of relabeling correctness
- Does NOT modify face structure or topology

辺ラベル貼り替えモジュール:
- edge_mapping に従って polyhedron.json の辺ラベルを置換
- 新しい辺ラベル体系の polyhedron_relabeled.json を生成
- 貼り替えの正しさを検証
- 面構造やトポロジーは変更しない

Responsibility in Phase 1:
- Applies edge mapping to all neighbors[].edge_id in polyhedron.json
- Preserves all other fields (face_id, gon, neighbor face_ids)
- Outputs polyhedron_relabeled.json for use in Phase 2 and beyond

Phase 1 における責務:
- polyhedron.json のすべての neighbors[].edge_id に辺ラベル対応を適用
- 他のすべてのフィールド（face_id, gon, 隣接面 ID）を保持
- Phase 2 以降で使用する polyhedron_relabeled.json を出力
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_polyhedron(polyhedron_path: Path) -> Dict[str, Any]:
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


def load_edge_mapping(mapping_path: Path) -> Dict[int, int]:
    """
    Load edge mapping from JSON file.
    
    JSON ファイルから辺ラベル対応表を読み込む。
    
    Args:
        mapping_path (Path): Path to edge_mapping.json
    
    Returns:
        dict: Mapping from old edge_id to new edge_id
    
    Note:
        JSON keys are strings, so they are converted to integers.
        JSON のキーは文字列なので整数に変換。
    """
    with open(mapping_path, 'r') as f:
        mapping_str = json.load(f)
        # JSON のキーは文字列なので整数に変換
        return {int(k): int(v) for k, v in mapping_str.items()}


def relabel_polyhedron(
    polyhedron: Dict[str, Any],
    edge_mapping: Dict[int, int]
) -> Dict[str, Any]:
    """
    Relabel edges in polyhedron according to edge mapping.
    
    edge_mapping に従って polyhedron の辺ラベルを貼り替える。
    
    Args:
        polyhedron (dict): Original polyhedron data
        edge_mapping (dict): Mapping from old edge_id to new edge_id
    
    Returns:
        dict: Polyhedron data with relabeled edges
    
    Raises:
        ValueError: If an edge_id not in mapping is found
    
    Note:
        Creates a deep copy to avoid modifying the original data.
        元データを変更しないために深いコピーを作成。
    """
    # 深いコピーを作成（元データを変更しない）
    import copy
    relabeled = copy.deepcopy(polyhedron)
    
    # 各面の辺ラベルを貼り替える
    for face in relabeled["faces"]:
        for neighbor in face["neighbors"]:
            old_edge_id = neighbor["edge_id"]
            
            if old_edge_id not in edge_mapping:
                raise ValueError(
                    f"edge_id {old_edge_id} がマッピングに存在しません "
                    f"(face_id={face['face_id']})"
                )
            
            # 新しい edge_id に置き換える
            neighbor["edge_id"] = edge_mapping[old_edge_id]
    
    return relabeled


def save_polyhedron(polyhedron: Dict[str, Any], output_path: Path) -> None:
    """
    Save polyhedron data as JSON file.
    
    polyhedron データを JSON ファイルとして保存。
    
    Args:
        polyhedron (dict): Polyhedron data
        output_path (Path): Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(polyhedron, f, indent=2)


def verify_relabeling(
    original: Dict[str, Any],
    relabeled: Dict[str, Any],
    edge_mapping: Dict[int, int]
) -> None:
    """
    Verify the correctness of edge relabeling.
    
    辺ラベル貼り替えの妥当性を検証。
    
    Args:
        original (dict): Original polyhedron data
        relabeled (dict): Relabeled polyhedron data
        edge_mapping (dict): Edge mapping used
    
    Raises:
        ValueError: If verification fails
    
    Verification checks:
    - Face count matches
    - face_id and gon unchanged
    - neighbor count unchanged
    - neighbor face_ids unchanged
    - edge_ids correctly mapped
    """
    # 面数が一致することを確認
    if len(original["faces"]) != len(relabeled["faces"]):
        raise ValueError("面数が一致しません")
    
    # 各面を検証
    for orig_face, relabeled_face in zip(original["faces"], relabeled["faces"]):
        # face_id が変わっていないことを確認
        if orig_face["face_id"] != relabeled_face["face_id"]:
            raise ValueError(
                f"face_id が変更されています: {orig_face['face_id']} → {relabeled_face['face_id']}"
            )
        
        # gon が変わっていないことを確認
        if orig_face["gon"] != relabeled_face["gon"]:
            raise ValueError(
                f"face_id={orig_face['face_id']}: gon が変更されています"
            )
        
        # neighbors の数が変わっていないことを確認
        if len(orig_face["neighbors"]) != len(relabeled_face["neighbors"]):
            raise ValueError(
                f"face_id={orig_face['face_id']}: neighbors の数が変更されています"
            )
        
        # 各 neighbor を検証
        for orig_neighbor, relabeled_neighbor in zip(
            orig_face["neighbors"], relabeled_face["neighbors"]
        ):
            # neighbor の face_id が変わっていないことを確認
            if orig_neighbor["face_id"] != relabeled_neighbor["face_id"]:
                raise ValueError(
                    f"neighbor の face_id が変更されています"
                )
            
            # edge_id が正しくマッピングされていることを確認
            expected_new_edge_id = edge_mapping[orig_neighbor["edge_id"]]
            if relabeled_neighbor["edge_id"] != expected_new_edge_id:
                raise ValueError(
                    f"edge_id のマッピングが不正: "
                    f"{orig_neighbor['edge_id']} → {relabeled_neighbor['edge_id']} "
                    f"(expected: {expected_new_edge_id})"
                )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python -m edge_relabeling.relabeler <polyhedron.json> <edge_mapping.json> <output.json>")
        sys.exit(1)
    
    polyhedron_path = Path(sys.argv[1])
    mapping_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])
    
    print(f"Relabeling polyhedron edges...")
    print(f"  Input polyhedron: {polyhedron_path}")
    print(f"  Edge mapping:     {mapping_path}")
    print(f"  Output:           {output_path}")
    
    try:
        # データを読み込む
        polyhedron = load_polyhedron(polyhedron_path)
        edge_mapping = load_edge_mapping(mapping_path)
        
        print(f"\n  Polyhedron: {polyhedron['polyhedron']['class']}/{polyhedron['polyhedron']['name']}")
        print(f"  Faces: {len(polyhedron['faces'])}")
        print(f"  Edge mapping size: {len(edge_mapping)}")
        
        # 辺ラベルを貼り替える
        relabeled = relabel_polyhedron(polyhedron, edge_mapping)
        
        # 妥当性を検証
        verify_relabeling(polyhedron, relabeled, edge_mapping)
        
        # 保存
        save_polyhedron(relabeled, output_path)
        
        print(f"\n✓ Success!")
        print(f"  Saved to {output_path}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
