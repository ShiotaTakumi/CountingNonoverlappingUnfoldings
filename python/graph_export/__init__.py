"""
edgeset_extraction — Edge Set Extraction from Unfoldings

Handles:
- Reading exact_relabeled.jsonl (Phase 2 intermediate output)
- Extracting edge_id sets from unfolding face sequences
- Generating unfoldings_edgesets.jsonl for ZDD input
- Does NOT handle geometric information or overlap detection

辺集合抽出 — 展開図からの辺集合抽出:
- exact_relabeled.jsonl の読み込み（Phase 2 中間出力）
- 展開図の面列からの edge_id 集合抽出
- ZDD 入力用の unfoldings_edgesets.jsonl 生成
- 幾何情報や重なり判定は扱わない

Responsibility in Counting Pipeline:
- Transform unfolding face sequences to pure edge sets
- Bridge Phase 2 (unfolding expansion) and Phase 4 (ZDD construction)
- Output minimal combinatorial data only

Counting パイプラインにおける責務:
- 展開図の面列を純粋な辺集合に変換
- Phase 2（展開図展開）と Phase 4（ZDD 構築）の橋渡し
- 最小限の組合せデータのみ出力
"""
