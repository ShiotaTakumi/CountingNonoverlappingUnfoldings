# graph_export — Graph Data Export for TdZdd (Phase 3)

## Overview / 概要

Phase 3: Generates graph data from polyhedron and unfolding data for TdZdd input.

Phase 3: 多面体と展開図データから TdZdd 入力用のグラフデータを生成します。

This module handles two tasks in sequence:
1. **Block A**: Generate `polyhedron.grh` from polyhedron structure
2. **Block B**: Extract edge sets from unfoldings to `unfoldings_edge_sets.jsonl`

このモジュールは2つのタスクを順次実行します:
1. **Block A**: 多面体構造から `polyhedron.grh` を生成
2. **Block B**: 展開図から辺集合を抽出し `unfoldings_edge_sets.jsonl` を生成

---

## Usage / 使い方

### Basic Usage / 基本的な使い方

Run Phase 3 (Block A + Block B) with a single command:

単一コマンドで Phase 3（Block A + Block B）を実行:

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

This automatically:
1. Loads `polyhedron_relabeled.json`
2. Generates `polyhedron.grh` (Block A)
3. Loads `unfoldings_overlapping_all.jsonl` from the same directory
4. Generates `unfoldings_edge_sets.jsonl` (Block B)

これにより自動的に:
1. `polyhedron_relabeled.json` を読み込み
2. `polyhedron.grh` を生成（Block A）
3. 同じディレクトリから `unfoldings_overlapping_all.jsonl` を読み込み
4. `unfoldings_edge_sets.jsonl` を生成（Block B）

---

## Inputs and Outputs / 入力と出力

### Inputs / 入力

Both input files must be in the same directory:

両方の入力ファイルは同じディレクトリにある必要があります:

1. **`polyhedron_relabeled.json`** (Phase 1 output)
   - Location: `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`
   - Schema version: 1
   - Contains face adjacency with edge IDs

2. **`unfoldings_overlapping_all.jsonl`** (Phase 2 output)
   - Location: `data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl`
   - Schema version: 2
   - Contains all isomorphic unfolding variants with face sequences

### Outputs / 出力

Both outputs are generated in the same directory:

両方の出力は同じディレクトリに生成されます:

1. **`polyhedron.grh`** (TdZdd graph input)
   - Location: `data/polyhedra/<class>/<name>/polyhedron.grh`
   - Format: No header, 0-indexed vertices, min-max normalized
   - Each line: `v1 v2` (space-separated)
   - Edges in edge_id order

2. **`unfoldings_edge_sets.jsonl`** (Edge set data)
   - Location: `data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl`
   - Format: JSON Lines
   - Each record: `{"edges": [0, 1, 2, ...]}`
   - Edge IDs sorted in ascending order

---

## Test Cases / テストケース

### johnson/n20 (Elongated pentagonal pyramid / 伸長五角錐)

```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

**Outputs:**
- `polyhedron.grh`: 25 vertices, 45 edges
- `unfoldings_edge_sets.jsonl`: 40 unfoldings, edge count 5-15
- ✓ Tested and validated

**出力:**
- `polyhedron.grh`: 25頂点、45辺
- `unfoldings_edge_sets.jsonl`: 40展開図、辺数5-15
- ✓ テスト・検証済み

### archimedean/s12L (Snub cube / ねじれ立方体)

```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/archimedean/s12L/polyhedron_relabeled.json
```

**Outputs:**
- `polyhedron.grh`: 24 vertices, 60 edges
- `unfoldings_edge_sets.jsonl`: 72 unfoldings, edge count 10
- ✓ Tested and validated

**出力:**
- `polyhedron.grh`: 24頂点、60辺
- `unfoldings_edge_sets.jsonl`: 72展開図、辺数10
- ✓ テスト・検証済み

---

## Verification / 検証

After running Phase 3, verify the outputs:

Phase 3 実行後、出力を確認:

```bash
# Check files exist / ファイルの存在確認
ls -l data/polyhedra/johnson/n20/polyhedron.grh
ls -l data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl

# Check polyhedron.grh format / polyhedron.grh の形式確認
head data/polyhedra/johnson/n20/polyhedron.grh

# Check edge sets format / 辺集合の形式確認
head -1 data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl | python3 -m json.tool
```

---

## Module Structure / モジュール構成

```
python/graph_export/
├── __init__.py                 # Package documentation
├── __main__.py                 # Entry point (python -m graph_export)
├── cli.py                      # Main CLI (Block A + Block B)
├── graph_builder.py            # Vertex reconstruction (Union-Find)
├── grh_generator.py            # .grh file generation
├── edge_set_extractor.py       # Edge set extraction logic
└── README.md                   # This file
```

---

## Block Details / ブロックの詳細

### Block A: Polyhedron Graph Generation

**Algorithm:**
1. Assign virtual vertex IDs: `(face_id, index)` for each face vertex
2. Merge virtual vertices sharing the same edge using Union-Find
3. Map Union-Find representatives to consecutive 0-indexed vertex IDs
4. Normalize edges (min, max order)
5. Output edges in edge_id order (preserves Phase 1 edge labeling)

**アルゴリズム:**
1. 各面の頂点に仮 ID `(face_id, index)` を割り当て
2. Union-Find で同じ辺を共有する仮頂点を統合
3. Union-Find 代表元を連続した 0-indexed 頂点 ID にマッピング
4. 辺を正規化（min, max 順）
5. edge_id 順に辺を出力（Phase 1 の辺ラベル付けを保持）

### Block B: Edge Set Extraction

**Algorithm:**
1. Read `faces[]` array from each unfolding record
2. Collect all `edge_id` values (skip first face, which has no edge_id)
3. Remove duplicates using set
4. Sort in ascending order
5. Output as `{"edges": [...]}`

**アルゴリズム:**
1. 各展開図レコードから `faces[]` 配列を読み込み
2. 全ての `edge_id` 値を収集（最初の面はスキップ、edge_id なし）
3. 集合を使って重複除去
4. 昇順ソート
5. `{"edges": [...]}` として出力

---

## Output Formats / 出力形式

### polyhedron.grh Format

```
0 1
0 2
1 2
```

- No header line / ヘッダー行なし
- Each line: two integers (0-indexed vertices) / 各行: 2つの整数（0-indexed 頂点）
- Edges in edge_id order / 辺は edge_id 順
- Vertices normalized (min, max) / 頂点は正規化済み（min, max）

### unfoldings_edge_sets.jsonl Format

```jsonl
{"edges": [0, 3, 5, 9, 12]}
{"edges": [1, 2, 4, 7, 10]}
```

- JSON Lines format / JSON Lines 形式
- Each line: one unfolding's edge set / 各行: 1つの展開図の辺集合
- Edges sorted in ascending order / 辺は昇順ソート
- No geometric or overlap information / 幾何情報や重なり情報なし

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

## Implementation Status / 実装状況

### ✅ Complete / 完了

Phase 3 (Block A + Block B) has been fully implemented and tested.

Phase 3（Block A + Block B）は完全に実装され、テスト済みです。

**Test Results / テスト結果:**
- ✓ johnson/n20: 25V, 45E → 40 unfoldings
- ✓ archimedean/s12L: 24V, 60E → 72 unfoldings

---

## Related Documentation / 関連ドキュメント

- Phase 2 specification: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- Implementation plan: `.cursor/plans/PHASE3_GRAPH_CONVERSION_IMPLEMENTATION_PLAN.md`
- TdZdd Graph API: `lib/tdzdd/include/tdzdd/util/Graph.hpp`
