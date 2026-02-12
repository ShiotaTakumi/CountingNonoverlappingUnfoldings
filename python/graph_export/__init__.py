"""
graph_export — Phase 3: Graph Data Conversion

Handles:
- Polyhedron graph generation from polyhedron_relabeled.json (Block A)
- Vertex reconstruction using Union-Find algorithm (Block A)
- .grh file generation in TdZdd-compatible format (Block A)
- Edge set extraction from unfoldings_overlapping_all.jsonl (Block B)
- Generation of unfoldings_edge_sets.jsonl for ZDD input (Block B)
- Does NOT handle ZDD construction or geometric computation

グラフデータ変換（Phase 3）:
- polyhedron_relabeled.json からの多面体グラフ生成（Block A）
- Union-Find アルゴリズムによる頂点再構成（Block A）
- TdZdd 互換形式での .grh ファイル生成（Block A）
- unfoldings_overlapping_all.jsonl からの辺集合抽出（Block B）
- ZDD 入力用の unfoldings_edge_sets.jsonl 生成（Block B）
- ZDD 構築や幾何計算は行わない

Responsibility in Counting Pipeline:
- Bridge between Phase 2 (unfolding expansion) and Phase 4 (ZDD construction)
- Transform polyhedron and unfolding data to pure graph format
- Preserve edge ordering from Phase 1 relabeling
- Remove all geometric and overlap information
- Output minimal combinatorial data for ZDD input

Counting パイプラインにおける責務:
- Phase 2（展開図展開）と Phase 4（ZDD 構築）の橋渡し
- 多面体と展開図データを純粋なグラフ形式に変換
- Phase 1 の辺ラベル順序を保持
- 全ての幾何情報と重なり情報を削除
- ZDD 入力用の最小限の組合せデータを出力
"""
