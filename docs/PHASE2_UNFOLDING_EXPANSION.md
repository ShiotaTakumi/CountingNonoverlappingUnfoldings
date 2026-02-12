# Phase 2: Unfolding Expansion — Isomorphic Variant Enumeration

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-12

---

## Overview / 概要

Phase 2 implements unfolding expansion from canonical (non-isomorphic) forms to complete isomorphic variant sets. It transforms the edge-relabeled unfolding data from Rotational Unfolding, applying the new edge labeling system from Phase 1, and enumerates all topologically equivalent unfoldings realizable on the target polyhedron.

Phase 2 は、標準形（非同型）展開図から完全な同型変種集合への展開を実装します。Rotational Unfolding の辺ラベル貼り替え済み展開図データを Phase 1 の新しい辺ラベル体系に変換し、対象多面体上で実現可能な全ての位相的に同等な展開図を列挙します。

**This is the expansion layer for Counting pipeline.** Phase 2 bridges Phase 1 (polyhedron edge relabeling) and Phase 3 (graph data conversion) by:
1. Applying edge mapping to unfolding records
2. Expanding each canonical unfolding to all isomorphic variants
3. Reconstructing complete face/edge structure for each variant

**これは Counting パイプラインの展開レイヤです。** Phase 2 は Phase 1（多面体辺ラベル貼り替え）と Phase 3（グラフデータ変換）の橋渡しを行います：
1. 展開図レコードへの辺ラベル対応の適用
2. 各標準形展開図の全同型変種への展開
3. 各変種の完全な面・辺構造の復元

---

## Purpose and Scope / 目的と範囲

### What Phase 2 Does / Phase 2 が行うこと

Phase 2 focuses on **isomorphic unfolding enumeration** and defines the complete unfolding set for the Counting pipeline:

1. **Edge relabeling (Step 1)**: Updates `exact.jsonl` edge IDs to Phase 1's new labeling system.
2. **Connectivity sequence construction**: Encodes unfolding topology as face-connectivity sequences.
3. **Isomorphism expansion (Step 2)**: Enumerates all isomorphic variants on the polyhedron structure.
4. **Face structure reconstruction**: Recovers complete face/edge information for each variant.
5. **Schema transformation**: Outputs `unfoldings_overlapping_all.jsonl` with `schema_version: 2`.

Phase 2 は**同型展開図の列挙**に焦点を当て、Counting パイプラインのための完全な展開図集合を定義します：

1. **辺ラベル貼り替え（Step 1）**: `exact.jsonl` の辺 ID を Phase 1 の新しいラベル体系に更新します。
2. **接続列の構築**: 展開図の位相を面接続列として符号化します。
3. **同型展開（Step 2）**: 多面体構造上の全同型変種を列挙します。
4. **面構造の復元**: 各変種の完全な面・辺情報を復元します。
5. **スキーマ変換**: `schema_version: 2` で `unfoldings_overlapping_all.jsonl` を出力します。

### What Phase 2 Does NOT Do / Phase 2 が行わないこと

Phase 2 intentionally **does not** implement:

- **Overlap detection**: Assumes Rotational Unfolding's overlap classification is correct.
- **Geometric computation**: Does not calculate coordinates, angles, or intersection tests.
- **Graph conversion**: Edge set extraction for ZDD is Phase 3's responsibility.
- **ZDD construction**: Combinatorial enumeration is Phase 4's responsibility.
- **Batch processing**: Each polyhedron must be processed individually.

Phase 2 は意図的に以下を実装**しません**：

- **重なり判定**: Rotational Unfolding の重なり分類が正しいと仮定します。
- **幾何計算**: 座標、角度、交差テストを計算しません。
- **グラフ変換**: ZDD 用の辺集合抽出は Phase 3 の責務です。
- **ZDD 構築**: 組合せ列挙は Phase 4 の責務です。
- **バッチ処理**: 各多面体は個別に処理する必要があります。

---

## Input Files / 入力ファイル

Phase 2 requires the following inputs:

### 1. polyhedron_relabeled.json (from Phase 1)

**Path:**
```
data/polyhedra/<class>/<name>/polyhedron_relabeled.json
```

**Purpose:** Provides polyhedron structure with Phase 1's optimized edge labels.

