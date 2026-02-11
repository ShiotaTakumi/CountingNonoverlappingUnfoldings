"""
relabeler.py

polyhedron.json の辺ラベルを、edge_mapping に従って貼り替え、
polyhedron_relabeled.json を生成する。
"""

import json
from pathlib import Path
from typing import Dict, Any


def load_polyhedron(polyhedron_path: Path) -> Dict[str, Any]:
    """
    polyhedron.json を読み込む
    
    Args:
        polyhedron_path: polyhedron.json のパス
    
    Returns:
        polyhedron データ（辞書）
    """
    with open(polyhedron_path, 'r') as f:
        return json.load(f)


def load_edge_mapping(mapping_path: Path) -> Dict[int, int]:
    """
    edge_mapping.json を読み込む
    
    Args:
        mapping_path: edge_mapping.json のパス
    
    Returns:
        {旧 edge_id: 新 edge_id} の辞書
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
    polyhedron の辺ラベルを貼り替える
    
    Args:
        polyhedron: 元の polyhedron データ
        edge_mapping: {旧 edge_id: 新 edge_id} の辞書
    
    Returns:
        辺ラベルが貼り替えられた polyhedron データ
    
    Raises:
        ValueError: マッピングに存在しない edge_id が見つかった場合
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
    polyhedron を JSON ファイルとして保存
    
    Args:
        polyhedron: polyhedron データ
        output_path: 出力ファイルパス
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
    辺ラベル貼り替えの妥当性を検証
    
    Args:
        original: 元の polyhedron データ
        relabeled: 貼り替え後の polyhedron データ
        edge_mapping: 使用した edge_mapping
    
    Raises:
        ValueError: 検証に失敗した場合
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
