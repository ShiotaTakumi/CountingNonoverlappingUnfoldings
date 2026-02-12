"""
isomorphism_expander — Isomorphic unfolding expansion from canonical forms.

同型展開図の復元（標準形から全同型変種を生成）。

This module implements the core logic of Phase 2: expanding canonical (non-isomorphic)
unfoldings from RotationalUnfolding into all isomorphic variants that can be realized
on the target polyhedron.

このモジュールは Phase 2 のコアロジックを実装：RotationalUnfolding の標準形（非同型）
展開図から、対象多面体上で実現可能な全ての同型変種を生成する。

Based on the algorithm from Reserch2024/EnumerateEdgesOfMOPE/.
Reserch2024/EnumerateEdgesOfMOPE/ のアルゴリズムに基づく。
"""

from typing import Dict, List, Tuple, Set, Any
import json


class PolyhedronData:
    """
    Polyhedron adjacency data structure.

    多面体の隣接関係データ構造。

    Attributes:
        num_faces: Number of faces (面の個数)
        gon: List of n-gon values for each face (各面が何角形か)
        adj_edge: For each face, list of adjacent edge IDs (各面の周りを囲む辺のリスト)
        adj_face: For each face, list of adjacent face IDs (各面の隣接面のリスト)
    """

    def __init__(self):
        self.num_faces: int = 0
        self.gon: List[int] = []
        self.adj_edge: List[List[int]] = []
        self.adj_face: List[List[int]] = []

    @classmethod
    def from_json(cls, polyhedron_json: Dict[str, Any]) -> 'PolyhedronData':
        """
        Load polyhedron data from polyhedron_relabeled.json.

        polyhedron_relabeled.json から多面体データを読み込む。

        Args:
            polyhedron_json: Parsed JSON data from polyhedron_relabeled.json

        Returns:
            PolyhedronData: Adjacency structure for the polyhedron
        """
        poly = cls()
        faces = polyhedron_json["faces"]
        poly.num_faces = len(faces)

        # Build adjacency lists
        # 隣接リストを構築
        for face in faces:
            poly.gon.append(face["gon"])

            edge_list = []
            face_list = []
            for neighbor in face["neighbors"]:
                edge_list.append(neighbor["edge_id"])
                face_list.append(neighbor["face_id"])

            poly.adj_edge.append(edge_list)
            poly.adj_face.append(face_list)

        return poly


