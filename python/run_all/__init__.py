"""
run_all — Full Pipeline Execution for Counting Non-overlapping Unfoldings

Executes all phases of the counting pipeline in a single command:
    Phase 1 (edge_relabeling)
    → Phase 2 (unfolding_expansion)
    → Phase 3 (graph_export)
    → Phase 4 & 5 (spanning_tree_zdd with filtering)

非重複展開図カウントパイプライン全体を単一コマンドで実行:
    Phase 1（辺ラベル貼り替え）
    → Phase 2（展開図展開）
    → Phase 3（グラフデータ変換）
    → Phase 4 & 5（ZDD 構築 + フィルタリング）

Usage:
    PYTHONPATH=python python -m run_all --poly data/polyhedra/<class>/<name>
"""

__version__ = "1.0.0"
