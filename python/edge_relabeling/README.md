# Edge Relabeling - .grh ファイル生成

## 概要

多面体データ（`polyhedron.json`）から Union-Find を用いて頂点を再構成し、
tdzdd が読み込める `.grh` 形式のグラフファイルを生成する。

---

## 実行方法

### 基本的な使い方

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings

PYTHONPATH=python python -m edge_relabeling.grh_generator \
  <polyhedron.json へのパス> \
  <出力 .grh ファイルパス>
```

### 実行例

#### Johnson solid n20

```bash
PYTHONPATH=python python -m edge_relabeling.grh_generator \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  tmp/test_n20.grh
```

**出力:**
```
Generated tmp/test_n20.grh
  Edges: 45
  Vertices: 25
```

#### Archimedean s12L

```bash
PYTHONPATH=python python -m edge_relabeling.grh_generator \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/archimedean/s12L/polyhedron.json \
  tmp/test_s12L.grh
```

**出力:**
```
Generated tmp/test_s12L.grh
  Edges: 60
  Vertices: 24
```

---

## 出力形式

生成される `.grh` ファイルの形式：

```
p edge <num_vertices> <num_edges>
e v1 v2
e v1 v2
...
```

**重要な仕様:**
- 頂点番号は **1-indexed**（lib/decompose が期待する形式）
- 無向グラフ
- 1行 = 1辺
- ヘッダー行 `p edge` を含む

---

## 内部処理

### 1. graph_builder.py

**機能:** Union-Find で頂点を再構成

**処理:**
1. 各面の各辺に仮の頂点ペアを割り当て
2. 同じ `edge_id` を共有する辺の頂点を Union-Find で統合
3. 代表元を最終的な頂点 ID に変換

**出力:** `{edge_id: (vertex_i, vertex_j)}` の辞書

### 2. grh_generator.py

**機能:** `.grh` ファイルの生成

**処理:**
1. `graph_builder` で構築した頂点–辺グラフを受け取る
2. 辺 ID の昇順で各辺を出力
3. 各行は `<vertex1> <vertex2>` の形式

---

## 検証結果

| 多面体 | 辺数 | 頂点数 | Research2024 との一致 |
|--------|------|--------|---------------------|
| Johnson n20 | 45 | 25 | ✅ 一致 |
| Archimedean s12L | 60 | 24 | ✅ 一致 |

---

## 注意事項

- **出力形式の違い**
  - grh_generator.py の出力: decompose 入力形式（`p edge` ヘッダー + `e v1 v2` 形式）
  - decompose の出力: tdzdd 入力形式（`v1 v2` のみ、ヘッダーなし）
  
- **頂点番号**
  - 頂点数は一致するが、頂点番号の割り当ては Union-Find の実装に依存
  - Phase 1 の頂点ラベルは Phase 3 で再構成されるため、一貫性は不要

---

## C++ 実装（decompose）

### ビルド

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings/cpp/edge_relabeling
mkdir -p build && cd build
cmake ..
make
```

実行ファイル: `cpp/edge_relabeling/build/edge_relabeling`

### Python から実行（推奨）

`decompose_runner.py` を使用して Python から C++ バイナリを実行：

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m edge_relabeling.decompose_runner \
  tmp/test_n20.grh \
  tmp/test_n20_decomposed.grh
```

**出力例:**
```
Running decompose...
  Input:  tmp/test_n20.grh
  Output: tmp/test_n20_decomposed.grh

✓ Success!
  Input edges:  45
  Output edges: 45
```

### C++ から直接実行（デバッグ用）

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
./cpp/edge_relabeling/build/edge_relabeling < tmp/test_n20.grh > tmp/test_n20_decomposed.grh
./cpp/edge_relabeling/build/edge_relabeling < tmp/test_s12L.grh > tmp/test_s12L_decomposed.grh
```

### 出力形式

decompose 後の `.grh` も入力と同じ形式（辺マッピング抽出のため）：
```
p edge <num_vertices> <num_edges>
e v1 v2
e v1 v2
...
```

辺の順序がパス幅最適化された順序に並び替えられています。

---

## 辺ラベル対応表の抽出（edge_mapper.py）

### 実行方法

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m edge_relabeling.edge_mapper \
  tmp/test_n20.grh \
  tmp/test_n20_decomposed.grh \
  tmp/test_n20_edge_mapping.json
```

### 出力例

```
Creating edge mapping...
  Original:   tmp/test_n20.grh
  Decomposed: tmp/test_n20_decomposed.grh
  Output:     tmp/test_n20_edge_mapping.json

✓ Success!
  Total edges: 45

  Mapping (first 10):
    0 → 3
    1 → 11
    2 → 6
    ...

✓ Saved to tmp/test_n20_edge_mapping.json
```

### 出力ファイル形式（JSON）

```json
{
  "0": 3,
  "1": 11,
  "2": 6,
  "3": 1,
  ...
}
```

- キー: 旧 edge_id（元の polyhedron.json の辺 ID）
- 値: 新 edge_id（パス幅最適化後の辺 ID）

---

## 辺ラベル貼り替え（relabeler.py）

### 実行方法

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m edge_relabeling.relabeler \
  <polyhedron.json> \
  <edge_mapping.json> \
  <output.json>
```

### 実行例

```bash
PYTHONPATH=python python -m edge_relabeling.relabeler \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  tmp/test_n20_edge_mapping.json \
  tmp/test_n20_polyhedron_relabeled.json
```

### 出力例

```
Relabeling polyhedron edges...
  Input polyhedron: .../polyhedra/johnson/n20/polyhedron.json
  Edge mapping:     tmp/test_n20_edge_mapping.json
  Output:           tmp/test_n20_polyhedron_relabeled.json

  Polyhedron: johnson/n20
  Faces: 22
  Edge mapping size: 45

✓ Success!
  Saved to tmp/test_n20_polyhedron_relabeled.json
```

### 処理内容

- polyhedron.json の各面の neighbors に含まれる `edge_id` を、edge_mapping に従って貼り替える
- `face_id`, `gon`, neighbor の `face_id` は変更しない
- 変更前後の妥当性を自動検証

---

## Phase 1 完全実行フロー

以下の手順で、Phase 1（辺ラベル貼り直し）を完全に実行できます。

### 1. .grh ファイル生成

```bash
PYTHONPATH=python python -m edge_relabeling.grh_generator \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  tmp/test_n20.grh
```

### 2. パス幅最適化実行

```bash
PYTHONPATH=python python -m edge_relabeling.decompose_runner \
  tmp/test_n20.grh \
  tmp/test_n20_decomposed.grh
```

### 3. 辺ラベル対応表抽出

```bash
PYTHONPATH=python python -m edge_relabeling.edge_mapper \
  tmp/test_n20.grh \
  tmp/test_n20_decomposed.grh \
  tmp/test_n20_edge_mapping.json
```

### 4. 辺ラベル貼り替え

```bash
PYTHONPATH=python python -m edge_relabeling.relabeler \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  tmp/test_n20_edge_mapping.json \
  tmp/test_n20_polyhedron_relabeled.json
```

### 最終成果物

- `tmp/test_n20_polyhedron_relabeled.json`: 新しい辺ラベル体系の polyhedron.json

---

## 次のステップ（Phase 2 以降）

Phase 1 の成果物を使って、Phase 2（Relabeling and Isomorphism Expansion）を実装します。

---

**作成日:** 2026-02-08  
**最終更新:** 2026-02-08