class UnfoldingSequence:
    """
    Connectivity sequence representation of a partial unfolding.

    部分展開図の接続関係を表す列。

    The sequence encodes how faces are connected in the unfolding tree:
    [gon_0, offset_0, gon_1, offset_1, ..., gon_n]

    列は展開図ツリーで面がどう接続されているかを符号化：
    [gon_0, offset_0, gon_1, offset_1, ..., gon_n]

    - gon_i: n-gon value of face i (面 i が何角形か)
    - offset_i: Relative edge position from previous face (前の面から何辺進むか)

    See Reserch2024/EnumerateEdgesOfMOPE/PartialUnfoldingConnectivity.cpp for details.
    詳細は Reserch2024/EnumerateEdgesOfMOPE/PartialUnfoldingConnectivity.cpp を参照。
    """

    @staticmethod
    def build_sequence(
        unfolding_record: Dict[str, Any],
        poly: PolyhedronData
    ) -> List[int]:
        """
        Build connectivity sequence from exact_relabeled.jsonl record.

        exact_relabeled.jsonl のレコードから接続列を構築する。

        Args:
            unfolding_record: Single record from exact_relabeled.jsonl
            poly: Polyhedron adjacency data

        Returns:
            List[int]: Connectivity sequence [gon_0, 0, gon_1, offset_1, ..., gon_n]

        Algorithm (from PartialUnfoldingConnectivity.cpp):
            For each face in the unfolding:
            1. Record its gon value
            2. Find the offset from previous edge to next edge
            3. Offset = clockwise distance on the face's edge list

        アルゴリズム（PartialUnfoldingConnectivity.cpp より）:
            展開図の各面について：
            1. gon 値を記録
            2. 前の辺から次の辺へのオフセットを求める
            3. オフセット = 面の辺リスト上の時計回り距離
        """
        faces = unfolding_record["faces"]
        sequence = []

        for j, face_data in enumerate(faces):
            gon = face_data["gon"]
            face_id = face_data["face_id"]

            sequence.append(gon)

            if j == 0:
                # First face: no previous edge
                # 最初の面：前の辺なし
                sequence.append(0)
            elif j < len(faces) - 1:
                # Middle faces: compute offset
                # 中間の面：オフセットを計算
                prev_edge_id = faces[j]["edge_id"]
                next_edge_id = faces[j + 1]["edge_id"]

                # Find position of prev_edge_id in this face's edge list
                # この面の辺リストで prev_edge_id の位置を探す
                pos = -1
                for k in range(gon):
                    if poly.adj_edge[face_id][k] == prev_edge_id:
                        pos = k
                        break

                if pos == -1:
                    raise ValueError(
                        f"Edge {prev_edge_id} not found in face {face_id}'s adjacency list"
                    )

                # Count clockwise distance from prev_edge to next_edge
                # prev_edge から next_edge への時計回り距離を数える
                cnt = 0
                for n in range(pos, pos + gon):
                    if poly.adj_edge[face_id][n % gon] == next_edge_id:
                        break
                    cnt += 1

                sequence.append(cnt)

        return sequence

    @staticmethod
    def flip_sequence(standard_form: List[int]) -> List[int]:
        """
        Generate flipped form of a connectivity sequence.

        接続列の反転形を生成する。

        Args:
            standard_form: Standard connectivity sequence

        Returns:
            List[int]: Flipped sequence

        Algorithm (from PartialUnfoldingConnectivity::getflippedForm):
            Flipping reverses the spatial orientation while preserving topology.

        アルゴリズム（PartialUnfoldingConnectivity::getflippedForm より）:
            反転は位相を保ちながら空間的な向きを逆にする。
        """
        flipped = []
        length = len(standard_form)

        flipped.append(standard_form[0])
        flipped.append(0)

        for i in range(2, length - 1, 2):
            flipped.append(standard_form[i])
            flipped.append(standard_form[i] - standard_form[i + 1])

        flipped.append(standard_form[length - 1])

        return flipped


