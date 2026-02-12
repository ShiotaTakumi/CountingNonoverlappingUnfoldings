# graph_export — Graph Data Export for TdZdd

## Overview / 概要

Generates graph data from polyhedron and unfolding data for TdZdd input.

多面体と展開図データから TdZdd 入力用のグラフデータを生成します。

This module handles two tasks:
1. **Block A**: Generate `polyhedron.grh` from polyhedron structure
2. **Block B**: Extract edge sets from unfoldings to `unfoldings_edge_sets.jsonl`

このモジュールは2つのタスクを扱います:
1. **Block A**: 多面体構造から `polyhedron.grh` を生成
2. **Block B**: 展開図から辺集合を抽出し `unfoldings_edge_sets.jsonl` を生成

---

## Block A: Polyhedron Graph Generation / ブロック A: 多面体グラフ生成

### Purpose / 目的

- Read `polyhedron_relabeled.json` (Phase 1 output)
- Extract edge-face adjacency information
- Reconstruct vertices using Union-Find algorithm
- Generate `.grh` file in TdZdd-compatible format

- `polyhedron_relabeled.json`（Phase 1 出力）を読み込み
- 辺-面隣接情報を抽出
- Union-Find アルゴリズムで頂点を再構成
- TdZdd 互換形式で `.grh` ファイルを生成

### Input / 入力

**`polyhedron_relabeled.json`** (Phase 1 output)
- Location: `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`
- Schema version: 1
- Contains face adjacency with edge IDs

### Output / 出力

**`polyhedron.grh`** (TdZdd graph input)
- Location: `data/polyhedra/<class>/<name>/polyhedron.grh`
- Format: No header, 0-indexed vertices, min-max normalized
- Each line: `v1 v2` (space-separated)
- Edges in edge_id order (critical: do not reorder!)

### Usage / 使い方

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

---

## Block B: Edge Set Extraction / ブロック B: 辺集合抽出

### Purpose / 目的

- Read `unfoldings_overlapping_all.jsonl` (Phase 2 output)
- Extract edge_id sets from each unfolding's face sequence
- Generate `unfoldings_edge_sets.jsonl` (pure combinatorial data)
- Remove all geometric and overlap information

- `unfoldings_overlapping_all.jsonl`（Phase 2 出力）を読み込み
- 各展開図の面列から edge_id 集合を抽出
- `unfoldings_edge_sets.jsonl`（純粋な組合せデータ）を生成
- 全ての幾何情報と重なり情報を削除

### Input / 入力

**`unfoldings_overlapping_all.jsonl`** (Phase 2 output)
- Location: `data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl`
- Format: JSON Lines
- Each record contains:
  - `faces[]`: Ordered array of faces in unfolding tree
    - `face_id`: Face identifier
    - `edge_id`: Shared edge with previous face (omitted for first face)
    - Other fields (x, y, angle_deg, etc.) are ignored

### Output / 出力

**`unfoldings_edge_sets.jsonl`** (Edge set data)
- Location: `data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl`
- Format: JSON Lines
- Each record: `{"edges": [0, 1, 2, ...]}`
- Edge IDs are sorted in ascending order
- No geometric or overlap information

### Usage / 使い方

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -c "from graph_export.cli_edgeset import main_edgeset; import sys; sys.argv = ['', '--unfoldings', 'data/polyhedra/johnson/n20/unfoldings_overlapping_all.jsonl']; main_edgeset()"
```

---

## Test Cases / テストケース

### johnson/n20 (Elongated pentagonal pyramid / 伸長五角錐)

**Block A:**
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```
- Output: `data/polyhedra/johnson/n20/polyhedron.grh`
- 25 vertices, 45 edges
- ✓ Tested and validated

**Block B:**
```bash
PYTHONPATH=python python -c "from graph_export.cli_edgeset import main_edgeset; import sys; sys.argv = ['', '--unfoldings', 'data/polyhedra/johnson/n20/unfoldings_overlapping_all.jsonl']; main_edgeset()"
```
- Output: `data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl`
- 40 unfoldings (from Phase 2 isomorphism expansion)
- Edge count range: 5-15
- ✓ Tested and validated

### archimedean/s12L (Snub cube / ねじれ立方体)

**Block A:**
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/archimedean/s12L/polyhedron_relabeled.json
```
- Output: `data/polyhedra/archimedean/s12L/polyhedron.grh`
- 24 vertices, 60 edges
- ✓ Tested and validated

**Block B:**
```bash
PYTHONPATH=python python -c "from graph_export.cli_edgeset import main_edgeset; import sys; sys.argv = ['', '--unfoldings', 'data/polyhedra/archimedean/s12L/unfoldings_overlapping_all.jsonl']; main_edgeset()"
```
- Output: `data/polyhedra/archimedean/s12L/unfoldings_edge_sets.jsonl`
- 72 unfoldings
- Edge count: 10 (all unfoldings)
- ✓ Tested and validated

---

## Module Structure / モジュール構成

```
python/graph_export/
├── __init__.py                 # Package documentation
├── __main__.py                 # Entry point for Block A
├── __main__edgeset.py          # Entry point for Block B (internal)
├── cli.py                      # CLI for Block A (polyhedron.grh)
├── cli_edgeset.py              # CLI for Block B (edge sets)
├── graph_builder.py            # Vertex reconstruction (Union-Find)
├── grh_generator.py            # .grh file generation
├── edge_set_extractor.py       # Edge set extraction logic
└── README.md                   # This file
```

---

## Implementation Status / 実装状況

### ✅ Complete / 完了

Both Block A and Block B have been fully implemented and tested.

Block A と Block B の両方が完全に実装され、テスト済みです。

**Test Results / テスト結果:**
- ✓ johnson/n20: Block A (25V, 45E), Block B (40 unfoldings)
- ✓ archimedean/s12L: Block A (24V, 60E), Block B (72 unfoldings)

---

## Algorithms / アルゴリズム

### Block A: Vertex Reconstruction (Union-Find)

1. Assign virtual vertex IDs: `(face_id, index)` for each face vertex
2. Merge virtual vertices sharing the same edge using Union-Find
3. Map Union-Find representatives to consecutive 0-indexed vertex IDs
4. Normalize edges (min, max order)
5. Output edges in edge_id order (preserves Phase 1 edge labeling)

### Block B: Edge Set Extraction

For each unfolding record:
1. Read `faces[]` array
2. Collect all `edge_id` values (skip first face, which has no edge_id)
3. Remove duplicates using set
4. Sort in ascending order
5. Output as `{"edges": [...]}`

---

## Scope / 範囲

This module handles:
- Graph structure extraction (Block A)
- Edge set extraction (Block B)
- File generation for TdZdd input

このモジュールが扱うもの:
- グラフ構造抽出（Block A）
- 辺集合抽出（Block B）
- TdZdd 入力用ファイル生成

This module does NOT handle:
- ZDD construction (Phase 4)
- Overlap detection or geometric computation
- Counting or enumeration

このモジュールが扱わないもの:
- ZDD 構築（Phase 4）
- 重なり判定や幾何計算
- 数え上げや列挙

---

## Related Documentation / 関連ドキュメント

- Phase 2 specification: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- Implementation plan: `.cursor/plans/PHASE3_GRAPH_CONVERSION_IMPLEMENTATION_PLAN.md`
