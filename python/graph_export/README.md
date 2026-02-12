# graph_export — Polyhedron Graph Export for TdZdd

## Overview / 概要

Generates `.grh` files from polyhedron data for TdZdd input.

多面体データから TdZdd 入力用の `.grh` ファイルを生成します。

## Purpose / 目的

- Read `polyhedron_relabeled.json` (Phase 1 output)
- Extract edge-face adjacency information
- Reconstruct vertices using Union-Find algorithm
- Generate `.grh` file in TdZdd-compatible format

- `polyhedron_relabeled.json`（Phase 1 出力）を読み込み
- 辺-面隣接情報を抽出
- Union-Find アルゴリズムで頂点を再構成
- TdZdd 互換形式で `.grh` ファイルを生成

## Input / 入力

**`polyhedron_relabeled.json`** (Phase 1 output)
- Location: `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`
- Schema version: 1
- Contains face adjacency with edge IDs

**`polyhedron_relabeled.json`**（Phase 1 出力）
- 場所: `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`
- スキーマバージョン: 1
- 辺 ID を含む面の隣接情報

## Output / 出力

**`polyhedron.grh`** (TdZdd graph input)
- Location: `data/polyhedra/<class>/<name>/polyhedron.grh`
- Format: No header, 0-indexed vertices
- Each line: `v1 v2` (space-separated)
- Edges in edge_id order (critical: do not reorder!)

**`polyhedron.grh`**（TdZdd グラフ入力）
- 場所: `data/polyhedra/<class>/<name>/polyhedron.grh`
- 形式: ヘッダーなし、0-indexed 頂点
- 各行: `v1 v2`（空白区切り）
- edge_id 順の辺（重要: 順序変更不可！）

### Example .grh Format / .grh 形式の例

```
0 1
0 2
1 2
```

## Usage / 使い方

### Basic Usage / 基本的な使い方

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

### Test Cases / テストケース

**johnson/n20** (Elongated pentagonal pyramid / 伸長五角錐)
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

Expected output / 期待される出力:
- `data/polyhedra/johnson/n20/polyhedron.grh`
- 25 vertices, 45 edges / 25頂点、45辺
- ✓ Tested and validated / テスト・検証済み

**archimedean/s12L** (Snub cube / ねじれ立方体)
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/archimedean/s12L/polyhedron_relabeled.json
```

Expected output / 期待される出力:
- `data/polyhedra/archimedean/s12L/polyhedron.grh`
- 24 vertices, 60 edges / 24頂点、60辺
- ✓ Tested and validated / テスト・検証済み

## Verification / 検証

After running, verify the output:

実行後、出力を確認:

```bash
# Check file exists / ファイルの存在確認
ls -l data/polyhedra/johnson/n20/polyhedron.grh

# Check line count (should equal number of edges) / 行数確認（辺数と一致すべき）
wc -l data/polyhedra/johnson/n20/polyhedron.grh

# View first few lines / 最初の数行を表示
head data/polyhedra/johnson/n20/polyhedron.grh
```

Expected format / 期待される形式:
- Each line has exactly two integers / 各行に正確に2つの整数
- Integers are 0-indexed / 整数は 0-indexed
- No header line / ヘッダー行なし

## Algorithm / アルゴリズム

### Vertex Reconstruction / 頂点再構成

Uses Union-Find to identify vertices from edge adjacency:

Union-Find を用いて辺の隣接関係から頂点を識別:

1. Each edge has 2 endpoints (endpoint_id = 2*edge_id, 2*edge_id+1)
2. For each face, consecutive edges share a vertex
3. Union-Find merges endpoint sets that represent the same vertex
4. Assign vertex IDs based on Union-Find root representatives

1. 各辺は 2 つの端点を持つ（endpoint_id = 2*edge_id, 2*edge_id+1）
2. 各面で、連続する辺は頂点を共有
3. Union-Find で同じ頂点を表す端点集合を統合
4. Union-Find のルート代表に基づいて頂点 ID を割り当て

### Edge Ordering / 辺の順序

**Critical constraint / 重要な制約:**

Edges MUST be output in edge_id order (0, 1, 2, ...).
Do NOT reorder by vertex IDs.

辺は edge_id 順（0, 1, 2, ...）で出力しなければなりません。
頂点 ID でソートしてはいけません。

This preserves the edge labeling from Phase 1, which is essential for Phase 4 (ZDD construction).

これにより Phase 1 の辺ラベル付けが保持され、Phase 4（ZDD 構築）に不可欠です。

## Scope / 範囲

This module handles:
- Graph structure extraction
- `.grh` file generation

このモジュールが扱うもの:
- グラフ構造抽出
- `.grh` ファイル生成

This module does NOT handle:
- Unfolding data (handled by other phases)
- ZDD construction (Phase 4)
- Decompose/pathwidth optimization

このモジュールが扱わないもの:
- 展開図データ（他のフェーズが担当）
- ZDD 構築（Phase 4）
- Decompose/幅優先最適化

## Implementation Status / 実装状況

### ✅ Complete / 完了

This module has been fully implemented and tested.

このモジュールは完全に実装され、テスト済みです。

**Test Results / テスト結果:**
- ✓ johnson/n20: 25 vertices, 45 edges (format validated)
- ✓ archimedean/s12L: 24 vertices, 60 edges (format validated)

**Files Created / 作成ファイル:**
```
python/graph_export/
├── __init__.py         # Package documentation
├── __main__.py         # Entry point
├── cli.py              # CLI implementation
├── graph_builder.py    # Vertex reconstruction (Union-Find)
├── grh_generator.py    # .grh file generation
└── README.md           # This file
```

### Module Structure / モジュール構成

```
python/graph_export/
├── __init__.py              # パッケージドキュメント
├── __main__.py              # python -m のエントリーポイント
├── cli.py                   # CLI 実装（引数解析、パス解決）
├── graph_builder.py         # Union-Find による頂点再構成
├── grh_generator.py         # .grh ファイル生成
└── README.md                # 本ファイル
```

### Key Implementation Details / 主要な実装詳細

**Algorithm / アルゴリズム:**
1. Assign virtual vertex IDs: `(face_id, index)` for each face vertex
2. Merge virtual vertices sharing the same edge using Union-Find
3. Map Union-Find representatives to consecutive 0-indexed vertex IDs
4. Output edges in edge_id order (preserves Phase 1 edge labeling)

**アルゴリズム:**
1. 各面の頂点に仮 ID `(face_id, index)` を割り当て
2. Union-Find で同じ辺を共有する仮頂点を統合
3. Union-Find 代表元を連続した 0-indexed 頂点 ID にマッピング
4. edge_id 順に辺を出力（Phase 1 の辺ラベル付けを保持）

**Critical Constraint / 重要な制約:**
- Edge ordering MUST be preserved (edge_id 0, 1, 2, ...)
- Do NOT reorder edges by vertex IDs
- This is essential for Phase 4 (ZDD construction)

**重要な制約:**
- 辺の順序は必ず保持（edge_id 0, 1, 2, ...）
- 頂点 ID で辺をソートしてはいけない
- Phase 4（ZDD 構築）に不可欠

## Related Documentation / 関連ドキュメント

- Implementation plan: `.cursor/plans/PHASE3_GRAPH_CONVERSION_IMPLEMENTATION_PLAN.md`
- TdZdd graph format: `lib/tdzdd/include/tdzdd/util/Graph.hpp`
- Phase 1 reference: `python/edge_relabeling/graph_builder.py`
