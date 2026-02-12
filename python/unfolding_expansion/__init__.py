"""
unfolding_expansion — Phase 2: Unfolding Expansion

Handles:
- Edge relabeling for exact.jsonl using Phase 1 edge mapping
- Isomorphic unfolding expansion from canonical forms
- Generation of unfoldings_overlapping_all.jsonl with schema_version: 2
- Preservation of face structure for visualization and verification
- Does NOT perform overlap detection or geometric computation

展開図の同型展開復元（Phase 2）:
- Phase 1 の辺ラベル対応表を用いた exact.jsonl の辺ラベル貼り替え
- 標準形からの同型展開図の復元
- schema_version: 2 での unfoldings_overlapping_all.jsonl 生成
- 可視化・検証用の面構造保持
- 重なり判定や幾何計算は行わない

Responsibility in Counting Pipeline:
- Bridge between Phase 1 (edge relabeling) and Phase 3 (graph conversion)
- Transforms canonical unfoldings to complete isomorphic set
- Maintains combinatorial structure for ZDD construction in Phase 4

Counting パイプラインにおける責務:
- Phase 1（辺ラベル貼り替え）と Phase 3（グラフ変換）の橋渡し
- 標準形展開図を完全な同型集合に変換
- Phase 4 の ZDD 構築のため組合せ構造を維持
"""
