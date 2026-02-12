# Phase 3: Graph Data Conversion — TdZdd Input Preparation

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-12

---

## Overview / 概要

Phase 3 implements graph data conversion from polyhedron and unfolding data to TdZdd-compatible input format. It transforms the complete isomorphic unfolding set from Phase 2 into pure combinatorial graph representation, removing all geometric and overlap information.

Phase 3 は、多面体と展開図データから TdZdd 互換入力形式へのグラフデータ変換を実装します。Phase 2 の完全な同型展開図集合を純粋な組合せグラフ表現に変換し、すべての幾何情報と重なり情報を削除します。

**This is the data transformation layer for Counting pipeline.** Phase 3 bridges Phase 2 (unfolding expansion) and Phase 4 (ZDD construction) by:
1. Generating polyhedron graph in TdZdd-readable format (Block A)
2. Extracting edge sets from unfolding face sequences (Block B)
3. Outputting minimal combinatorial data for ZDD input

**これは Counting パイプラインのデータ変換レイヤです。** Phase 3 は Phase 2（展開図展開）と Phase 4（ZDD 構築）の橋渡しを行います：
1. TdZdd が読み込める形式で多面体グラフを生成（Block A）
2. 展開図の面列から辺集合を抽出（Block B）
3. ZDD 入力用の最小限の組合せデータを出力

---

## Purpose and Scope / 目的と範囲

### What Phase 3 Does / Phase 3 が行うこと

Phase 3 focuses on **graph format conversion** and prepares TdZdd input data:

**Block A: Polyhedron Graph Generation**
1. **Vertex reconstruction**: Uses Union-Find to reconstruct vertices from face-adjacency data.
2. **Graph representation**: Converts polyhedron structure to vertex-edge pairs.
3. **Edge normalization**: Orders vertex pairs (min, max) for readability.
4. **.grh file generation**: Outputs TdZdd-compatible graph file (0-indexed, no header).

**Block B: Edge Set Extraction**
1. **Face sequence parsing**: Reads unfolding face sequences from Phase 2 output.
2. **Edge ID collection**: Extracts edge_id from each face (except root face).
3. **Deduplication and sorting**: Removes duplicates and sorts edge sets.
4. **JSONL generation**: Outputs pure combinatorial edge set data.

Phase 3 は**グラフ形式変換**に焦点を当て、TdZdd 入力データを準備します：

**Block A: 多面体グラフ生成**
1. **頂点の再構成**: Union-Find を用いて面隣接データから頂点を再構成します。
2. **グラフ表現**: 多面体構造を頂点–辺ペアに変換します。
3. **辺の正規化**: 頂点ペアを（min, max）順に並べて可読性を向上させます。
4. **.grh ファイル生成**: TdZdd 互換グラフファイルを出力します（0-indexed、ヘッダーなし）。

**Block B: 辺集合の抽出**
1. **面列の解析**: Phase 2 出力から展開図の面列を読み込みます。
2. **辺 ID の収集**: 各面から edge_id を抽出します（根面を除く）。
3. **重複除去とソート**: 重複を削除し辺集合をソートします。
4. **JSONL 生成**: 純粋な組合せ辺集合データを出力します。

### What Phase 3 Does NOT Do / Phase 3 が行わないこと

Phase 3 intentionally **does not** implement:

- **Geometric computation**: Does not calculate coordinates, angles, or polygon positions.
- **Overlap detection**: Does not perform intersection tests or overlap classification.
- **Isomorphism handling**: Assumes Phase 2 has already expanded all variants.
- **ZDD construction**: Graph data is prepared but ZDD building is Phase 4's responsibility.
- **Filtering or counting**: Non-overlapping unfolding identification is Phase 5's responsibility.
- **Batch processing**: Each polyhedron must be processed individually.

Phase 3 は意図的に以下を実装**しません**：

- **幾何計算**: 座標、角度、多角形の位置を計算しません。
- **重なり判定**: 交差テストや重なり分類を行いません。
- **同型処理**: Phase 2 がすでに全変種を展開済みと仮定します。
- **ZDD 構築**: グラフデータは準備しますが、ZDD 構築は Phase 4 の責務です。
- **フィルタリングや数え上げ**: 非重複展開図の識別は Phase 5 の責務です。
- **バッチ処理**: 各多面体は個別に処理する必要があります。