**Required Fields:**
- `faces[]`: Array of face objects
  - `face_id`: Face identifier (unchanged from Phase 1)
  - `gon`: Number of sides (3, 4, 5, etc.)
  - `neighbors[]`: Adjacent faces and shared edges
    - `edge_id`: Edge identifier (Phase 1's new labeling)
    - `face_id`: Adjacent face identifier

**用途:** Phase 1 の最適化された辺ラベルを持つ多面体構造を提供します。

### 2. edge_mapping.json (from Phase 1)

**Path:**
```
data/polyhedra/<class>/<name>/edge_mapping.json
```

**Purpose:** Maps old edge IDs (Rotational Unfolding) to new edge IDs (Phase 1).

**Format:**
```json
{
  "0": 15,
  "1": 20,
  "2": 18,
  ...
}
```

**用途:** 旧辺 ID（Rotational Unfolding）を新辺 ID（Phase 1）にマッピングします。

### 3. exact.jsonl (from Rotational Unfolding)

**Path:**
```
RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl
```

**Purpose:** Canonical (non-isomorphic) unfoldings with exact overlap detection.

**Format:** JSON Lines (one record per line)

**Required Fields per Record:**
- `schema_version`: 1
- `faces[]`: Ordered array of faces in unfolding tree
  - `face_id`: Face identifier (original labeling)
  - `gon`: Number of sides
  - `edge_id`: Shared edge with previous face (omitted for first face)
  - `x`, `y`: Face center coordinates (used for verification only)
  - `angle_deg`: Edge normal direction (used for verification only)
- `exact_overlap`: Overlap classification
  - `kind`: "face-face", "edge-edge", etc.

**用途:** 正確な重なり判定済みの標準形（非同型）展開図を提供します。

---

## Output Files / 出力ファイル

Phase 2 generates the following outputs:

### 1. exact_relabeled.jsonl (intermediate)

**Path:**
```
data/polyhedra/<class>/<name>/exact_relabeled.jsonl
```

**Purpose:** Edge-relabeled canonical unfoldings (Step 1 output, Step 2 input).

**Format:** JSON Lines

**Fields:**
- All fields from `exact.jsonl` with updated `edge_id` values
- Geometric information (`x`, `y`, `angle_deg`) preserved for verification
- Search control fields (`base_pair`, `symmetric_used`) removed

**Example:**
```json
{
  "faces": [
    {"face_id": 0, "gon": 3, "x": 0.0, "y": 0.0, "angle_deg": 0.0},
    {"face_id": 3, "gon": 4, "edge_id": 3, "x": 0.788675, "y": 0.0, "angle_deg": -180.0},
    ...
  ],
  "exact_overlap": {"kind": "face-face"}
}
```

**用途:** 辺ラベル貼り替え済み標準形展開図（Step 1 出力、Step 2 入力）。

### 2. unfoldings_overlapping_all.jsonl (final output)

**Path:**
```
data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
```

**Purpose:** Complete set of all isomorphic unfolding variants (Phase 2 final output).

**Format:** JSON Lines

**Schema Version:** 2

**Fields:**
- `schema_version`: 2 (indicates Phase 2 output)
- `faces[]`: Ordered array of faces
  - `face_id`: Face identifier (Phase 1 labeling)
  - `gon`: Number of sides
  - `edge_id`: Shared edge (omitted for first face)
  - `x`, `y`, `angle_deg`: Geometric info (approximate, for visualization)
- `exact_overlap`: Overlap classification (from source record)
- `source`: Provenance metadata
  - `input_file`: "exact_relabeled.jsonl"
  - `input_record_index`: Source record line number (0-based)
  - `isomorphism_variant`: "standard" or "flipped"

**Example:**
```json
{
  "schema_version": 2,
  "faces": [
    {"face_id": 0, "gon": 3, "x": 0.0, "y": 0.0, "angle_deg": 0.0},
    {"face_id": 3, "gon": 4, "edge_id": 3, "x": 0.788675, "y": 0.0, "angle_deg": -180.0},
    ...
  ],
  "exact_overlap": {"kind": "face-face"},
  "source": {
    "input_file": "exact_relabeled.jsonl",
    "input_record_index": 0,
    "isomorphism_variant": "standard"
  }
}
```

**Key Differences from Schema Version 1:**
- `schema_version: 2` (explicit Phase 2 marker)
- `source` metadata for traceability
- Geometric info is approximate (reused from source for visualization)
- All isomorphic variants included (not just canonical forms)

**Schema Version 1 との主な違い:**
- `schema_version: 2`（Phase 2 出力の明示的マーカー）
- 追跡可能性のための `source` メタデータ
- 幾何情報は近似（可視化用に元データから再利用）
- 全同型変種を含む（標準形のみではない）

**用途:** 全同型展開変種の完全集合（Phase 2 最終出力）。

---

## Processing Steps / 処理ステップ

Phase 2 consists of two sequential steps:

### Step 1: Edge Relabeling

**Module:** `python/unfolding_expansion/relabeler.py`

**Input:**
- `exact.jsonl` (Rotational Unfolding output)
- `edge_mapping.json` (Phase 1 output)

**Output:**
- `exact_relabeled.jsonl`

**Process:**
1. Load edge mapping from Phase 1
2. For each record in `exact.jsonl`:
   - Update all `edge_id` fields using the mapping
   - Remove search control fields (`base_pair`, `symmetric_used`)
   - Preserve geometric fields (`x`, `y`, `angle_deg`) for verification
   - Preserve face structure (`face_id`, `gon`, `exact_overlap`)
3. Write to `exact_relabeled.jsonl`

**処理:**
1. Phase 1 の辺ラベル対応表を読み込む
2. `exact.jsonl` の各レコードについて：
   - 対応表を用いて全 `edge_id` フィールドを更新
   - 探索制御フィールド（`base_pair`, `symmetric_used`）を削除
   - 検証用に幾何フィールド（`x`, `y`, `angle_deg`）を保持
   - 面構造（`face_id`, `gon`, `exact_overlap`）を保持
3. `exact_relabeled.jsonl` に書き出す

### Step 2: Isomorphism Expansion

**Module:** `python/unfolding_expansion/isomorphism_expander.py`

**Input:**
- `exact_relabeled.jsonl` (Step 1 output)
- `polyhedron_relabeled.json` (Phase 1 output)

**Output:**
- `unfoldings_overlapping_all.jsonl`

**Process:**
1. Load polyhedron adjacency structure
2. For each record in `exact_relabeled.jsonl`:
   a. **Build connectivity sequence**:
      - Encode face-connectivity as `[gon_0, 0, gon_1, offset_1, ..., gon_n]`
      - `gon_i`: n-gon value of face i
      - `offset_i`: Clockwise edge distance from previous to next shared edge

   b. **Generate flipped variant**:
      - Create mirror-reflected connectivity sequence
      - Preserves topology while reversing spatial orientation

   c. **Enumerate matching unfoldings**:
      - For each sequence (standard + flipped):
        - Try all starting faces with matching first `gon`
        - Try all starting edges of that face
        - Walk the sequence, matching `gon` and `offset` at each step
        - Track used faces to ensure tree structure (no cycles)
        - If complete match, record the face sequence

   d. **Reconstruct face structure**:
      - For each matched face sequence:
        - Look up `face_id`, `gon` from `polyhedron_relabeled.json`
        - Find shared `edge_id` between consecutive faces
        - Copy geometric info from source record (approximate)
        - Add `source` metadata for provenance

   e. **Append to output**: Write record with `schema_version: 2`

3. Write all expanded records to `unfoldings_overlapping_all.jsonl`

**処理:**
1. 多面体の隣接構造を読み込む
2. `exact_relabeled.jsonl` の各レコードについて：
   a. **接続列を構築**:
      - 面接続を `[gon_0, 0, gon_1, offset_1, ..., gon_n]` として符号化
      - `gon_i`: 面 i の n 角形値
      - `offset_i`: 前の共有辺から次の共有辺への時計回り辺距離

   b. **反転変種を生成**:
      - 鏡像反転した接続列を作成
      - 位相を保ちながら空間的向きを反転

   c. **マッチング展開図を列挙**:
      - 各列（標準形 + 反転形）について：
        - 最初の `gon` と一致する全開始面を試行
        - その面の全開始辺を試行
        - 列を辿り、各ステップで `gon` と `offset` をマッチング
        - ツリー構造を保証するため使用済み面を追跡（閉路なし）
        - 完全にマッチしたら面列を記録

   d. **面構造を復元**:
      - 各マッチした面列について：
        - `polyhedron_relabeled.json` から `face_id`, `gon` を検索
        - 連続する面間の共有 `edge_id` を探索
        - 元レコードから幾何情報をコピー（近似）
        - 由来追跡のため `source` メタデータを追加

   e. **出力に追加**: `schema_version: 2` でレコードを書き出す

3. 展開された全レコードを `unfoldings_overlapping_all.jsonl` に書き出す

**Algorithm Origin:**

The isomorphism expansion algorithm is based on `Reserch2024/EnumerateEdgesOfMOPE/` (C++ implementation), ported to Python for integration with the Counting pipeline. The core matching logic uses connectivity sequences to efficiently enumerate topologically equivalent unfoldings without explicit graph isomorphism testing.

同型展開アルゴリズムは `Reserch2024/EnumerateEdgesOfMOPE/`（C++ 実装）に基づき、Counting パイプラインへの統合のため Python に移植されています。コアマッチングロジックは、明示的なグラフ同型性テストなしに位相的に同等な展開図を効率的に列挙するために接続列を使用します。

---

## Module Structure / モジュール構造

```
python/unfolding_expansion/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point (python -m unfolding_expansion)
├── cli.py                   # Command-line interface
├── relabeler.py             # Step 1: Edge relabeling
├── isomorphism_expander.py  # Step 2: Isomorphism expansion
└── README.md                # Implementation notes (development log)
```

### Module Responsibilities / モジュールの責務

**`relabeler.py`:**
- Loads `exact.jsonl` and `edge_mapping.json`
- Updates edge IDs in unfolding records
- Removes search control fields
- Preserves geometric information for verification
- Outputs `exact_relabeled.jsonl`

**`isomorphism_expander.py`:**
- Defines `PolyhedronData` class for adjacency structure
- Implements `UnfoldingSequence` for connectivity encoding
- Implements `IsomorphicUnfoldingFinder` for matching
- Reconstructs complete face/edge structure
- Outputs `unfoldings_overlapping_all.jsonl` with `schema_version: 2`

**`cli.py`:**
- Parses `--exact <path>` argument
- Resolves input/output paths
- Orchestrates Step 1 and Step 2 execution
- Reports progress and handles errors

---

## Data Schema Evolution / データスキーマの進化

### Schema Version 1 (Rotational Unfolding)

- Used in `exact.jsonl`
- Contains geometric information (`x`, `y`, `angle_deg`)
- Contains search control fields (`base_pair`, `symmetric_used`)
- Canonical (non-isomorphic) unfoldings only
- No provenance metadata

### Schema Version 2 (Phase 2 Output)

- Used in `unfoldings_overlapping_all.jsonl`
- Geometric information is approximate (reused from source)
- No search control fields
- All isomorphic variants included
- Provenance metadata (`source`) for traceability
- Explicit `schema_version: 2` field

**Key Design Decision:**

Geometric information is preserved in `unfoldings_overlapping_all.jsonl` as an approximation for visualization purposes. This allows drawing/verification of expanded unfoldings, though the geometry may not be exact for all isomorphic variants (since they use different face placements on the polyhedron). The combinatorial structure (face connectivity) is always exact.

**重要な設計判断:**

幾何情報は可視化目的の近似として `unfoldings_overlapping_all.jsonl` に保持されます。これにより展開図の描画・検証が可能になりますが、全ての同型変種について幾何情報が正確とは限りません（多面体上の異なる面配置を使用するため）。組合せ構造（面の接続関係）は常に正確です。

---

## Directory Structure / ディレクトリ構成

```
CountingNonoverlappingUnfoldings/
├── data/
│   └── polyhedra/
│       └── <class>/
│           └── <name>/
│               ├── polyhedron_relabeled.json    (Phase 1 output, Phase 2 input)
│               ├── edge_mapping.json            (Phase 1 output, Phase 2 input)
│               ├── exact_relabeled.jsonl        (Phase 2 Step 1 output)
│               └── unfoldings_overlapping_all.jsonl (Phase 2 final output)
│
├── output/
│   └── polyhedra/
│       └── <class>/
│           └── <name>/
│               └── draw/
│                   ├── exact_relabeled/         (Verification SVGs)
│                   └── unfoldings_overlapping_all/ (Verification SVGs)
│
└── python/
    └── unfolding_expansion/
        ├── __init__.py
        ├── __main__.py
        ├── cli.py
        ├── relabeler.py
        ├── isomorphism_expander.py
        └── README.md
```

**Naming Convention:**

- Input files use original names from source phases
- Intermediate output: `exact_relabeled.jsonl`
- Final output: `unfoldings_overlapping_all.jsonl`
- Schema version indicates processing stage

**命名規則:**

- 入力ファイルは元フェーズの元の名前を使用
- 中間出力: `exact_relabeled.jsonl`
- 最終出力: `unfoldings_overlapping_all.jsonl`
- スキーマバージョンが処理段階を示す

---

## Usage / 実行方法

### Basic Execution / 基本実行

```bash
cd /path/to/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m unfolding_expansion \
  --exact /path/to/RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl
```

### Example / 実行例

```bash
# Johnson solid n20
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl

# Archimedean solid s12L
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/archimedean/s12L/exact.jsonl
```

### Prerequisites / 前提条件

Before running Phase 2, ensure:
1. Phase 1 has been executed for the target polyhedron
2. `polyhedron_relabeled.json` exists in `data/polyhedra/<class>/<name>/`
3. `edge_mapping.json` exists in `data/polyhedra/<class>/<name>/`
4. `exact.jsonl` exists in `RotationalUnfolding/output/polyhedra/<class>/<name>/`

Phase 2 を実行する前に、以下を確認してください：
1. 対象多面体について Phase 1 が実行済み
2. `data/polyhedra/<class>/<name>/` に `polyhedron_relabeled.json` が存在
3. `data/polyhedra/<class>/<name>/` に `edge_mapping.json` が存在
4. `RotationalUnfolding/output/polyhedra/<class>/<name>/` に `exact.jsonl` が存在

### Output Verification / 出力検証

Verify Phase 2 output using the drawing utility:

```bash
# Verify Step 1 output (edge relabeling)
PYTHONPATH=python python -m drawing \
  --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl

# Verify Step 2 output (isomorphism expansion)
PYTHONPATH=python python -m drawing \
  --jsonl data/polyhedra/johnson/n20/unfoldings_overlapping_all.jsonl
```

SVG files are generated in:
- `output/polyhedra/<class>/<name>/draw/exact_relabeled/`
- `output/polyhedra/<class>/<name>/draw/unfoldings_overlapping_all/`

---

## Phase 2 in Pipeline Context / パイプライン内での Phase 2 の位置づけ

```
Phase 1: Edge Relabeling
  ↓ (polyhedron_relabeled.json, edge_mapping.json)
Phase 2: Unfolding Expansion ← YOU ARE HERE
  ↓ (unfoldings_overlapping_all.jsonl, schema_version: 2)
Phase 3: Graph Data Conversion
  ↓ (edge set extraction)
Phase 4: ZDD Construction
  ↓ (combinatorial enumeration)
Phase 5: Filtering
  ↓ (non-overlapping counting)
```

**Phase 2's Role:**
- Bridges polyhedron relabeling (Phase 1) and graph conversion (Phase 3)
- Transforms canonical unfoldings to complete isomorphic sets
- Establishes schema_version: 2 as the standard for expanded unfoldings
- Provides verification support through preserved geometric information

**Phase 2 の役割:**
- 多面体辺ラベル貼り替え（Phase 1）とグラフ変換（Phase 3）の橋渡し
- 標準形展開図を完全な同型集合に変換
- 展開済み展開図の標準として schema_version: 2 を確立
- 保持された幾何情報を通じて検証サポートを提供

---

## Notes on Independent Modules / 独立モジュールに関する注記

### Drawing Module

The `python/drawing/` module is an independent visualization utility, **not part of Phase 2**. It is used for verification purposes but is not a phase or sub-phase of the Counting pipeline.

- `draw_raw.py`: Identical to RotationalUnfolding's implementation
- `cli.py`: Customized for CountingNonoverlappingUnfoldings (output directory structure)
- Purpose: Visualization and verification only
- No semantic extension from RotationalUnfolding

`python/drawing/` モジュールは独立した可視化ユーティリティであり、**Phase 2 の一部ではありません**。検証目的で使用されますが、Counting パイプラインのフェーズまたはサブフェーズではありません。

- `draw_raw.py`: RotationalUnfolding の実装と同一
- `cli.py`: CountingNonoverlappingUnfoldings 用にカスタマイズ（出力ディレクトリ構造）
- 目的: 可視化と検証のみ
- RotationalUnfolding からの意味的拡張なし

---

## Test Results / テスト結果

Phase 2 has been tested on the following polyhedra:

| Polyhedron | Input Records | Output Records | Expansion Ratio | Status |
|------------|--------------|----------------|-----------------|--------|
| johnson/n20 | 4 | 40 | 10× | ✅ Verified |
| johnson/n24 | 6 | 60 | 10× | ✅ Verified |
| archimedean/s12L | 3 | 72 | 24× | ✅ Verified |

**Verification Method:**
- Visual inspection of SVG outputs from `python/drawing/`
- Schema validation of `unfoldings_overlapping_all.jsonl`
- Line count verification (JSONL records match reported counts)

**検証方法:**
- `python/drawing/` からの SVG 出力の目視検査
- `unfoldings_overlapping_all.jsonl` のスキーマ検証
- 行数検証（JSONL レコード数が報告されたカウントと一致）

---

## References / 参考文献

- Phase 1 Specification: `docs/PHASE1_EDGE_RELABELING.md`
- Rotational Unfolding: `/Users/tshiota/Github/RotationalUnfolding/`
- Algorithm Source: `Reserch2024/EnumerateEdgesOfMOPE/` (C++ implementation)
- Implementation Notes: `python/unfolding_expansion/README.md`

---

**Document Version History:**

- 1.0.0 (2026-02-12): Initial specification freeze
