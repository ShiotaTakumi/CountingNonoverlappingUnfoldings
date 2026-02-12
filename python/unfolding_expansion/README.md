# unfolding_expansion — Phase 2 Implementation Notes

**Status**: ✅ Complete
**Last Updated**: 2026-02-12
**Purpose**: 辺ラベル貼り替えと同型展開復元（Phase 2）の実装メモ

---

## Overview / 概要

Phase 2 は Rotational Unfolding の `exact.jsonl` を入力として、以下を実行する：

1. **辺ラベル貼り替え** — Phase 1 の新ラベル体系に合わせて `edge_id` を更新
2. **同型展開復元** — 非同型のみの `exact.jsonl` から、同型変種を生成
3. **最終出力** — `unfoldings_overlapping_all.jsonl`（schema_version: 2）

**設計方針**:
- **中間出力（`exact_relabeled.jsonl`）では幾何情報を保持** — 検証目的
- **最終出力（`unfoldings_overlapping_all.jsonl`）では幾何情報を削除** — Counting は純粋に組合せ構造のみを扱う
- 重なり判定は Rotational Unfolding 側で完了済み
- 同型展開のアルゴリズムは `Reserch2024/EnumerateEdgesOfMOPE/` を Python に移植

---

## Current Implementation Status / 実装状況

### ✅ 完了済み

Phase 2 は完全に実装され、テスト済みです。

#### Step 1: 辺ラベル貼り替え
**Module**: [`relabeler.py`](relabeler.py)

- `exact.jsonl` の各レコードの `edge_id` を新ラベル体系に更新
- **幾何情報を保持**（`x`, `y`, `angle_deg`）— 検証目的で残す
- 探索情報を削除（`base_pair`, `symmetric_used`）
- 組合せ構造と幾何情報を保持（`face_id`, `gon`, `edge_id`, `x`, `y`, `angle_deg`）

**入力**:
- `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl`
- `data/polyhedra/<class>/<name>/edge_mapping.json`（Phase 1 成果物）

**出力**:
- `data/polyhedra/<class>/<name>/exact_relabeled.jsonl`
- **幾何情報を含む**（描画・検証用）

**可視化**:
- `python/drawing/` モジュールを使用して SVG 生成可能
- 使用例: `PYTHONPATH=python python -m drawing --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl`
- 出力先: `data/polyhedra/<class>/<name>/draw/exact_relabeled/`

**テスト結果**:
- johnson/n20: 4 レコード処理成功 ✅
- johnson/n24: 6 レコード処理成功 ✅
- archimedean/s12L: 3 レコード処理成功 ✅
- 描画テスト: johnson/n20, archimedean/s12L で SVG 生成確認 ✅

#### Step 2: 同型展開復元
**Module**: [`isomorphism_expander.py`](isomorphism_expander.py)

`Reserch2024/EnumerateEdgesOfMOPE/` の C++ アルゴリズムを Python に移植し、
標準形の展開図から全ての同型変種を多面体上で列挙します。

**アルゴリズム概要**:
1. **接続列の構築**（`UnfoldingSequence.build_sequence`）:
   - `exact_relabeled.jsonl` のレコードから面の接続関係を表す列を生成
   - 形式: `[gon_0, 0, gon_1, offset_1, gon_2, offset_2, ..., gon_n]`
   - `gon_i`: 面 i が何角形か
   - `offset_i`: 前の面から次の面への辺の相対位置

2. **反転形の生成**（`UnfoldingSequence.flip_sequence`）:
   - 標準形から鏡像反転した接続列を生成
   - 位相構造を保ちながら空間的な向きを逆転

3. **多面体上でのマッチング**（`IsomorphicUnfoldingFinder`）:
   - 接続列（標準形 + 反転形）を多面体の全ての面・辺の組合せで試行
   - gon 値とオフセットが一致する経路を探索
   - ツリー構造を保証（各面は1回のみ使用）

4. **面情報の復元**（`reconstruct_unfolding_record`）:
   - マッチした面列から完全な展開図レコードを復元
   - `polyhedron_relabeled.json` と照合して `face_id`, `gon`, `edge_id` を保持
   - **これは描画検証に不可欠**

**入力**:
- `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`（Phase 1 成果物）
- `data/polyhedra/<class>/<name>/exact_relabeled.jsonl`（Step 1 成果物）

**出力**:
- `data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl`
- **schema_version: 2**
- **幾何情報なし**（組合せ構造のみ）
- **source メタデータ付き**（`input_file`, `input_record_index`, `isomorphism_variant`）