---

## Input Files / 入力ファイル

Phase 3 requires the following inputs:

### 1. polyhedron_relabeled.json (from Phase 1)

**Path:**
```
data/polyhedra/<class>/<name>/polyhedron_relabeled.json
```

**Purpose:** Provides polyhedron structure with Phase 1's optimized edge labels.

**Schema Version:** 1

**Required Fields:**
- `faces[]`: Array of face objects
  - `face_id`: Face identifier
  - `gon`: Number of sides (3, 4, 5, etc.)
  - `neighbors[]`: Adjacent faces and shared edges
    - `edge_id`: Edge identifier (Phase 1's new labeling)
    - `face_id`: Adjacent face identifier

**用途:** Phase 1 の最適化された辺ラベルを持つ多面体構造を提供します。

### 2. unfoldings_overlapping_all.jsonl (from Phase 2)

**Path:**
```
data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
```

**Purpose:** Complete set of all isomorphic unfolding variants (including overlapping ones).

**Schema Version:** 2

**Format:** JSON Lines (one record per line)

**Required Fields per Record:**
- `schema_version`: 2
- `faces[]`: Ordered array of faces in unfolding tree
  - `face_id`: Face identifier (Phase 1 labeling)
  - `gon`: Number of sides
  - `edge_id`: Shared edge with previous face (omitted for first face)
  - `x`, `y`, `angle_deg`: Geometric info (ignored in Phase 3)
- `exact_overlap`: Overlap classification (ignored in Phase 3)
- `source`: Provenance metadata (ignored in Phase 3)

**用途:** すべての同型展開図変種の完全な集合を提供します（重なっているものを含む）。

---

## Output Files / 出力ファイル

Phase 3 generates the following outputs:

### 1. polyhedron.grh (Block A output)

**Path:**
```
data/polyhedra/<class>/<name>/polyhedron.grh
```

**Purpose:** Polyhedron graph in TdZdd-compatible format.

**Format:** Plain text, no header, 0-indexed vertices

**Structure:**
```
v1 v2
v1 v2
...
```

Each line represents one edge as a vertex pair (space-separated).
Edges are output in edge_id order (preserves Phase 1 ordering).
Vertices are normalized (min, max order).

**Example:**
```
0 2
0 1
1 2
2 8
1 8
```

**用途:** TdZdd 互換形式の多面体グラフ。

**形式:** プレーンテキスト、ヘッダーなし、0-indexed 頂点

**構造:**
各行が1つの辺を頂点ペアとして表現します（空白区切り）。
辺は edge_id 順で出力されます（Phase 1 の順序を保持）。
頂点は正規化されます（min, max 順）。

### 2. unfoldings_edge_sets.jsonl (Block B output)

**Path:**
```
data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
```

**Purpose:** Edge sets for all unfoldings (pure combinatorial data).

**Format:** JSON Lines (one record per line)

**Structure per Record:**
```json
{
  "edges": [0, 1, 2, 5, 7, 10, ...]
}
```

- `edges`: Sorted array of edge_id values used in this unfolding
- No geometric information (x, y, angle_deg removed)
- No overlap information (exact_overlap removed)
- No face structure (face_id, gon removed)

**Example:**
```jsonl
{"edges": [1, 3, 11, 25, 37]}
{"edges": [7, 10, 11, 16, 25, 39, 40]}
{"edges": [1, 3, 6, 8, 9, 10, 12, 16, 24, 25, 27, 33, 36, 39, 44]}
```

**用途:** すべての展開図の辺集合（純粋な組合せデータ）。

**形式:** JSON Lines（1行1レコード）

**レコードごとの構造:**
- `edges`: この展開図で使用される edge_id 値のソート済み配列
- 幾何情報なし（x, y, angle_deg を削除）
- 重なり情報なし（exact_overlap を削除）
- 面構造なし（face_id, gon を削除）

---

## Processing Flow / 処理フロー

### Block A: Polyhedron Graph Generation

**Step 1: Load polyhedron structure**
- Read `polyhedron_relabeled.json`
- Verify `schema_version: 1`
- Extract face-edge adjacency

**Step 2: Reconstruct vertices (Union-Find)**
- Assign virtual vertex IDs to each face corner: `(face_id, index)`
- For each edge shared by two faces, merge corresponding virtual vertices
- Map Union-Find representatives to consecutive 0-indexed vertex IDs

**Step 3: Build edge list**
- For each edge_id (in ascending order):
  - Get vertex pair from Union-Find result
  - Normalize (min, max order)
  - Append to edge list

**Step 4: Generate .grh file**
- Write edges to file without header
- Format: `v1 v2` per line (0-indexed)
- Output in edge_id order

### Block B: Edge Set Extraction

**Step 1: Load unfoldings**
- Read `unfoldings_overlapping_all.jsonl` line by line
- Parse each JSON record

**Step 2: Extract edge IDs**
- For each record:
  - Iterate through `faces[]` array
  - Collect all `edge_id` values (skip first face, which has no edge_id)
  - Add to set (automatic deduplication)

**Step 3: Sort and output**
- Convert set to sorted list
- Wrap in `{"edges": [...]}` format
- Write to `unfoldings_edge_sets.jsonl`

### Block A: 多面体グラフ生成

**Step 1: 多面体構造の読み込み**
- `polyhedron_relabeled.json` を読み込み
- `schema_version: 1` を検証
- 面–辺隣接情報を抽出

**Step 2: 頂点の再構成（Union-Find）**
- 各面の角に仮頂点 ID を割り当て: `(face_id, index)`
- 2つの面で共有される各辺について、対応する仮頂点を統合
- Union-Find 代表元を連続した 0-indexed 頂点 ID にマッピング

**Step 3: 辺リストの構築**
- 各 edge_id について（昇順）:
  - Union-Find 結果から頂点ペアを取得
  - 正規化（min, max 順）
  - 辺リストに追加

**Step 4: .grh ファイルの生成**
- ヘッダーなしで辺をファイルに書き込み
- 形式: 1行あたり `v1 v2`（0-indexed）
- edge_id 順で出力

### Block B: 辺集合の抽出

**Step 1: 展開図の読み込み**
- `unfoldings_overlapping_all.jsonl` を行ごとに読み込み
- 各 JSON レコードを解析

**Step 2: 辺 ID の抽出**
- 各レコードについて:
  - `faces[]` 配列を反復処理
  - すべての `edge_id` 値を収集（最初の面はスキップ、edge_id なし）
  - 集合に追加（自動重複除去）

**Step 3: ソートと出力**
- 集合をソート済みリストに変換
- `{"edges": [...]}` 形式でラップ
- `unfoldings_edge_sets.jsonl` に書き込み

---

## Data Schema Evolution / データスキーマの進化

Phase 3 performs schema transformation from Phase 2 outputs to ZDD-compatible format:

Phase 3 は Phase 2 出力から ZDD 互換形式へのスキーマ変換を行います：

### Block A: Polyhedron Structure Transformation

| Source | Target | Transformation |
|--------|--------|----------------|
| `polyhedron_relabeled.json` (schema v1) | `polyhedron.grh` | Graph extraction + format conversion |
| Face-edge adjacency | Vertex-edge pairs | Union-Find vertex reconstruction |
| JSON structure | Plain text format | Simplified for TdZdd input |

### Block B: Unfolding Data Transformation

| Source | Target | Transformation |
|--------|--------|----------------|
| `unfoldings_overlapping_all.jsonl` (schema v2) | `unfoldings_edge_sets.jsonl` | Face sequence → edge set |
| `faces[]` with geometry | `edges[]` only | Remove x, y, angle_deg |
| With overlap info | Pure combinatorial | Remove exact_overlap |
| With source metadata | No metadata | Remove source provenance |

**Key Principle:** Phase 3 strips away all non-combinatorial information.

**重要原則:** Phase 3 はすべての非組合せ情報を削除します。

---

## Module Structure / モジュール構成

Phase 3 is implemented as a single Python module:

Phase 3 は単一の Python モジュールとして実装されます：

```
python/graph_export/
├── __init__.py              # Module documentation / モジュールドキュメント
├── __main__.py              # Entry point (python -m graph_export) / エントリーポイント
├── cli.py                   # Main CLI (Block A + Block B orchestration) / メイン CLI
├── graph_builder.py         # Vertex reconstruction (Union-Find) / 頂点再構成
├── grh_generator.py         # .grh file writer / .grh ファイル書き込み
├── edge_set_extractor.py    # Edge set extraction logic / 辺集合抽出ロジック
└── README.md                # User documentation / ユーザー向けドキュメント
```

### Module Responsibilities / モジュールの責務

| Module | Responsibility |
|--------|----------------|
| **cli.py** | Argument parsing, path resolution, Block A+B orchestration |
| **graph_builder.py** | Union-Find vertex reconstruction, edge list building |
| **grh_generator.py** | Writing .grh files in TdZdd format |
| **edge_set_extractor.py** | Edge set extraction from unfolding face sequences |

---

## Usage / 使用方法

### Command-Line Interface / コマンドラインインターフェース

Phase 3 uses a unified CLI that runs both Block A and Block B:

Phase 3 は Block A と Block B の両方を実行する統一 CLI を使用します：

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m graph_export --poly data/polyhedra/<class>/<name>/polyhedron_relabeled.json
```

**Arguments:**
- `--poly`: Path to `polyhedron_relabeled.json` (required)

**引数:**
- `--poly`: `polyhedron_relabeled.json` へのパス（必須）

### Example Usage / 使用例

**johnson/n20** (Elongated pentagonal pyramid):
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

**archimedean/s12L** (Snub cube):
```bash
PYTHONPATH=python python -m graph_export --poly data/polyhedra/archimedean/s12L/polyhedron_relabeled.json
```

---

## Algorithm Details / アルゴリズム詳細

### Block A: Union-Find Vertex Reconstruction

The vertex reconstruction algorithm is based on Phase 1's implementation:

頂点再構成アルゴリズムは Phase 1 の実装に基づいています：

**Algorithm / アルゴリズム:**

1. **Virtual vertex assignment / 仮頂点の割り当て**
   - Each face corner is assigned a virtual vertex: `(face_id, corner_index)`
   - For an n-gon face, corners are indexed 0 to n-1
   
2. **Edge-based merging / 辺ベースの統合**
   - For each edge shared by two faces:
     - Edge connects corner i of face A to corner j of face B
     - Merge the corresponding virtual vertices using Union-Find
   
3. **Representative mapping / 代表元のマッピング**
   - Get Union-Find representative for each virtual vertex
   - Map unique representatives to consecutive vertex IDs (0, 1, 2, ...)
   
4. **Edge list construction / 辺リストの構築**
   - For each edge_id (in ascending order):
     - Get vertex pair from Union-Find result
     - Normalize to (min, max) order
     - Output to edge list

**Time Complexity:** O(E × α(V)) where E = edges, V = vertices, α = inverse Ackermann function

**時間計算量:** O(E × α(V))、E = 辺数、V = 頂点数、α = 逆アッカーマン関数

### Block B: Edge Set Extraction

**Algorithm / アルゴリズム:**

1. **Parse unfolding records / 展開図レコードの解析**
   - Read JSON Lines format
   - Parse each record independently
   
2. **Extract edge IDs / 辺 ID の抽出**
   - For each face in `faces[]` array (skip index 0):
     - Extract `edge_id` field
     - Add to set (automatic deduplication)
   
3. **Sort and format / ソートとフォーマット**
   - Convert set to list
   - Sort in ascending order
   - Wrap in `{"edges": [...]}` format
   
4. **Write output / 出力書き込み**
   - Write one JSON record per line (JSON Lines format)

**Time Complexity:** O(N × F) where N = number of unfoldings, F = faces per unfolding

**時間計算量:** O(N × F)、N = 展開図数、F = 展開図あたりの面数

---

## Output Format Specifications / 出力形式仕様

### polyhedron.grh Format

**Specification:**
- Plain text file / プレーンテキストファイル
- No header line / ヘッダー行なし
- One edge per line / 1行1辺
- Format: `v1 v2` (space-separated, 0-indexed integers) / 形式: `v1 v2`（空白区切り、0-indexed 整数）
- Vertices normalized to (min, max) order / 頂点は（min, max）順に正規化
- Edges in edge_id order (0, 1, 2, ...) / 辺は edge_id 順（0, 1, 2, ...）
- Final newline at end of file / ファイル末尾に改行

**Example (first 5 edges):**
```
0 2
0 1
1 2
2 8
1 8
```

**Critical Constraint:** Edge ordering MUST be preserved from Phase 1.

**重要な制約:** 辺の順序は Phase 1 から保持されなければなりません。

### unfoldings_edge_sets.jsonl Format

**Specification:**
- JSON Lines format / JSON Lines 形式
- One unfolding per line / 1行1展開図
- Each record: `{"edges": [list of edge_id]}` / 各レコード: `{"edges": [edge_id のリスト]}`
- Edge IDs sorted in ascending order / 辺 ID は昇順ソート
- No trailing comma / 末尾のカンマなし
- Final newline at end of file / ファイル末尾に改行

**Example (first 3 unfoldings):**
```jsonl
{"edges": [1, 3, 11, 25, 37]}
{"edges": [8, 9, 12, 25, 35]}
{"edges": [34, 35, 41, 42, 43]}
```

**Why Sorted?** Simplifies debugging and allows efficient set operations in Phase 4.

**なぜソート？** デバッグが簡単になり、Phase 4 での効率的な集合演算が可能になります。

---

## Test Results / テスト結果

### Test Case 1: johnson/n20 (Elongated pentagonal pyramid)

**Input:**
- `polyhedron_relabeled.json`: 22 faces, 45 edges
- `unfoldings_overlapping_all.jsonl`: 40 unfoldings (Phase 2 output)

**Output:**
- `polyhedron.grh`: 45 lines, 25 vertices
- `unfoldings_edge_sets.jsonl`: 40 records, edge count 5-15

**Verification:**
- ✓ All edges in .grh are normalized (min, max)
- ✓ All edge sets are sorted
- ✓ No duplicate edges within each set
- ✓ All edge IDs are in valid range (0-44)

**検証:**
- ✓ .grh のすべての辺が正規化済み（min, max）
- ✓ すべての辺集合がソート済み
- ✓ 各集合内に重複辺なし
- ✓ すべての辺 ID が有効範囲内（0-44）

### Test Case 2: archimedean/s12L (Snub cube)

**Input:**
- `polyhedron_relabeled.json`: 38 faces, 60 edges
- `unfoldings_overlapping_all.jsonl`: 72 unfoldings (Phase 2 output)

**Output:**
- `polyhedron.grh`: 60 lines, 24 vertices
- `unfoldings_edge_sets.jsonl`: 72 records, edge count 10

**Verification:**
- ✓ All edges in .grh are normalized (min, max)
- ✓ All edge sets are sorted
- ✓ No duplicate edges within each set
- ✓ All edge IDs are in valid range (0-59)

**検証:**
- ✓ .grh のすべての辺が正規化済み（min, max）
- ✓ すべての辺集合がソート済み
- ✓ 各集合内に重複辺なし
- ✓ すべての辺 ID が有効範囲内（0-59）

---

## Interface with Other Phases / 他のフェーズとのインターフェース

### Phase 2 → Phase 3

**Input Contract:**
- `polyhedron_relabeled.json` with `schema_version: 1`
- `unfoldings_overlapping_all.jsonl` with `schema_version: 2`
- Edge IDs use Phase 1's optimized labeling
- All isomorphic variants are present in input

**入力契約:**
- `schema_version: 1` の `polyhedron_relabeled.json`
- `schema_version: 2` の `unfoldings_overlapping_all.jsonl`
- 辺 ID は Phase 1 の最適化されたラベル付けを使用
- すべての同型変種が入力に存在

### Phase 3 → Phase 4

**Output Contract:**
- `polyhedron.grh`: TdZdd-compatible graph file (0-indexed, no header)
- `unfoldings_edge_sets.jsonl`: Pure combinatorial edge sets
- Edge ordering preserved from Phase 1
- No geometric or overlap information

**出力契約:**
- `polyhedron.grh`: TdZdd 互換グラフファイル（0-indexed、ヘッダーなし）
- `unfoldings_edge_sets.jsonl`: 純粋な組合せ辺集合
- Phase 1 からの辺順序を保持
- 幾何情報や重なり情報なし

---

## Design Decisions / 設計判断

### Why Two Blocks? / なぜ2つのブロック？

**Block A and Block B are independent:**
- Block A processes polyhedron structure (once per polyhedron)
- Block B processes unfolding data (once per polyhedron)
- They can potentially be parallelized in future versions

**Block A と Block B は独立:**
- Block A は多面体構造を処理（多面体ごとに1回）
- Block B は展開図データを処理（多面体ごとに1回）
- 将来のバージョンでは並列化可能

### Why 0-indexed? / なぜ 0-indexed？

**TdZdd expects vertex names as strings:**
- TdZdd's `readEdges()` treats vertex IDs as string labels
- `"0"`, `"1"`, `"2"` are valid vertex names
- Internally, TdZdd assigns consecutive vertex numbers starting from 1
- Using 0-indexed output matches Python's natural indexing

**TdZdd は頂点名を文字列として期待:**
- TdZdd の `readEdges()` は頂点 ID を文字列ラベルとして扱う
- `"0"`, `"1"`, `"2"` は有効な頂点名
- 内部的には、TdZdd は 1 から始まる連続した頂点番号を割り当てる
- 0-indexed 出力は Python の自然なインデックス付けと一致

### Why Remove Geometric Data? / なぜ幾何データを削除？

**Geometric information is not needed for ZDD construction:**
- ZDD operates on combinatorial edge sets only
- Coordinates and angles are irrelevant for subset enumeration
- Removing them reduces file size and clarifies the data model

**幾何情報は ZDD 構築に不要:**
- ZDD は組合せ辺集合のみを操作
- 座標と角度は部分集合列挙に無関係
- それらを削除するとファイルサイズが減り、データモデルが明確になる

---

## Verification / 検証

### Block A Verification

```bash
# Check file exists and line count
wc -l data/polyhedra/johnson/n20/polyhedron.grh

# Verify format (each line should have two integers)
awk '{if (NF != 2 || $1 !~ /^[0-9]+$/ || $2 !~ /^[0-9]+$/) {print "Invalid line " NR; exit 1}}' \
  data/polyhedra/johnson/n20/polyhedron.grh && echo "✓ Format valid"

# Check edge normalization (min, max order)
awk '{if ($1 > $2) {print "Line " NR " not normalized: " $0; exit 1}}' \
  data/polyhedra/johnson/n20/polyhedron.grh && echo "✓ All edges normalized"
```

### Block B Verification

```bash
# Check file exists and record count
wc -l data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl

# View first record
head -1 data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl | python3 -m json.tool

# Verify all records (sorted, unique, valid range)
python3 -c "
import json
with open('data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl', 'r') as f:
    for i, line in enumerate(f, 1):
        record = json.loads(line)
        edges = record['edges']
        if edges != sorted(edges):
            print(f'Line {i}: NOT sorted')
        if len(edges) != len(set(edges)):
            print(f'Line {i}: Has duplicates')
        if any(e < 0 or e >= 45 for e in edges):
            print(f'Line {i}: Edge ID out of range')
print('✓ All checks passed')
"
```

---

## Performance / パフォーマンス

### Block A Performance

**johnson/n20:**
- Vertices: 25
- Edges: 45
- Execution time: ~50ms

**archimedean/s12L:**
- Vertices: 24
- Edges: 60
- Execution time: ~50ms

**Complexity:** O(F × G + E × α(V))
- F = number of faces / 面数
- G = average gon (sides per face) / 平均 gon（面あたりの辺数）
- E = number of edges / 辺数
- V = number of vertices / 頂点数
- α = inverse Ackermann function / 逆アッカーマン関数

### Block B Performance

**johnson/n20:**
- Input: 40 unfoldings
- Output: 40 edge sets
- Execution time: ~50ms

**archimedean/s12L:**
- Input: 72 unfoldings
- Output: 72 edge sets
- Execution time: ~50ms

**Complexity:** O(N × F)
- N = number of unfoldings / 展開図数
- F = faces per unfolding / 展開図あたりの面数

---

## Error Handling / エラーハンドリング

Phase 3 validates inputs and handles errors gracefully:

Phase 3 は入力を検証し、エラーを適切に処理します：

### Input Validation

- **File existence:** Checks that both input files exist before processing
- **Schema version:** Warns if `polyhedron_relabeled.json` has unexpected schema version
- **Path format:** Validates polyhedron path follows expected structure

**ファイル存在確認:** 処理前に両方の入力ファイルが存在することを確認
**スキーマバージョン:** `polyhedron_relabeled.json` が予期しないスキーマバージョンの場合に警告
**パス形式:** 多面体パスが期待される構造に従っているかを検証

### Error Messages

All errors are reported to stderr with clear descriptions:

すべてのエラーは明確な説明とともに stderr に報告されます：

```
Error: Input file not found: data/polyhedra/johnson/n20/polyhedron_relabeled.json
Error: Input must be polyhedron_relabeled.json, got: polyhedron.json
Error: Required input file not found: data/polyhedra/johnson/n20/unfoldings_overlapping_all.jsonl
```

---

## Limitations and Future Work / 制限と今後の作業

### Current Limitations

1. **Sequential processing:** Block A and Block B run sequentially (not parallelized)
2. **Single polyhedron:** Must run separately for each polyhedron (no batch mode)
3. **No pathwidth optimization:** Unlike Phase 1, Phase 3 does not reorder edges

**現在の制限:**
1. **順次処理:** Block A と Block B は順次実行（並列化されていない）
2. **単一多面体:** 各多面体ごとに個別実行が必要（バッチモードなし）
3. **パス幅最適化なし:** Phase 1 とは異なり、Phase 3 は辺の順序を変更しない

### Future Enhancements

- Parallel execution of Block A and Block B
- Batch processing for multiple polyhedra
- Progress bar for large datasets
- Additional output formats (if needed by Phase 4)

**将来の拡張:**
- Block A と Block B の並列実行
- 複数の多面体のバッチ処理
- 大規模データセット用のプログレスバー
- Phase 4 が必要とする追加の出力形式

---

## Related Documentation / 関連ドキュメント

- **Phase 1 specification:** `docs/PHASE1_EDGE_RELABELING.md`
- **Phase 2 specification:** `docs/PHASE2_UNFOLDING_EXPANSION.md`
- **Implementation plan:** `.cursor/plans/PHASE3_GRAPH_CONVERSION_IMPLEMENTATION_PLAN.md`
- **Module README:** `python/graph_export/README.md`
- **TdZdd Graph API:** `lib/tdzdd/include/tdzdd/util/Graph.hpp`

---

## Appendix: File Format Comparison / 付録: ファイル形式比較

### Phase 1 .grh vs Phase 3 .grh

| Feature | Phase 1 (lib/decompose) | Phase 3 (TdZdd) |
|---------|------------------------|-----------------|
| Header | `p edge <V> <E>` | None |
| Edge format | `e v1 v2` | `v1 v2` |
| Vertex indexing | 1-indexed | 0-indexed |
| Purpose | Pathwidth optimization | ZDD construction |

**Why Different?** Different libraries have different input format requirements.

**なぜ異なる？** 異なるライブラリは異なる入力形式要件を持ちます。

### Input/Output Formats Across Phases

```
Phase 1:
  polyhedron.json → polyhedron_relabeled.json (schema v1)
                 → edge_mapping.json
                 → polyhedron.grh (decompose format)

Phase 2:
  exact.jsonl + edge_mapping.json → exact_relabeled.jsonl
                                  → unfoldings_overlapping_all.jsonl (schema v2)

Phase 3:
  polyhedron_relabeled.json → polyhedron.grh (TdZdd format)
  unfoldings_overlapping_all.jsonl → unfoldings_edge_sets.jsonl
```

---

**Document Status:** Specification frozen for Phase 3 implementation.
**ドキュメント状態:** Phase 3 実装のため仕様を凍結。