class IsomorphicUnfoldingFinder:
    """
    Find all isomorphic unfoldings on a polyhedron given a connectivity sequence.

    接続列から多面体上の全同型展開図を探索する。

    This implements the core matching algorithm from FinderOfIsomorphicMOPE.cpp.
    FinderOfIsomorphicMOPE.cpp のコアマッチングアルゴリズムを実装。
    """

    def __init__(self, poly: PolyhedronData):
        """
        Initialize finder with polyhedron data.

        多面体データでファインダーを初期化。

        Args:
            poly: Polyhedron adjacency structure
        """
        self.poly = poly

    def find_matching_unfoldings(
        self,
        sequence: List[int]
    ) -> List[List[int]]:
        """
        Find all face sequences that match the given connectivity sequence.

        与えられた接続列にマッチする全ての面列を探索する。

        Args:
            sequence: Connectivity sequence [gon_0, 0, gon_1, offset_1, ..., gon_n]

        Returns:
            List of face sequences, where each sequence is a list of face IDs

        Algorithm (from FinderOfIsomorphicMOPE::compareSequenceMatching):
            1. Try all starting faces with matching gon value
            2. For each starting edge of that face:
                a. Walk the sequence, matching gon and offset at each step
                b. Track used faces to ensure tree structure (no cycles)
                c. If complete match, record the face sequence

        アルゴリズム（FinderOfIsomorphicMOPE::compareSequenceMatching より）:
            1. gon 値が一致する全ての開始面を試す
            2. その面の各開始辺について：
                a. 列を辿り、各ステップで gon とオフセットをマッチング
                b. 使用済み面を追跡してツリー構造を保証（閉路なし）
                c. 完全にマッチしたら面列を記録
        """
        face_sequences = []

        # Try all starting faces
        # 全ての開始面を試す
        for start_face_id in range(self.poly.num_faces):
            # Check if gon matches first face in sequence
            # 列の最初の面と gon が一致するか確認
            if sequence[0] != self.poly.gon[start_face_id]:
                continue

            # Try all starting edges of this face
            # この面の全ての開始辺を試す
            for start_edge_idx in range(len(self.poly.adj_edge[start_face_id])):
                face_seq = self._try_match_from_start(
                    sequence,
                    start_face_id,
                    start_edge_idx
                )

                if face_seq is not None:
                    face_sequences.append(face_seq)

        return face_sequences

    def _try_match_from_start(
        self,
        sequence: List[int],
        start_face_id: int,
        start_edge_idx: int
    ) -> List[int] | None:
        """
        Try to match sequence starting from a specific face and edge.

        特定の面と辺から列のマッチングを試みる。

        Args:
            sequence: Connectivity sequence
            start_face_id: Starting face ID
            start_edge_idx: Starting edge index in face's edge list

        Returns:
            List of face IDs if match succeeds, None otherwise
        """
        face_list = []

        curr_face = start_face_id
        curr_edge = self.poly.adj_edge[start_face_id][start_edge_idx]
        next_face = self.poly.adj_face[start_face_id][start_edge_idx]

        is_used = [True] * self.poly.num_faces  # True = unused, False = used

        # Walk the sequence
        # 列を辿る
        # Sequence format: [gon_0, 0, gon_1, offset_1, gon_2, offset_2, ..., gon_n]
        # Loop through middle elements (skip first gon and 0, process pairs)
        for k in range(2, len(sequence), 2):
            face_list.append(curr_face)
            is_used[curr_face] = False

            # Check if next face matches and is unused
            # 次の面がマッチし、未使用か確認
            if sequence[k] == self.poly.gon[next_face] and is_used[next_face]:
                # Find position of current edge in next face
                # 次の面で現在の辺の位置を探す
                pos = -1
                for m in range(self.poly.gon[next_face]):
                    if self.poly.adj_edge[next_face][m] == curr_edge:
                        pos = m
                        break

                if pos == -1:
                    return None

                # Move to next face
                # 次の面へ移動
                curr_face = next_face

                # Add last face if at end of sequence (no more offset)
                # 列の最後（offset がない）なら最後の面を追加
                if k == len(sequence) - 1:
                    face_list.append(curr_face)
                else:
                    # There is an offset at k+1
                    # k+1 に offset がある
                    offset = sequence[k + 1]
                    next_edge_idx = (pos + offset) % self.poly.gon[curr_face]
                    curr_edge = self.poly.adj_edge[curr_face][next_edge_idx]
                    next_face = self.poly.adj_face[curr_face][next_edge_idx]
            else:
                # Mismatch: abort
                # ミスマッチ：中止
                return None

        return face_list if face_list else None


def expand_to_isomorphic_unfoldings(
    unfolding_record: Dict[str, Any],
    poly: PolyhedronData,
    input_index: int
) -> List[Dict[str, Any]]:
    """
    Expand a single canonical unfolding into all isomorphic variants.
    
    1つの標準形展開図を全ての同型変種に展開する。
    
    Args:
        unfolding_record: Single record from exact_relabeled.jsonl
        poly: Polyhedron adjacency data
        input_index: Index of this record in input file (for provenance)
        
    Returns:
        List of expanded unfolding records with face information preserved
        
    Process:
        1. Build connectivity sequence from input record
        2. Generate flipped variant of sequence
        3. For each sequence (standard + flipped):
            - Find all matching face sequences on polyhedron
            - Reconstruct full unfolding data (face_id, gon, edge_id)
        4. Return all unique isomorphic unfoldings
        
    処理:
        1. 入力レコードから接続列を構築
        2. 列の反転形を生成
        3. 各列（標準形 + 反転形）について：
            - 多面体上でマッチする全ての面列を探す
            - 完全な展開図データ（face_id, gon, edge_id）を復元
        4. 全ての一意な同型展開図を返す
    """
    # Build connectivity sequences (standard + flipped)
    # 接続列を構築（標準形 + 反転形）
    standard_seq = UnfoldingSequence.build_sequence(unfolding_record, poly)
    flipped_seq = UnfoldingSequence.flip_sequence(standard_seq)
    
    finder = IsomorphicUnfoldingFinder(poly)
    
    all_unfoldings = []
    
    # Process both sequence variants
    # 両方の列変種を処理
    for variant_name, sequence in [("standard", standard_seq), ("flipped", flipped_seq)]:
        face_sequences = finder.find_matching_unfoldings(sequence)
        
        for face_seq in face_sequences:
            # Reconstruct full unfolding record with face information
            # 面情報を含む完全な展開図レコードを復元
            unfolding = reconstruct_unfolding_record(
                face_seq,
                poly,
                unfolding_record,
                input_index,
                variant_name
            )
            all_unfoldings.append(unfolding)
    
    return all_unfoldings