**テスト結果**:
- johnson/n20: 4 → 40 展開図 ✅（10倍拡張）
- johnson/n24: 6 → 60 展開図 ✅（10倍拡張）
- archimedean/s12L: 3 → 72 展開図 ✅（24倍拡張）

---

## 廃止された設計（採用されませんでした）

当初は以下の個別モジュールを計画していましたが、
`Reserch2024/EnumerateEdgesOfMOPE/` の既存ロジックを統合的に移植する方針に変更しました：

- ~~Step 2: `variant_generator.py`（4変種生成）~~
- ~~Step 3: `feasibility_checker.py`（実現可能性検証）~~
- ~~Step 4: `writer.py`（最終出力生成）~~

これらは `isomorphism_expander.py` に統合されています。

---

## Usage / 実行方法

### Phase 2 全体を実行（完全実装済み）

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl
```

**Arguments**（必須）:
- `--exact <path>`: Path to exact.jsonl from Rotational Unfolding

### 実行例

```bash
# johnson/n20 で実行
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl

# johnson/n24 で実行
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n24/exact.jsonl

# 別の環境での実行例（相対パスも可）
PYTHONPATH=python python -m unfolding_expansion \
  --exact ../RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl
```

---

## Input/Output Specification / 入出力仕様

### 入力ファイル

#### 1. exact.jsonl（Rotational Unfolding の出力）
**パス**: `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl`

**形式**: JSON Lines（1 行 1 レコード）

**スキーマ（schema_version: 1）**:
```json
{
  "schema_version": 1,
  "record_type": "partial_unfolding",
  "base_pair": {"base_face": 0, "base_edge": 0},
  "symmetric_used": false,
  "faces": [
    {
      "face_id": 0,
      "gon": 3,
      "edge_id": 0,
      "x": 0.0,
      "y": 0.0,
      "angle_deg": 0.0
    },
    ...
  ],
  "exact_overlap": {"kind": "face-face"}
}
```

#### 2. edge_mapping.json（Phase 1 の成果物）
**パス**: `data/polyhedra/<class>/<name>/edge_mapping.json`

**形式**: JSON

**内容**:
```json
{
  "0": 3,
  "1": 11,
  "2": 6,
  ...
}
```

- Key: 旧 edge_id（文字列）
- Value: 新 edge_id（整数）

### 出力ファイル（現在）

#### exact_relabeled.jsonl（Step 1 の中間出力）
**パス**: `data/polyhedra/<class>/<name>/exact_relabeled.jsonl`

**形式**: JSON Lines（1 行 1 レコード）

**スキーマ**:
```json
{
  "faces": [
    {
      "face_id": 0,
      "gon": 3,
      "edge_id": 3
    },
    ...
  ],
  "exact_overlap": {"kind": "face-face"}
}
```

**schema_version 1 からの変更点**:
- `base_pair` 削除
- `symmetric_used` 削除
- `faces[].x` 削除
- `faces[].y` 削除
- `faces[].angle_deg` 削除

### 最終出力ファイル（未実装）

#### unfoldings_overlapping_all.jsonl（Phase 2 の最終成果物）
**パス**: `data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl`

**スキーマ（schema_version: 2）**:
```json
{
  "schema_version": 2,
  "record_type": "partial_unfolding",
  "source": {
    "phase": "counting-phase2",
    "input_file": "RotationalUnfolding/.../exact.jsonl",
    "input_record_index": 0,
    "isomorphism_variant": "original"
  },
  "faces": [
    {"face_id": 0, "gon": 3, "edge_id": 3},
    ...
  ],
  "exact_overlap": {"kind": "face-face"}
}
```

---

## Implementation Details / 実装詳細

### Module Structure / モジュール構成

```
python/unfolding_expansion/
├── __init__.py              # パッケージ初期化
├── __main__.py              # エントリポイント
├── cli.py                   # CLI orchestration
├── relabeler.py             # Step 1: 辺ラベル貼り替え ✅
├── variant_generator.py     # Step 2: 同型変種生成 🚧
├── feasibility_checker.py   # Step 3: 実現可能性検証 🚧
├── writer.py                # Step 4: 最終出力生成 🚧
└── README.md                # このファイル
```

### relabeler.py の主要関数

#### `load_edge_mapping(edge_mapping_path: Path) -> Dict[int, int]`
- `edge_mapping.json` を読み込み
- 文字列キーを整数に変換
- Returns: `{old_edge_id: new_edge_id}`

#### `relabel_record(record: Dict, edge_mapping: Dict) -> Dict`
- 1 レコードに辺ラベル貼り替えを適用
- 幾何情報・探索情報を削除
- 組合せ構造のみを保持

#### `relabel_exact_jsonl(exact_jsonl_path, edge_mapping_path, output_path) -> int`
- `exact.jsonl` の全レコードを処理
- `exact_relabeled.jsonl` に書き出し
- Returns: 処理レコード数

### エラーハンドリング

- `schema_version` チェック（= 1）
- `edge_id` がマッピングに存在することを確認
- 入力ファイルの存在確認
- JSON parse エラーのハンドリング

---

## Test Results / テスト結果

### johnson/n20

**実行コマンド**:
```bash
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl
```

**結果**:
```
============================================================
Phase 2: Unfolding Expansion (Step 1: Edge Relabeling)
  Polyhedron: johnson/n20
