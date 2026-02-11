# Phase 1: Edge Relabeling

多面体データの辺ラベルをパス幅最適化された順序に貼り直すフェーズです。

## 概要

Rotational Unfolding で使用されている `polyhedron.json` の辺ラベル（edge ID）を、
パス幅に基づく新しい体系に貼り直します。

### 処理フロー

1. **グラフ構築**: Union-Find で頂点を再構成し、.grh ファイルを生成
2. **パス幅最適化**: lib/decompose で辺順序を最適化
3. **辺ラベル対応表**: 旧 edge_id → 新 edge_id のマッピングを抽出
4. **辺ラベル貼り替え**: polyhedron.json の辺ラベルを更新

---

## 実行方法（統合実行 - 推奨）

### 基本的な使い方

Phase 1 の全ステップを一括実行：

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m edge_relabeling --poly <polyhedron.json へのパス>
```

### 実行例

#### Johnson solid n20

```bash
PYTHONPATH=python python -m edge_relabeling \
  --poly /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json
```

**出力:**
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

Output files:
  - output/polyhedra/johnson/n20/edge_relabeling/input.grh
  - output/polyhedra/johnson/n20/edge_relabeling/output.grh
  - data/polyhedra/johnson/n20/edge_mapping.json
  - data/polyhedra/johnson/n20/polyhedron_relabeled.json
============================================================
```

#### Platonic solid r01

```bash
PYTHONPATH=python python -m edge_relabeling \
  --poly /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/platonic/r01/polyhedron.json
```

---

## ディレクトリ構造

Phase 1 の実行により、以下のファイルが生成されます：

```
CountingNonoverlappingUnfoldings/
├── data/
│   └── polyhedra/
│       └── <class>/
│           └── <name>/
│               ├── polyhedron_relabeled.json  # 新ラベル体系の polyhedron
│               └── edge_mapping.json          # 辺ラベル対応表
│
└── output/
    └── polyhedra/
        └── <class>/
            └── <name>/
                └── edge_relabeling/
                    ├── input.grh              # decompose 入力
                    └── output.grh             # decompose 出力
```

### ファイルの説明

| ファイル | 説明 | 用途 |
|---------|------|------|
| `polyhedron_relabeled.json` | 新ラベル体系の多面体データ | Phase 2 以降の入力 |
| `edge_mapping.json` | 辺ラベル対応表 `{旧 edge_id: 新 edge_id}` | Phase 2 での辺ラベル変換 |
| `input.grh` | 元の .grh ファイル（1-indexed） | デバッグ・検証用 |
| `output.grh` | パス幅最適化後の .grh ファイル（1-indexed） | デバッグ・検証用 |

---

## .grh ファイル形式

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
2. 辺 ID の昇順で各辺を出力（1-indexed に変換）
3. ヘッダー行 `p edge` を含む形式で出力

### 3. decompose_runner.py

**機能:** C++ バイナリ `cpp/edge_relabeling/build/edge_relabeling` を実行

**処理:**
1. input.grh を標準入力に渡す
2. lib/decompose でパス幅最適化
3. output.grh を標準出力から取得

### 4. edge_mapper.py

**機能:** 辺ラベル対応表の抽出

**処理:**
1. input.grh と output.grh を比較
2. 同じ頂点ペアを持つ辺を対応付け
3. `{旧 edge_id: 新 edge_id}` の辞書を生成
4. JSON ファイルとして保存

### 5. relabeler.py

**機能:** polyhedron.json の辺ラベル貼り替え

**処理:**
1. polyhedron.json を読み込む
2. 全ての `neighbors[].edge_id` を edge_mapping に従って置き換え
3. 妥当性を検証
4. polyhedron_relabeled.json として保存

---

## 個別モジュールの実行（上級者向け）

Phase 1 の各ステップを個別に実行することもできます。

### 1. .grh ファイル生成

```bash
PYTHONPATH=python python -m edge_relabeling.grh_generator \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  output/polyhedra/johnson/n20/edge_relabeling/input.grh
```

### 2. パス幅最適化実行

```bash
PYTHONPATH=python python -m edge_relabeling.decompose_runner \
  output/polyhedra/johnson/n20/edge_relabeling/input.grh \
  output/polyhedra/johnson/n20/edge_relabeling/output.grh
```

### 3. 辺ラベル対応表抽出

```bash
PYTHONPATH=python python -m edge_relabeling.edge_mapper \
  output/polyhedra/johnson/n20/edge_relabeling/input.grh \
  output/polyhedra/johnson/n20/edge_relabeling/output.grh \
  data/polyhedra/johnson/n20/edge_mapping.json
```

### 4. 辺ラベル貼り替え

```bash
PYTHONPATH=python python -m edge_relabeling.relabeler \
  /Users/tshiota/Github/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json \
  data/polyhedra/johnson/n20/edge_mapping.json \
  data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

---

## C++ 実装（lib/decompose）

### ビルド

```bash
cd /Users/tshiota/Github/CountingNonoverlappingUnfoldings/cpp/edge_relabeling
mkdir -p build && cd build
cmake ..
make
```

実行ファイル: `cpp/edge_relabeling/build/edge_relabeling`

### 直接実行（デバッグ用）

```bash
./cpp/edge_relabeling/build/edge_relabeling < input.grh > output.grh
```

通常は `decompose_runner.py` 経由で実行することを推奨します。

---

## 検証結果

| 多面体 | 辺数 | 頂点数 | ステータス |
|--------|------|--------|------------|
| Johnson n20 | 45 | 25 | ✅ 完全成功 |
| Platonic r01 | 6 | 4 | ✅ 完全成功 |
| Archimedean s12L | 60 | 24 | ✅ 完全成功 |

---

## 注意事項

- **頂点番号**: Union-Find の実装に依存するため、実行ごとに異なる可能性あり
- **Phase 3 での再構成**: Phase 1 の頂点ラベルは Phase 3 で再構成されるため、一貫性は不要
- **1-indexed**: lib/decompose は 1-indexed を期待するため、入出力を統一

---

## 次のステップ（Phase 2 以降）

Phase 1 の成果物を使って、Phase 2（Relabeling and Isomorphism Expansion）を実装します。

**Phase 1 の成果物:**
- `data/polyhedra/<class>/<name>/polyhedron_relabeled.json`
- `data/polyhedra/<class>/<name>/edge_mapping.json`

---

**作成日:** 2026-02-08  
**最終更新:** 2026-02-11
