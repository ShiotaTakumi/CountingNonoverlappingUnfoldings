# Phase 1: Edge Relabeling — Pathwidth-Optimized Edge Label Assignment

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-11

---

## Overview / 概要

Phase 1 implements edge label reassignment for polyhedron data based on pathwidth optimization. It transforms the edge labeling system used in Rotational Unfolding to a new optimized ordering suitable for efficient ZDD construction in later phases.

Phase 1 は、パス幅最適化に基づく多面体データの辺ラベル貼り替えを実装します。Rotational Unfolding で使用されている辺ラベル体系を、後続フェーズでの効率的な ZDD 構築に適した新しい最適化順序に変換します。

**This is the preprocessing foundation for Counting pipeline.** Phase 1 establishes the edge labeling contract that all subsequent phases (Phase 2: Relabeling and Isomorphism Expansion, Phase 3: Graph Data Conversion, Phase 4: ZDD Construction, Phase 5: Filtering) depend on. The specification defined in this document is frozen and serves as the basis for the entire counting pipeline.

**これは Counting パイプラインの前処理基盤です。** Phase 1 は、すべての後続フェーズ（Phase 2: 辺ラベル貼り替えと同型展開、Phase 3: グラフデータ変換、Phase 4: ZDD 構築、Phase 5: フィルタリング）が依存する辺ラベル契約を確立します。本文書で定義される仕様は凍結されており、カウンティングパイプライン全体の基礎として機能します。

---

## Purpose and Scope / 目的と範囲

### What Phase 1 Does / Phase 1 が行うこと

Phase 1 focuses on **edge label transformation** via pathwidth optimization and defines the canonical edge labeling for the Counting pipeline:

1. **Vertex reconstruction**: Implicit vertices are reconstructed from face-adjacency data using Union-Find algorithm.
2. **Graph representation**: Polyhedron structure is converted to `.grh` format (vertex-edge graph).
3. **Pathwidth optimization**: `lib/decompose` (external black-box program) reorders edges to minimize pathwidth.
4. **Edge mapping extraction**: Old edge IDs are mapped to new edge IDs based on vertex pairs.
5. **Polyhedron relabeling**: `polyhedron.json` is updated with the new edge labeling system.

Phase 1 は**辺ラベル変換**にパス幅最適化を用いることに焦点を当て、Counting パイプラインのための正規の辺ラベル体系を定義します：

1. **頂点の再構成**: 面隣接データから Union-Find アルゴリズムを用いて暗黙的な頂点を再構成します。
2. **グラフ表現**: 多面体構造を `.grh` 形式（頂点–辺グラフ）に変換します。
3. **パス幅最適化**: `lib/decompose`（外部ブラックボックスプログラム）で辺順序を最適化しパス幅を最小化します。
4. **辺ラベル対応表の抽出**: 頂点ペアに基づき旧辺 ID を新辺 ID にマッピングします。
5. **多面体の辺ラベル貼り替え**: `polyhedron.json` を新しい辺ラベル体系で更新します。

### What Phase 1 Does NOT Do / Phase 1 が行わないこと

Phase 1 intentionally **does not** implement:

- **Unfolding relabeling**: Rotational Unfolding output (`exact.jsonl`) is not processed in Phase 1.
- **Isomorphism expansion**: Non-isomorphic unfoldings are not expanded to include all isomorphic variants.
- **Geometric computation**: No coordinate calculations or polygon intersection tests.
- **ZDD construction**: Graph data is prepared but ZDD building is Phase 4's responsibility.
- **Batch processing**: Each polyhedron must be processed individually.

Phase 1 は意図的に以下を**実装しません**：

- **展開図の辺ラベル貼り替え**: Rotational Unfolding の出力（`exact.jsonl`）は Phase 1 では処理しません。
- **同型展開**: 非同型展開図をすべての同型バリアントを含むように展開しません。
- **幾何計算**: 座標計算や多角形交差テストは行いません。
- **ZDD 構築**: グラフデータは準備しますが、ZDD 構築は Phase 4 の責務です。
- **バッチ処理**: 各多面体は個別に処理する必要があります。

