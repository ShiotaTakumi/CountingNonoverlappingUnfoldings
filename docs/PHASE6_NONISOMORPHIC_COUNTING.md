# Phase 6: Nonisomorphic Counting — Burnside's Lemma on ZDD

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-08

---

## Overview / 概要

Phase 6 counts nonisomorphic spanning trees (i.e., nonisomorphic edge unfoldings) using Burnside's lemma applied to ZDD. It computes the automorphism group Aut(Γ) of the polyhedron's 1-skeleton graph, then for each automorphism g, counts g-invariant spanning trees |T_g| via ZDD subsetting. The final result is obtained by dividing the sum of all |T_g| by the group order |Aut(Γ)|.

Phase 6 は、ZDD に適用した Burnside の補題を用いて非同型な全域木（= 非同型な辺展開図）を数え上げます。多面体の 1-skeleton グラフの自己同型群 Aut(Γ) を計算し、各自己同型 g に対して ZDD subsetting により g-不変全域木 |T_g| を数えます。最終結果は全 |T_g| の和を群位数 |Aut(Γ)| で割ることで得られます。

Phase 6 operates on the ZDD constructed in Phase 4. If Phase 5 (overlap filtering) has been applied, Phase 6 counts nonisomorphic non-overlapping unfoldings instead.

Phase 6 は Phase 4 で構築された ZDD に対して動作します。Phase 5（重なりフィルタ）が適用済みの場合、Phase 6 は重なりを持たない非同型展開図を数えます。

---

## Theoretical Foundation / 理論的基盤

### Burnside's Lemma

Given a polyhedron P with 1-skeleton Γ:

u(Γ) = (1 / |Aut Γ|) × Σ_{g ∈ Aut Γ} |T_g|

where T_g = {T ∈ T | gT = T} is the set of g-invariant spanning trees.

### Theorem 2 Zero Pre-filtering [HS13]

For certain automorphisms, |T_g| = 0 can be determined without ZDD operations:

- **Case 3**: Fix(g) ≠ ∅ and Fix(g) is not connected → |T_g| = 0
- **Case 4**: Fix(g) = ∅ and ι(g) = 0 → |T_g| = 0

where Fix(g) is the subgraph of fixed vertices, and ι(g) is the number of g-invariant edges.

This pre-filtering significantly reduces the number of ZDD subsetting operations required.

---

## Input / 入力

| File | Source | Description / 説明 |
|------|--------|-------------------|
| `polyhedron.grh` | Phase 3 | Polyhedron graph (0-indexed, no header) / 多面体グラフ |
| ZDD (in memory) | Phase 4 (or Phase 4+5) | Spanning tree ZDD / 全域木 ZDD |

Phase 6 does not read additional files from disk; it operates on the ZDD already constructed by Phase 4 (optionally filtered by Phase 5). The automorphism data is computed at runtime by the Python CLI and passed to C++ via `automorphisms.json`.

Phase 6 はディスクからの追加ファイル読み込みを行いません。Phase 4 で構築済み（Phase 5 で任意にフィルタ済み）の ZDD に対して動作します。自己同型データは Python CLI が実行時に計算し、`automorphisms.json` 経由で C++ に渡されます。

---

## Output / 出力

Results are included in `output/polyhedra/<class>/<name>/spanning_tree/result.json` under the `phase6` key:

結果は `output/polyhedra/<class>/<name>/spanning_tree/result.json` の `phase6` キーに含まれます：