============================================================

[Step 1/1] Relabeling edge IDs in exact.jsonl...
  Input:  /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl
  Mapping: /Users/tshiota/Github/CountingNonoverlappingUnfoldings/data/polyhedra/johnson/n20/edge_mapping.json
  Output: /Users/tshiota/Github/CountingNonoverlappingUnfoldings/data/polyhedra/johnson/n20/exact_relabeled.jsonl

  Processed: 4 records
  Output written: /Users/tshiota/Github/CountingNonoverlappingUnfoldings/data/polyhedra/johnson/n20/exact_relabeled.jsonl

============================================================
Phase 2 Step 1 Complete!
============================================================
```

**検証**:
- ✅ 4 レコード処理成功
- ✅ 辺ラベルが正しく変換（例: 0→3, 1→11, 31→37）
- ✅ 幾何情報削除（x, y, angle_deg）
- ✅ 探索情報削除（base_pair, symmetric_used）
- ✅ 組合せ構造保持（face_id, gon, edge_id, exact_overlap）

### johnson/n24

**実行コマンド**:
```bash
PYTHONPATH=python python -m unfolding_expansion \
  --exact /Users/tshiota/Github/RotationalUnfolding/output/polyhedra/johnson/n24/exact.jsonl
```

**結果**:
```
Processed: 6 records
Output written: .../johnson/n24/exact_relabeled.jsonl
```

**検証**:
- ✅ 6 レコード処理成功
- ✅ johnson/n20 と同様にすべての要件を満たす

---

## Design Decisions / 設計判断

### なぜ幾何情報を削除するか

1. **Counting は組合せ問題** — 「どの面が、どの辺で連結しているか」が本質
2. **重なり判定は完了済み** — Rotational Unfolding の `exact_overlap` が権威
3. **データサイズの削減** — 幾何情報削除により、ファイルサイズが約 50% 削減

### Phase 2 が扱うデータ

**使用する**:
- 面の識別子（face_id）
- 面の辺数（gon）
- 共有辺の識別子（edge_id）
- 重なりの種類（exact_overlap.kind）

**使用しない**:
- 面の配置（x, y）
- 面の向き（angle_deg）
- 探索の起点（base_pair）
- 対称性の使用有無（symmetric_used）

---

## Next Steps / 次のステップ

### 実装予定（優先度順）

1. **Step 2: 同型変種生成**
   - `variant_generator.py` を作成
   - 4 変種（original, flipped, reversed, flipped_reversed）の生成ロジック
   - 面列の操作（reversed は逆順、flipped は名前のみ保持）

2. **Step 3: 実現可能性検証**
   - `feasibility_checker.py` を作成
   - `polyhedron_relabeled.json` との照合
   - 連結性チェック（各面が前の面と `edge_id` で隣接しているか）

3. **Step 4: 最終出力生成**
   - `writer.py` を作成
   - `schema_version: 2` への更新
   - `source` メタデータの付与
   - `unfoldings_overlapping_all.jsonl` の生成

4. **CLI の拡張**
   - Step 1-4 を統合した実行フロー
   - 各ステップの進捗表示

---

## Known Issues / 既知の問題

現時点でなし。

---

## References / 参考資料

- Phase 2 仕様書: [`../.cursor/plans/PHASE2_RELABELING_AND_ISOMORPHISM_EXPANSION_SPEC.md`](../.cursor/plans/PHASE2_RELABELING_AND_ISOMORPHISM_EXPANSION_SPEC.md)
- Phase 1 実装: [`python/edge_relabeling/`](../edge_relabeling/)
- Phase 1 仕様書: [`docs/PHASE1_EDGE_RELABELING.md`](../../docs/PHASE1_EDGE_RELABELING.md)

---

## Development Log / 開発ログ

### 2026-02-12
- ✅ モジュール構造作成（`__init__.py`, `__main__.py`, `cli.py`）
- ✅ Step 1 実装（`relabeler.py`）
- ✅ johnson/n20 でテスト成功（4 レコード）
- ✅ johnson/n24 でテスト成功（6 レコード）
- ✅ README.md 作成