---

## Architecture / アーキテクチャ

Phase 1 uses a hybrid Python-C++ architecture:

Phase 1 は Python-C++ ハイブリッドアーキテクチャを使用します：

```
┌─────────────────────────────────────────┐
│  Python CLI (edge_relabeling)           │
│  - Path resolution                      │
│  - Graph construction (Union-Find)      │
│  - .grh generation                      │
│  - Edge mapping extraction              │
│  - Polyhedron relabeling                │
└─────────────┬───────────────────────────┘
              │ subprocess
              ↓
┌─────────────────────────────────────────┐
│  C++ Core (edge_relabeling binary)      │
│  - Wrapper for lib/decompose            │
│  - Pathwidth optimization               │
│  - Edge reordering                      │
└─────────────────────────────────────────┘
              │ uses (read-only)
              ↓
┌─────────────────────────────────────────┐
│  lib/decompose (external)               │
│  - Path decomposition algorithm         │
│  - Black-box program (cannot modify)    │
└─────────────────────────────────────────┘
```

### Responsibility Separation / 責務分離

| Component | Responsibility |
|-----------|----------------|
| **Python CLI** | Orchestration, file I/O, mapping extraction |
| **C++ Wrapper** | Subprocess invocation of lib/decompose |
| **lib/decompose** | Pathwidth optimization (external black-box) |

| コンポーネント | 責務 |
|-----------|----------------|
| **Python CLI** | オーケストレーション、ファイル I/O、対応表抽出 |
| **C++ ラッパー** | lib/decompose のサブプロセス呼び出し |
| **lib/decompose** | パス幅最適化（外部ブラックボックス） |

The `lib/decompose` program is treated as a **black-box optimizer** that consumes and produces `.grh` files. It cannot be modified and its internal algorithm is not part of this specification.

`lib/decompose` プログラムは `.grh` ファイルを消費・生成する**ブラックボックス最適化器**として扱われます。変更できず、その内部アルゴリズムは本仕様の一部ではありません。

---

## Input Format / 入力形式

Phase 1 accepts `polyhedron.json` from Rotational Unfolding's data directory as input:

Phase 1 は Rotational Unfolding のデータディレクトリから `polyhedron.json` を入力として受け取ります：

```
RotationalUnfolding/data/polyhedra/
└── <class>/
    └── <name>/
        └── polyhedron.json
```

### polyhedron.json

Defines the combinatorial structure of a polyhedron with **old edge labeling**:

- `schema_version`: Format version (currently 1)
- `polyhedron.class` / `polyhedron.name`: Identifier
- `faces[]`: Array of faces with adjacency information
  - `face_id`: Face identifier
  - `gon`: Number of edges (polygon type)
  - `neighbors[]`: Adjacent faces and edges
    - `edge_id`: Edge identifier (**old labeling**)
    - `face_id`: Adjacent face identifier

**旧辺ラベル体系**の多面体の組合せ構造を定義：

- `schema_version`: フォーマットバージョン（現在 1）
- `polyhedron.class` / `polyhedron.name`: 識別子
- `faces[]`: 隣接情報を含む面の配列
  - `face_id`: 面識別子
  - `gon`: 辺の数（多角形の種類）
  - `neighbors[]`: 隣接する面と辺
    - `edge_id`: 辺識別子（**旧ラベル体系**）
    - `face_id`: 隣接する面識別子

---

## Output Format / 出力形式

**Phase 1 Contract**: Each execution produces exactly four files as the canonical output:

- `polyhedron_relabeled.json`: Polyhedron data with new edge labels (for Phase 2+)
- `edge_mapping.json`: Old edge ID → new edge ID mapping (for Phase 2)
- `input.grh`: Original graph representation (for debugging)
- `output.grh`: Optimized graph representation (for debugging)

**Phase 1 の契約**: 各実行は正規の出力として正確に4つのファイルを生成します：