```json
{
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

| Field | Description / 説明 |
|-------|-------------------|
| `group_order` | |Aut(Γ)| / 自己同型群の位数 |
| `burnside_time_ms` | Phase 6 execution time (ms) / Phase 6 実行時間 |
| `burnside_sum` | Σ |T_g| / 不変全域木数の合計 |
| `nonisomorphic_count` | burnside_sum / group_order / 非同型数 |
| `invariant_counts` | |T_g| for each g ∈ Aut(Γ) / 各 g の不変全域木数 |

---

## Processing Flow / 処理フロー

### Step 1: Automorphism Computation (Python)

1. Load `polyhedron.grh` and build a networkx graph
2. Compute all automorphisms Aut(Γ) as vertex permutations using `networkx.algorithms.isomorphism.GraphMatcher`
3. Convert vertex permutations to edge permutations (preserving .grh edge order)
4. Apply Theorem 2 zero pre-filtering for each automorphism
5. Save `automorphisms.json` with edge permutations and zero flags

### Step 2: Burnside Computation (C++)

1. Load `automorphisms.json`
2. For each automorphism g:
   - If zero-flagged: record |T_g| = 0 (no ZDD operation)
   - If identity: |T_g| = ZDD cardinality (no subsetting)
   - Otherwise: copy ZDD, apply SymmetryFilter<BitMask>, count cardinality
3. Sum all |T_g| and divide by |Aut(Γ)|

---

## Implementation / 実装

### Python Side

**Directory:** `python/counting/`

| File | Responsibility / 責務 |
|------|----------------------|
| `cli.py` | Unified CLI for Phase 4/5/6 pipeline / Phase 4/5/6 統合 CLI |
| `compute_automorphisms.py` | Automorphism group computation / 自己同型群計算 |
| `__main__.py` | Module entry point / エントリーポイント |

### C++ Side

**Directory:** `cpp/spanning_tree_zdd/`

| File | Responsibility / 責務 |
|------|----------------------|
| `main.cpp` | Phase 4/5/6 main program / Phase 4/5/6 メインプログラム |
| `SymmetryFilter.hpp` | g-invariance filter (DdSpec<BitMask>) / g-不変フィルタ |

### SymmetryFilter Design

SymmetryFilter uses a single bitmask to enforce orbit consistency:

- Each non-trivial orbit under g is assigned one bit
- The "representative" edge (smallest index) records the selection decision
- Subsequent edges in the same orbit enforce the same decision
- Inconsistency results in branch pruning

This design mirrors UnfoldingFilter's bitmask approach for performance.

---

## Usage / 使用方法

### Prerequisites / 前提条件

```bash
# Build C++ binary / C++ バイナリのビルド
cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make
```

### Phase 4→6 (Nonisomorphic counting)

```bash
PYTHONPATH=python python -m counting --poly data/polyhedra/johnson/n20 --noniso
```

### Phase 4→5→6 (Filter + Nonisomorphic counting)

```bash
PYTHONPATH=python python -m counting --poly data/polyhedra/johnson/n20 --no-overlap --noniso
```

---

## Verified Results / 検証済み結果

### n20 (J20)

| Metric | Phase 4→6 | Phase 4→5→6 |
|--------|-----------|-------------|
| Spanning trees | 29,821,320,745 | 29,821,320,745 |
| Non-overlapping | — | 27,158,087,415 |
| Nonisomorphic | 2,982,139,245 | 2,715,815,541 |
| Group order | 10 | 10 |

Phase 4→6 nonisomorphic count matches [HS13] Table 3 (J20).

### s12L (Snub cube)

| Metric | Phase 4→6 | Phase 4→5→6 |
|--------|-----------|-------------|
| Spanning trees | 89,904,012,853,248 | 89,904,012,853,248 |
| Non-overlapping | — | 85,967,688,920,076 |
| Nonisomorphic | 3,746,001,752,064 | 3,581,988,230,895 |
| Group order | 24 | 24 |

Phase 4→6 nonisomorphic count matches [HS13] Table 2 (Snub cube).

---

## Correctness Guarantee / 正当性の保証

### Theorem 2 Pre-filtering Safety

T'_g ⊆ T_g holds because T' ⊆ T (non-overlapping trees are a subset of all trees). Therefore, if T_g = ∅ then T'_g = ∅. The zero pre-filtering is safe for both Phase 4→6 and Phase 4→5→6 modes.

T' ⊆ T（重なりなし全域木は全域木の部分集合）であるため、T'_g ⊆ T_g が成立します。従って T_g = ∅ ならば T'_g = ∅ です。ゼロ前処理は Phase 4→6 と Phase 4→5→6 の両モードで安全です。

---

## References / 参考文献

- [HS13] Takashi Horiyama and Wataru Shoji. The number of different unfoldings of polyhedra. In 24th International Symposium on Algorithms and Computation, volume 8283 of LNCS, pages 623-633. Springer, 2013.
