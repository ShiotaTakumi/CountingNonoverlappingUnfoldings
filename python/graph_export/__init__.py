"""
graph_export — Polyhedron Graph Export for TdZdd

Handles:
- Reading polyhedron_relabeled.json
- Extracting edge-face adjacency information
- Reconstructing vertices using Union-Find algorithm
- Generating .grh files in TdZdd-compatible format
- Does NOT handle unfolding data or ZDD construction

多面体グラフのエクスポート（TdZdd 用）:
- polyhedron_relabeled.json の読み込み
- 辺-面の隣接情報抽出
- Union-Find アルゴリズムによる頂点再構成
- TdZdd 互換形式での .grh ファイル生成
- 展開図データや ZDD 構築は扱わない

Responsibility in Counting Pipeline:
- Generate graph input files for TdZdd from polyhedron structure
- Preserve edge ordering from Phase 1 relabeling
- Output minimal combinatorial graph data only

Counting パイプラインにおける責務:
- 多面体構造から TdZdd 用のグラフ入力ファイルを生成
- Phase 1 の辺ラベル順序を保持
- 最小限の組合せグラフデータのみ出力
"""