- `polyhedron_relabeled.json`: 新辺ラベル体系の多面体データ（Phase 2 以降用）
- `edge_mapping.json`: 旧辺 ID → 新辺 ID の対応表（Phase 2 用）
- `input.grh`: 元のグラフ表現（デバッグ用）
- `output.grh`: 最適化されたグラフ表現（デバッグ用）

These files are written to deterministic locations within the Counting repository:

これらのファイルは Counting リポジトリ内の決定的な場所に書き込まれます：

```
CountingNonoverlappingUnfoldings/
├── data/polyhedra/<class>/<name>/
│   ├── polyhedron_relabeled.json
│   └── edge_mapping.json
│
└── output/polyhedra/<class>/<name>/edge_relabeling/
    ├── input.grh
    └── output.grh
```

### polyhedron_relabeled.json

**Generated by**: `relabeler.py`
**Format**: JSON (pretty-printed)
**Purpose**: Polyhedron data with new edge labels for Phase 2+

**生成元**: `relabeler.py`
**形式**: JSON（整形済み）
**目的**: Phase 2 以降のための新辺ラベル体系の多面体データ

Identical structure to input `polyhedron.json`, but all `neighbors[].edge_id` values are updated according to `edge_mapping.json`. This file serves as the **authoritative polyhedron data** for all subsequent Counting phases.

入力 `polyhedron.json` と同一構造ですが、すべての `neighbors[].edge_id` 値が `edge_mapping.json` に従って更新されています。このファイルはすべての後続 Counting フェーズのための**権威的多面体データ**として機能します。

### edge_mapping.json

**Generated by**: `edge_mapper.py`
**Format**: JSON (pretty-printed)
**Purpose**: Edge label mapping for Phase 2 unfolding relabeling

**生成元**: `edge_mapper.py`
**形式**: JSON（整形済み）
**目的**: Phase 2 の展開図辺ラベル貼り替えのための辺ラベル対応表

```json
{
  "0": 3,
  "1": 11,
  "2": 6,
  ...
}
```

**Key properties**:
- Keys are old edge IDs (as strings, due to JSON spec)
- Values are new edge IDs (integers)
- Mapping is a bijection (one-to-one correspondence)
- All edge IDs from 0 to (num_edges - 1) are present

**主要な特性**：
- キーは旧辺 ID（JSON 仕様により文字列）
- 値は新辺 ID（整数）
- マッピングは全単射（1対1対応）
- 0 から (辺数 - 1) までのすべての辺 ID が存在

### .grh Files (input.grh, output.grh)

**Generated by**: `grh_generator.py` (input), `edge_relabeling` binary (output)
**Format**: Custom text format (compatible with lib/decompose and tdzdd)
**Purpose**: Debugging and verification

**生成元**: `grh_generator.py`（input）、`edge_relabeling` バイナリ（output）
**形式**: カスタムテキスト形式（lib/decompose および tdzdd 互換）
**目的**: デバッグと検証

```
p edge <num_vertices> <num_edges>
e <v1> <v2>
e <v1> <v2>
...
```

**Format specification**:
- Header line: `p edge V E` where V = number of vertices, E = number of edges
- Edge lines: `e v1 v2` where v1, v2 are **1-indexed** vertex IDs
- Vertices are reconstructed via Union-Find (not from input data)
- Edges are listed in edge ID order (input.grh: old order, output.grh: new order)

**形式仕様**：
- ヘッダー行: `p edge V E`（V = 頂点数、E = 辺数）
- 辺行: `e v1 v2`（v1, v2 は **1-indexed** 頂点 ID）
- 頂点は Union-Find で再構成される（入力データからではない）
- 辺は edge ID 順にリスト（input.grh: 旧順序、output.grh: 新順序）

---

## Usage / 使用方法

### Basic Execution

```bash
# From CountingNonoverlappingUnfoldings repository root
cd /path/to/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m edge_relabeling --poly <path_to_polyhedron.json>
```

### Arguments

