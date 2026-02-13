# nonisomorphic - 全域木パイプライン CLI

全域木の列挙・重なりフィルタ・非同型数え上げを統合実行する CLI。

## 実行モード

2 つの直交フラグ `--filter` と `--noniso` の組み合わせで 4 モードを提供する。

| フラグ | フェーズ | 内容 |
|--------|---------|------|
| （なし） | Phase 4 | ラベル付き全域木の数え上げのみ |
| `--filter` | Phase 4→5 | + 重なりフィルタ |
| `--noniso` | Phase 4→6 | + 非同型数え上げ（Burnside） |
| `--filter --noniso` | Phase 4→5→6 | + 両方 |

### 各フェーズの役割

- **Phase 4**: 多面体グラフの全域木を ZDD として構築し、ラベル付き全域木数を数える
- **Phase 5**: 重なりを持つ展開図（MOPE）を ZDD subsetting で除去し、重なりなし展開図数を数える
- **Phase 6**: Burnside の補題により、非同型な展開図数を数える

## 実行方法

### 前提

```bash
# C++ バイナリのビルド（初回のみ）
cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make
```

### Phase 4（全域木の数え上げのみ）

```bash
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n20
```

### Phase 4→5（+ 重なりフィルタ）

```bash
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n20 --filter
```

`unfoldings_edge_sets.jsonl` が `--poly` ディレクトリに必要。

### Phase 4→6（+ 非同型数え上げ）

```bash
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n20 --noniso
```

論文 HS13 と同じ結果を得るモード。

### Phase 4→5→6（+ 重なりフィルタ + 非同型数え上げ）

```bash
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n20 --filter --noniso
```

「**重なりを持たない非同型な辺展開図の個数**」を得る。

## 入力ファイル

`--poly` で指定するディレクトリに以下が必要：

| ファイル | 必須条件 |
|---------|---------|
| `polyhedron.grh` | 常に必須 |
| `unfoldings_edge_sets.jsonl` | `--filter` 使用時 |

`automorphisms.json` は `--noniso` 指定時に自動生成される。

## 出力

`output/polyhedra/<class>/<name>/spanning_tree/result.json` に保存される。

Phase 4→5→6 実行時の出力例：

```json
{
  "input_file": "data/polyhedra/johnson/n20/polyhedron.grh",
  "vertices": 25,
  "edges": 45,
  "phase4": {
    "build_time_ms": 2.8,
    "count_time_ms": 0.52,
    "spanning_tree_count": "29821320745"
  },
  "phase5": {
    "filter_applied": true,
    "num_mopes": 40,
    "subset_time_ms": 517.19,
    "non_overlapping_count": "27158087415"
  },
  "phase6": {
    "burnside_applied": true,
    "group_order": 10,
    "burnside_time_ms": 204.58,
    "burnside_sum": "27158155410",
    "nonisomorphic_count": "2715815541",
    "invariant_counts": ["27158087415", "13599", "0", ...]
  }
}
```

## 高速化

### SymmetryFilter（Phase 6）

- `DdSpec<BitMask>` ベースのビットマスク実装
- 軌道の一貫性を単一ビットマスクで追跡

### Theorem 2 ゼロ前処理（Phase 6）

HS13 論文の Theorem 2 Case 3/4 により、ZDD subsetting なしで |T_g| = 0 を判定：

- **Case 3**: Fix(g) ≠ ∅ かつ Fix(g) が非連結 → |T_g| = 0
- **Case 4**: Fix(g) = ∅ かつ ι(g) = 0 → |T_g| = 0

## 検証済み結果

### n20 (J20)

| モード | ラベル付き全域木 | 重なりなし | 非同型 |
|--------|----------------|-----------|--------|
| Phase 4 | 29,821,320,745 | — | — |
| Phase 4→5 | 29,821,320,745 | 27,158,087,415 | — |
| Phase 4→6 | 29,821,320,745 | — | 2,982,139,245 |
| Phase 4→5→6 | 29,821,320,745 | 27,158,087,415 | 2,715,815,541 |

Phase 4→6 の非同型数は論文 HS13 Table 3 (J20) と一致。

### s12L (Snub cube)

| モード | ラベル付き全域木 | 重なりなし | 非同型 |
|--------|----------------|-----------|--------|
| Phase 4→6 | 89,904,012,853,248 | — | 3,746,001,752,064 |
| Phase 4→5→6 | 89,904,012,853,248 | 85,967,688,920,076 | 3,581,988,230,895 |

Phase 4→6 の非同型数は論文 HS13 Table 2 (Snub cube) と一致。

## 参考文献

- HS13: Horiyama, T., Shoji, W. "The Number of Different Unfoldings of Polyhedra", ISAAC 2013.