def reconstruct_unfolding_record(
    face_sequence: List[int],
    poly: PolyhedronData,
    source_record: Dict[str, Any],
    input_index: int,
    variant_name: str
) -> Dict[str, Any]:
    """
    Reconstruct a full unfolding record from a face sequence.
    
    面列から完全な展開図レコードを復元する。
    
    Args:
        face_sequence: List of face IDs in unfolding order
        poly: Polyhedron adjacency data
        source_record: Original record from exact_relabeled.jsonl (for geometric data)
        input_index: Source record index (for provenance)
        variant_name: "standard" or "flipped"
        
    Returns:
        Complete unfolding record with faces, edges, and metadata
        
    IMPORTANT: This function preserves face information (face_id, gon, edge_id)
    by cross-referencing with polyhedron_relabeled.json. This is critical for
    later visualization and verification.
    
    For geometric information (x, y, angle_deg), we reuse the source record's
    geometry as an approximation. This allows visualization of isomorphic variants,
    though the geometry may not be exact.
    
    重要: この関数は polyhedron_relabeled.json と照合することで面情報
    （face_id, gon, edge_id）を保持します。これは後の可視化と検証に不可欠です。
    
    幾何情報（x, y, angle_deg）については、元のレコードの幾何情報を近似として
    再利用します。これにより同型変種の可視化が可能になりますが、幾何情報は
    厳密には正確ではない場合があります。
    """
    faces = []
    source_faces = source_record["faces"]
    
    for i, face_id in enumerate(face_sequence):
        face_data = {
            "face_id": face_id,
            "gon": poly.gon[face_id]
        }
        
        # Add edge_id for all but the first face
        # 最初の面以外は edge_id を追加
        if i > 0:
            # Find shared edge between previous and current face
            # 前の面と現在の面の共有辺を探す
            prev_face_id = face_sequence[i - 1]
            shared_edge = find_shared_edge(poly, prev_face_id, face_id)
            
            if shared_edge is None:
                raise ValueError(
                    f"No shared edge found between faces {prev_face_id} and {face_id}"
                )
            
            face_data["edge_id"] = shared_edge
        
        # Copy geometric info from source record if available (for visualization)
        # 元のレコードから幾何情報をコピー（可視化用）
        if i < len(source_faces):
            source_face = source_faces[i]
            if "x" in source_face:
                face_data["x"] = source_face["x"]
            if "y" in source_face:
                face_data["y"] = source_face["y"]
            if "angle_deg" in source_face:
                face_data["angle_deg"] = source_face["angle_deg"]
        
        faces.append(face_data)
    
    # Build output record with schema_version: 2
    # schema_version: 2 で出力レコードを構築
    record = {
        "schema_version": 2,
        "faces": faces,
        "exact_overlap": source_record["exact_overlap"],
        "source": {
            "input_file": "exact_relabeled.jsonl",
            "input_record_index": input_index,
            "isomorphism_variant": variant_name
        }
    }
    
    return record


def find_shared_edge(
    poly: PolyhedronData,
    face_a: int,
    face_b: int
) -> int | None:
    """
    Find the shared edge between two adjacent faces.

    隣接する2つの面の共有辺を探す。

    Args:
        poly: Polyhedron adjacency data
        face_a: First face ID
        face_b: Second face ID

    Returns:
        Shared edge ID, or None if faces are not adjacent
    """
    edges_a = set(poly.adj_edge[face_a])
    edges_b = set(poly.adj_edge[face_b])

    shared = edges_a & edges_b

    if len(shared) == 0:
        return None
    elif len(shared) == 1:
        return shared.pop()
    else:
        # Multiple shared edges should not happen for valid polyhedra
        # 有効な多面体では複数の共有辺は起こらない
        raise ValueError(
            f"Faces {face_a} and {face_b} share multiple edges: {shared}"
        )