- `--poly <path>`: Path to `polyhedron.json` (can be absolute or relative) **[required]**

### Examples

#### Johnson solid n20

```bash
PYTHONPATH=python python -m edge_relabeling \
  --poly /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json
```

**Output:**
```
============================================================
Phase 1: Edge Relabeling
  Polyhedron: johnson/n20
  Input:      /Users/.../n20/polyhedron.json
============================================================

[Step 1/4] Generating .grh file...
  Generated: output/polyhedra/johnson/n20/edge_relabeling/input.grh
    Edges:    45
    Vertices: 25

[Step 2/4] Running decompose (pathwidth optimization)...
  Input:  output/polyhedra/johnson/n20/edge_relabeling/input.grh
  Output: output/polyhedra/johnson/n20/edge_relabeling/output.grh
    Input edges:  45
    Output edges: 45

[Step 3/4] Extracting edge mapping...
  Created: data/polyhedra/johnson/n20/edge_mapping.json
    Total edges: 45
    Mapping (first 5):
      0 → 3
      1 → 11
      2 → 6
      3 → 1
      4 → 8

[Step 4/4] Relabeling polyhedron edges...
  Created: data/polyhedra/johnson/n20/polyhedron_relabeled.json
    Faces: 22

============================================================
Phase 1 Complete!
============================================================
```

#### Platonic solid r01

```bash
PYTHONPATH=python python -m edge_relabeling \
  --poly /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/platonic/r01/polyhedron.json
```

### Output Directory Structure

```
CountingNonoverlappingUnfoldings/
├── data/polyhedra/
│   ├── johnson/
│   │   └── n20/
│   │       ├── polyhedron_relabeled.json
│   │       └── edge_mapping.json
│   └── platonic/
│       └── r01/
│           ├── polyhedron_relabeled.json
│           └── edge_mapping.json
│
└── output/polyhedra/
    ├── johnson/
    │   └── n20/
    │       └── edge_relabeling/
    │           ├── input.grh
    │           └── output.grh
    └── platonic/
        └── r01/
            └── edge_relabeling/
                ├── input.grh
                └── output.grh
```

---

## Processing Steps / 処理ステップ

Phase 1 consists of four sequential steps orchestrated by `cli.py`:

Phase 1 は `cli.py` によってオーケストレーションされる4つの連続ステップから構成されます：

### Step 1: Graph Construction / グラフ構築

**Module**: `graph_builder.py`

**Input**: `polyhedron.json`
**Output**: `{edge_id: (vertex_i, vertex_j)}` mapping (in-memory)

**Algorithm**:
1. Assign virtual vertex pairs to each edge from face-adjacency data
2. Assign unique IDs to all virtual vertices: `(face_id, neighbor_index)` → `virtual_vertex_id`
3. Use Union-Find to merge vertices that share the same edge
4. Map Union-Find representatives to final vertex IDs (0-indexed, consecutive)
5. Output edge-to-vertex mapping

**アルゴリズム**:
1. 面隣接データから各辺に仮頂点ペアを割り当て
2. すべての仮頂点に一意な ID を割り当て: `(face_id, neighbor_index)` → `virtual_vertex_id`
3. Union-Find で同じ辺を共有する頂点を統合
4. Union-Find の代表元を最終頂点 ID（0-indexed、連続）にマッピング
5. 辺–頂点対応を出力

**Note**: Vertex IDs reconstructed here are internal and independent of any geometric or topological vertex ordering. They exist solely to represent edge connectivity.

**注記**: ここで再構成される頂点 ID は内部的なものであり、幾何的またはトポロジカルな頂点順序とは無関係です。辺の接続性を表現するためだけに存在します。

### Step 2: .grh File Generation / .grh ファイル生成

**Module**: `grh_generator.py`

**Input**: `{edge_id: (vertex_i, vertex_j)}` mapping (from Step 1)
**Output**: `input.grh` (written to `output/polyhedra/<class>/<name>/edge_relabeling/`)

