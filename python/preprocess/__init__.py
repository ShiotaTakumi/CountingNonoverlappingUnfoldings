"""
preprocess — Preprocessing Pipeline (Phase 1-3)

Executes the preprocessing phases of the counting pipeline in a single command:
    Phase 1 (edge_relabeling)
    → Phase 2 (unfolding_expansion)
    → Phase 3 (graph_export)

These phases prepare input data required for Phase 4-6 (nonisomorphic module).

前処理パイプライン（Phase 1-3）を単一コマンドで実行:
    Phase 1（辺ラベル貼り替え）
    → Phase 2（展開図展開）
    → Phase 3（グラフデータ変換）

これらのフェーズは Phase 4-6（nonisomorphic モジュール）に必要な入力データを準備します。

Usage:
    PYTHONPATH=python python -m preprocess --poly data/polyhedra/<class>/<name>
"""

__version__ = "2.0.0"
