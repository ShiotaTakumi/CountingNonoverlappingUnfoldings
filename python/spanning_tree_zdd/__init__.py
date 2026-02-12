"""
spanning_tree_zdd — Phase 4: ZDD-based Spanning Tree Enumeration

Handles:
- Execution of C++ binary for spanning tree counting
- JSON output parsing and presentation
- Timing measurement and reporting
- Does NOT handle overlap filtering or unfolding data

ZDD による全域木列挙（Phase 4）:
- 全域木数え上げのための C++ バイナリ実行
- JSON 出力のパースと表示
- 時間計測と報告
- 重なりフィルタリングや展開図データは扱わない

Responsibility in Counting Pipeline:
- Demonstrates ZDD construction for spanning trees
- Validates that TdZdd integration works correctly
- Provides baseline count before overlap filtering (Phase 5)
- Outputs structured results for further analysis

Counting パイプラインにおける責務:
- 全域木に対する ZDD 構築を実証
- TdZdd 統合が正しく動作することを検証
- 重なりフィルタリング前のベースライン個数を提供（Phase 5）
- さらなる分析のための構造化結果を出力
"""