**Format conversion**:
- Vertices: 0-indexed (internal) → 1-indexed (lib/decompose format)
- Output edges in edge_id ascending order
- Include `p edge V E` header

**形式変換**:
- 頂点: 0-indexed（内部）→ 1-indexed（lib/decompose 形式）
- edge_id の昇順で辺を出力
- `p edge V E` ヘッダーを含む

### Step 3: Pathwidth Optimization / パス幅最適化

**Module**: `decompose_runner.py` (Python) + `edge_relabeling` binary (C++)

**Input**: `input.grh`
**Output**: `output.grh` (written to `output/polyhedra/<class>/<name>/edge_relabeling/`)

**Execution**:
```bash
./cpp/edge_relabeling/build/edge_relabeling < input.grh > output.grh
```

**Internal processing** (within C++ binary):
1. Read `.grh` from stdin (lib/decompose's `readGraph` converts 1-indexed to 0-indexed internally)
2. Run `decompose(G, time_limit=30.0, beam_width=60)` for path decomposition
3. Convert vertex ordering to edge ordering via `convertEdgePermutation`
4. Validate edge count consistency
5. Output `.grh` to stdout (convert back to 1-indexed)

**内部処理**（C++ バイナリ内）:
1. stdin から `.grh` を読み込み（lib/decompose の `readGraph` が内部で 1-indexed を 0-indexed に変換）
2. `decompose(G, time_limit=30.0, beam_width=60)` でパス分解を実行
3. `convertEdgePermutation` で頂点順序を辺順序に変換
4. 辺数の一貫性を検証
5. `.grh` を stdout に出力（1-indexed に変換し直す）

**Black-box disclaimer**: The `lib/decompose` algorithm is external, cannot be modified, and its internal behavior is not part of this specification. Phase 1 treats it as a black-box optimizer.

**ブラックボックス免責事項**: `lib/decompose` アルゴリズムは外部のものであり、変更できず、その内部動作は本仕様の一部ではありません。Phase 1 はそれをブラックボックス最適化器として扱います。

### Step 4a: Edge Mapping Extraction / 辺ラベル対応表の抽出

**Module**: `edge_mapper.py`

**Input**: `input.grh`, `output.grh`
**Output**: `edge_mapping.json` (written to `data/polyhedra/<class>/<name>/`)

**Algorithm**:
1. Parse `input.grh` and create `{(v1, v2): edge_id}` mapping (normalized: min vertex first)
2. Parse `output.grh` and create `{(v1, v2): edge_id}` mapping
3. Match edges by vertex pairs: `old_edge_id` → `new_edge_id`
4. Validate that the mapping is a bijection
5. Save as JSON

**アルゴリズム**:
1. `input.grh` を解析し `{(v1, v2): edge_id}` マッピングを作成（正規化: 小さい頂点を先に）
2. `output.grh` を解析し `{(v1, v2): edge_id}` マッピングを作成
3. 頂点ペアで辺を照合: `old_edge_id` → `new_edge_id`
4. マッピングが全単射であることを検証
5. JSON として保存

### Step 4b: Polyhedron Relabeling / 多面体の辺ラベル貼り替え

**Module**: `relabeler.py`

**Input**: `polyhedron.json`, `edge_mapping.json`
**Output**: `polyhedron_relabeled.json` (written to `data/polyhedra/<class>/<name>/`)

**Algorithm**:
1. Load `polyhedron.json`
2. Load `edge_mapping.json` (convert string keys to integers)
3. Deep copy polyhedron data
4. For each face, for each neighbor, replace `edge_id` using the mapping
5. Verify relabeling correctness (face count, gon, neighbor structure unchanged)
6. Save as `polyhedron_relabeled.json`

**アルゴリズム**:
1. `polyhedron.json` を読み込み
2. `edge_mapping.json` を読み込み（文字列キーを整数に変換）
3. 多面体データを深いコピー
4. 各面、各隣接について、マッピングを使用して `edge_id` を置換
5. 貼り替えの正しさを検証（面数、gon、隣接構造が不変）
6. `polyhedron_relabeled.json` として保存

---

## Design Decisions / 設計判断

### Why Union-Find for vertex reconstruction?

Polyhedron data only stores face-edge adjacency, not explicit vertex information. Vertices must be reconstructed by identifying which edges share endpoints. Union-Find efficiently merges virtual vertices that belong to the same actual vertex.

### なぜ頂点再構成に Union-Find を使うのか？

多面体データは面と辺の隣接のみを保存し、明示的な頂点情報は持ちません。頂点は、どの辺が端点を共有するかを識別することで再構成する必要があります。Union-Find は、同じ実際の頂点に属する仮頂点を効率的に統合します。

### Why 1-indexed vertices in .grh?

`lib/decompose` expects 1-indexed vertex IDs as input. Internally, it converts them to 0-indexed, but the input/output contract requires 1-indexed. Phase 1 maintains this convention for compatibility.

### なぜ .grh で 1-indexed 頂点を使うのか？

`lib/decompose` は入力として 1-indexed 頂点 ID を期待します。内部的には 0-indexed に変換しますが、入出力契約は 1-indexed を要求します。Phase 1 は互換性のためこの慣習を維持します。

### Why separate data/ and output/ directories?

- `data/`: Contains authoritative data for downstream phases (Phase 2+). These files are **phase outputs** and should be versioned.
- `output/`: Contains intermediate/debugging files (.grh). These are regenerable and less critical.

### なぜ data/ と output/ ディレクトリを分離するのか？

- `data/`: 下流フェーズ（Phase 2 以降）のための権威的データを含む。これらのファイルは**フェーズの出力**でありバージョン管理すべき。
- `output/`: 中間・デバッグファイル（.grh）を含む。これらは再生成可能でそれほど重要ではない。

### Why JSON for edge mapping instead of binary?

- Human-readable for debugging
- Easy to parse in any language (Python, C++, etc.)
- Phase 2 can directly load and use it

### なぜ辺ラベル対応表を JSON にするのか、バイナリではなく？

- デバッグのために人間が読める
- あらゆる言語（Python、C++ など）で解析が容易
- Phase 2 が直接読み込んで使用できる

---

## Limitations and Known Issues / 制限と既知の問題

### Phase 1 Guarantees

Phase 1 provides the following guarantees:

1. **Deterministic output paths**: Same polyhedron always writes to the same location within Counting repository.
2. **Bijective mapping**: Every old edge ID maps to exactly one new edge ID, and vice versa.
3. **Structure preservation**: Face topology (face_id, gon, neighbor face_ids) is unchanged after relabeling.
4. **Optimized ordering**: Edge ordering is optimized for pathwidth (subject to lib/decompose's algorithm).

### Phase 1 の保証

Phase 1 は以下を保証します：

1. **決定的な出力パス**: 同じ多面体は Counting リポジトリ内の同じ場所に常に書き込まれます。
2. **全単射マッピング**: すべての旧辺 ID は正確に1つの新辺 ID にマッピングされ、逆も同様です。
3. **構造の保持**: 貼り替え後も面トポロジー（face_id、gon、隣接面 ID）は変更されません。
4. **最適化された順序**: 辺順序はパス幅について最適化されます（lib/decompose のアルゴリズムに依存）。

### Phase 1 Does NOT Guarantee

1. **No vertex ID consistency across runs**: Vertex IDs are reconstructed via Union-Find and may differ between runs (but edge connectivity is preserved).
2. **No geometric information**: Vertex positions, face coordinates, and angles are not computed.
3. **No unfolding processing**: Rotational Unfolding output (`exact.jsonl`) is not touched in Phase 1.
4. **No optimality proof**: Pathwidth optimization quality depends on lib/decompose's heuristic algorithm.

### Phase 1 が保証しないこと

1. **実行間での頂点 ID の一貫性なし**: 頂点 ID は Union-Find で再構成され、実行間で異なる可能性があります（ただし辺の接続性は保持されます）。
2. **幾何情報なし**: 頂点位置、面座標、角度は計算されません。
3. **展開図の処理なし**: Rotational Unfolding の出力（`exact.jsonl`）は Phase 1 では触れません。
4. **最適性の証明なし**: パス幅最適化の品質は lib/decompose のヒューリスティックアルゴリズムに依存します。

### Intentional Design Choices (Not Bugs)

The following behaviors are intentional and part of the Phase 1 specification:

- **Vertex IDs are internal**: Vertex labels reconstructed in Phase 1 are for .grh generation only. Phase 3 will reconstruct vertices again from `polyhedron_relabeled.json`. No consistency between Phase 1 and Phase 3 vertices is required.
- **1-indexed .grh output**: This matches lib/decompose's expected format. Internal Python processing uses 0-indexed vertices.
- **No polyhedron.json modification**: Original `polyhedron.json` in RotationalUnfolding repository is **never modified** (read-only constraint). Phase 1 creates a new file in Counting repository.

### 意図的な設計選択（バグではない）

以下の挙動は意図的であり、Phase 1 仕様の一部です：

- **頂点 ID は内部的**: Phase 1 で再構成される頂点ラベルは .grh 生成のためだけのものです。Phase 3 は `polyhedron_relabeled.json` から頂点を再構成します。Phase 1 と Phase 3 の頂点間の一貫性は不要です。
- **1-indexed .grh 出力**: これは lib/decompose の期待形式と一致します。内部的な Python 処理は 0-indexed 頂点を使用します。
- **polyhedron.json の変更なし**: RotationalUnfolding リポジトリの元の `polyhedron.json` は**決して変更されません**（読み取り専用制約）。Phase 1 は Counting リポジトリに新しいファイルを作成します。

---

## Downstream Processing / 下流処理

**Phase 1 Output Contract**: `polyhedron_relabeled.json` + `edge_mapping.json` serve as the stable interface for Phase 2 and beyond.

**Phase 1 出力契約**: `polyhedron_relabeled.json` + `edge_mapping.json` は Phase 2 以降のための安定したインターフェースとして機能します。

Phase 1 output serves as **input** for the following downstream phases:

- **Phase 2 (Relabeling and Isomorphism Expansion)**: 
  - Reads `polyhedron_relabeled.json` for new edge labels
  - Reads `edge_mapping.json` to relabel `exact.jsonl` from Rotational Unfolding
  - Expands non-isomorphic unfoldings to include all isomorphic variants
  - Outputs `unfoldings_overlapping_all.jsonl` (with new edge labels, no geometric data)

- **Phase 3 (Graph Data Conversion)**: 
  - Reads `polyhedron_relabeled.json` to generate `.grh` for tdzdd
  - Reads `unfoldings_overlapping_all.jsonl` to extract edge sets
  - Outputs `polyhedron.grh` and `unfoldings_edgesets.jsonl`

- **Phase 4 (ZDD Construction)**: 
  - Reads `polyhedron.grh` to build ZDD of all spanning trees
  - Does not use `unfoldings_edgesets.jsonl` directly

- **Phase 5 (Filtering)**: 
  - Applies no-overlap filter to ZDD from Phase 4
  - Uses `unfoldings_edgesets.jsonl` to identify overlapping unfoldings

Phase 1 の出力は以下の下流フェーズの**入力**として機能します：

- **Phase 2（辺ラベル貼り替えと同型展開）**: 
  - 新辺ラベルのため `polyhedron_relabeled.json` を読み込み
  - Rotational Unfolding の `exact.jsonl` を辺ラベル貼り替えするため `edge_mapping.json` を読み込み
  - 非同型展開図をすべての同型バリアントを含むように展開
  - `unfoldings_overlapping_all.jsonl` を出力（新辺ラベル、幾何データなし）

- **Phase 3（グラフデータ変換）**: 
  - tdzdd 用の `.grh` を生成するため `polyhedron_relabeled.json` を読み込み
  - 辺集合を抽出するため `unfoldings_overlapping_all.jsonl` を読み込み
  - `polyhedron.grh` と `unfoldings_edgesets.jsonl` を出力

- **Phase 4（ZDD 構築）**: 
  - すべての全域木の ZDD を構築するため `polyhedron.grh` を読み込み
  - `unfoldings_edgesets.jsonl` は直接使用しない

- **Phase 5（フィルタリング）**: 
  - Phase 4 の ZDD に重なりなしフィルタを適用
  - 重なりを持つ展開図を識別するため `unfoldings_edgesets.jsonl` を使用

**Phase boundary contract**: The guaranteed contract is:

1. `polyhedron_relabeled.json` adheres to the same schema as input `polyhedron.json` (schema_version: 1) but with new edge labels
2. `edge_mapping.json` provides a bijective mapping from old to new edge IDs
3. Output paths follow the Counting repository convention: `data/polyhedra/<class>/<name>/` for authoritative data

**Phase 境界契約**: 保証される契約は：

1. `polyhedron_relabeled.json` は入力 `polyhedron.json` と同じスキーマに従います（schema_version: 1）が、新辺ラベルを持ちます
2. `edge_mapping.json` は旧辺 ID から新辺 ID への全単射マッピングを提供します
3. 出力パスは Counting リポジトリの規約に従います：権威的データは `data/polyhedra/<class>/<name>/`

---

## References / 参考資料

### Specification and Implementation

- **Python implementation**: `python/edge_relabeling/`
  - `cli.py`: Unified CLI orchestration
  - `graph_builder.py`: Union-Find and vertex-edge graph construction
  - `grh_generator.py`: .grh file generation
  - `decompose_runner.py`: C++ binary subprocess invocation
  - `edge_mapper.py`: Edge mapping extraction
  - `relabeler.py`: Polyhedron edge relabeling
- **C++ implementation**: `cpp/edge_relabeling/src/main.cpp`
- **External dependency**: `lib/decompose/` (black-box, read-only)
- **Specification documents**: `.cursor/plans/PHASE1_EDGE_RELABELING_SPEC.md`

### 仕様と実装

- **Python 実装**: `python/edge_relabeling/`
  - `cli.py`: 統合 CLI オーケストレーション
  - `graph_builder.py`: Union-Find と頂点–辺グラフ構築
  - `grh_generator.py`: .grh ファイル生成
  - `decompose_runner.py`: C++ バイナリのサブプロセス呼び出し
  - `edge_mapper.py`: 辺ラベル対応表の抽出
  - `relabeler.py`: 多面体の辺ラベル貼り替え
- **C++ 実装**: `cpp/edge_relabeling/src/main.cpp`
- **外部依存**: `lib/decompose/`（ブラックボックス、読み取り専用）
- **仕様ドキュメント**: `.cursor/plans/PHASE1_EDGE_RELABELING_SPEC.md`

### Build Instructions

**C++ binary** (required before running Phase 1):

```bash
cd cpp/edge_relabeling
mkdir -p build && cd build
cmake ..
make
```

This produces `cpp/edge_relabeling/build/edge_relabeling` binary.

**C++ バイナリ**（Phase 1 実行前に必要）:

```bash
cd cpp/edge_relabeling
mkdir -p build && cd build
cmake ..
make
```

これにより `cpp/edge_relabeling/build/edge_relabeling` バイナリが生成されます。

---

**Document Status**: This document describes the **frozen specification** of Phase 1 as of 2026-02-11. The input/output contract defined here is stable and serves as the foundation for Phase 2 (Relabeling and Isomorphism Expansion), Phase 3 (Graph Data Conversion), Phase 4 (ZDD Construction), and Phase 5 (Filtering).

**文書ステータス**: この文書は 2026-02-11 時点での Phase 1 の**凍結された仕様**を記述します。ここで定義される入出力契約は安定しており、Phase 2（辺ラベル貼り替えと同型展開）、Phase 3（グラフデータ変換）、Phase 4（ZDD 構築）、Phase 5（フィルタリング）の基盤として機能します。
