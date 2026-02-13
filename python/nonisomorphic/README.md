# Phase 6: Nonisomorphic Counting — Automorphism Computation Module

## 概要 / Overview

Phase 6 の前処理として、多面体グラフの自己同型群 Aut(Γ) を計算し、
各自己同型を辺置換（edge permutation）として出力する Python モジュール。

This Python module computes the automorphism group Aut(Γ) of a polyhedron's
1-skeleton graph, expressing each automorphism as an edge permutation.
The output is consumed by the C++ `spanning_tree_zdd` binary for
Burnside's lemma computation.

---

## 理論的背景 / Theoretical Background

Burnside の補題により、非同型展開図の個数 u(Γ) は以下で与えられる：

```
u(Γ) = (1 / |Aut(Γ)|) × Σ_{g ∈ Aut(Γ)} |T_g|
```

ここで |T_g| は、自己同型 g の下で不変な全域木（= 展開図）の個数。

本モジュールは Aut(Γ) を計算し、各 g を辺置換として表現する。
|T_g| の計算は C++ 側（SymmetryFilter + ZDD subsetting）が担当する。

参考: Horiyama & Shoji (2013), "The Number of Different Unfoldings of Polyhedra"

---

## ファイル構成 / File Structure

```
python/nonisomorphic/
├── __init__.py                  # モジュール定義
├── __main__.py                  # モジュールエントリーポイント
├── cli.py                       # 統合 CLI（自己同型計算 + C++ 実行）
├── compute_automorphisms.py     # 自己同型群の計算・辺置換への変換
└── README.md                    # 本ファイル
```

---

## 依存ライブラリ / Dependencies

- **networkx** (`pip install networkx`)
  - グラフの構築と、VF2 アルゴリズムによる全自己同型の列挙に使用

---

## 使い方 / Usage

### 基本的な実行方法（推奨）

```bash
PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir>
```

**例:**
```bash
# n20 (Johnson solid J20) の非同型数え上げ
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n20

# s12L (Snub dodecahedron) の非同型数え上げ
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/archimedean/s12L
```

### 入力

- `<polyhedron_dir>/polyhedron.grh` — Phase 3 で生成された多面体グラフファイル
  - 形式: 1 行 1 辺、`v1 v2`（0-indexed、ヘッダーなし）

### 出力

1. **`<polyhedron_dir>/automorphisms.json`** — 自己同型群の辺置換データ

```json
{
  "num_vertices": 25,
  "num_edges": 45,
  "group_order": 10,
  "edge_permutations": [
    [0, 1, 2, ...],
    [3, 0, 1, ...],
    ...
  ]
}
```

| フィールド | 説明 |
|---|---|
| `num_vertices` | グラフの頂点数 |
| `num_edges` | グラフの辺数 |
| `group_order` | 自己同型群の位数 \|Aut(Γ)\| |
| `edge_permutations` | 辺置換のリスト。各要素は長さ E の配列 [σ(0), σ(1), ..., σ(E-1)] |

2. **`output/polyhedra/<class>/<name>/spanning_tree/result.json`** — Phase 4+6 の結果

```json
{
  "input_file": "data/polyhedra/johnson/n20/polyhedron.grh",
  "vertices": 25,
  "edges": 45,
  "phase4": {
    "build_time_ms": 3.55,
    "count_time_ms": 0.50,
    "spanning_tree_count": "29821320745"
  },
  "phase5": {
    "filter_applied": false
  },
  "phase6": {
    "burnside_applied": true,
    "group_order": 10,
    "burnside_time_ms": 310.66,
    "burnside_sum": "29821392450",
    "nonisomorphic_count": "2982139245",
    "invariant_counts": ["29821320745", "14341", "0", ...]
  }
}
```

| phase6 フィールド | 説明 |
|---|---|
| `burnside_applied` | Burnside の補題が適用されたか |
| `group_order` | \|Aut(Γ)\| |
| `burnside_time_ms` | Phase 6 実行時間（ミリ秒） |
| `burnside_sum` | Σ \|T_g\|（Burnside の分子） |
| `nonisomorphic_count` | **非同型展開図の個数**（burnside_sum / group_order） |
| `invariant_counts` | 各自己同型 g に対する \|T_g\| のリスト |

---

## 内部処理の詳細 / Internal Processing

Python CLI が以下を自動で実行します：

1. **自己同型計算** (`compute_automorphisms.py`):
   - `polyhedron.grh` から networkx グラフを構築
   - VF2 アルゴリズムで全自己同型を列挙
   - 頂点置換を辺置換に変換
   - `automorphisms.json` に保存

2. **C++ Phase 4+6 実行**:
   - C++ バイナリ `spanning_tree_zdd` を起動
   - `--automorphisms` フラグで Phase 6 を有効化
   - Phase 4: ZDD で全域木を列挙
   - Phase 6: Burnside の補題で非同型個数を計算
   - 結果を JSON として出力

3. **結果保存**:
   - JSON 出力を `output/.../result.json` に保存

---

## 処理フロー / Processing Flow

```
PYTHONPATH=python python -m nonisomorphic --poly <dir>
    │
    ▼
[cli.py] ─── polyhedron.grh のパスを解決
    │
    ├─ Step 1: 自己同型計算 ────────────────────────────
    │       │
    │       ▼
    │   [load_grh] ─── .grh を読み込み、辺リスト取得
    │       │
    │       ▼
    │   [build_graph] ── networkx グラフを構築
    │       │
    │       ▼
    │   [compute_all_automorphisms] ── VF2 で全自己同型を列挙
    │       │
    │       ▼
    │   [vertex_perm_to_edge_perm] ── 辺置換に変換
    │       │
    │       ▼
    │   automorphisms.json に保存
    │
    ├─ Step 2: C++ Phase 4+6 実行 ───────────────────────
    │       │
    │       ▼
    │   cpp/spanning_tree_zdd/build/spanning_tree_zdd \
    │       <grh> --automorphisms <json>
    │       │
    │       ├─ Phase 4: ZDD 構築 + 全域木カウント
    │       │
    │       └─ Phase 6: Burnside の補題で非同型カウント
    │               │
    │               ├─ 各 g に対して SymmetryFilter 適用
    │               ├─ |T_g| を計算
    │               └─ Σ|T_g| / |Aut(Γ)|
    │       │
    │       ▼
    │   JSON 出力（stdout）
    │
    └─ Step 3: 結果保存 ─────────────────────────────────
            │
            ▼
        output/polyhedra/<class>/<name>/spanning_tree/result.json
```

---

## 検証済みデータ / Verified Results

| 多面体 | |V| | |E| | |Aut(Γ)| | HS13 論文との照合 |
|---|---|---|---|---|
| n20 (J20) | 25 | 45 | 10 | 2,982,139,245 ✓ |
| s12L (Snub dodecahedron) | 24 | 60 | 24 | 3,746,001,752,064 ✓ |

---

## 設計上の注意 / Design Notes

- **nauty の代替**: 本モジュールは nauty を使わず networkx の VF2 実装を利用。
  小〜中規模のグラフ（頂点数 ≤ 100 程度）では十分な性能。
  大規模グラフに対しては nauty への置き換えを検討。

- **辺置換の意味**: `edge_permutations[i][j] = k` は、自己同型 i の下で辺 j が辺 k に写ることを意味する。辺のインデックスは `polyhedron.grh` の行順序に対応。

- **恒等置換の保証**: 出力には必ず恒等置換（`[0, 1, 2, ..., E-1]`）が含まれる。
  含まれない場合は警告を出力する。
