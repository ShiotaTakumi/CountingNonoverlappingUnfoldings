"""
spanning_tree_zdd — Phase 4 & 5: ZDD-based Spanning Tree Enumeration and Filtering

Handles:
- Execution of C++ binary for spanning tree counting and MOPE-based filtering
- JSON output parsing and presentation
- Timing measurement and reporting

ZDD による全域木列挙とフィルタリング（Phase 4 & 5）:
- 全域木数え上げと MOPE ベースフィルタリングのための C++ バイナリ実行
- JSON 出力のパースと表示
- 時間計測と報告

Responsibility in Counting Pipeline:
- Phase 4: Constructs spanning tree ZDD and counts all spanning trees
- Phase 5: Applies MOPE-based subsetting to count non-overlapping unfoldings
- Outputs structured results (result.json) for analysis

Counting パイプラインにおける責務:
- Phase 4: 全域木 ZDD を構築し、全域木の個数を計算
- Phase 5: MOPE ベースの subsetting を適用し非重複展開図を数え上げ
- 分析のための構造化結果（result.json）を出力
"""
