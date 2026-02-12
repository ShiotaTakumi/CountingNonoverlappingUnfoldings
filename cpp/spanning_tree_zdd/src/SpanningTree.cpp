// ============================================================================
// SpanningTree.cpp
// ============================================================================
//
// What this file does:
//   Implements SpanningTree class methods for ZDD-based spanning tree enumeration.
//   Uses frontier-based search with component tracking.
//
// このファイルの役割:
//   ZDD ベース全域木列挙のための SpanningTree クラスメソッドを実装。
//   成分追跡を伴うフロンティアベース探索を使用。
//
// ============================================================================

#include "SpanningTree.hpp"

// ============================================================================
// initializeComp
// ============================================================================
//
// Initializes component values in frontier to 0.
// Frontier の成分値を 0 で初期化。
//
void SpanningTree::initializeComp(FrontierData* data) const {
    // Frontier のサイズの最大値のサイズの配列を 0 で初期化する 
    // Initialize array of max frontier size to 0
    for (int i = 0; i < fm.getMaxFrontierSize(); ++i){
        data[i].comp = 0;
    }
}

// ============================================================================
// setComp
// ============================================================================
//
// Updates component value for vertex v.
// 頂点 v の成分値を更新。
//
void SpanningTree::setComp(FrontierData* data, short v, short c) const {
    data[fm.vertexToPos(v)].comp = c;
}

// ============================================================================
// getComp
// ============================================================================
//
// Gets component value for vertex v.
// 頂点 v の成分値を取得。
//
short SpanningTree::getComp(FrontierData* data, short v) const {
    return data[fm.vertexToPos(v)].comp;
}

// ============================================================================
// Constructor
// ============================================================================
//
// Initializes SpanningTree with graph and sets array size.
// グラフで SpanningTree を初期化し、配列サイズを設定。
//
SpanningTree::SpanningTree(const tdzdd::Graph& G) : 
    G(G), 
    v(static_cast<short>(G.vertexSize())),
    e(G.edgeSize()),
    fm(G){
        setArraySize(fm.getMaxFrontierSize());
    }

// ============================================================================
// getRoot
// ============================================================================
//
// Stores computation state at root node.
// Returns the level (number of edges).
//
// 根節点における計算状態を格納。
// レベル（辺の数）を返す。
//
int SpanningTree::getRoot(FrontierData* data) const {
    initializeComp(data);
    return e;
}

// ============================================================================
// getChild
// ============================================================================
//
// Computes child node state for current level and branch choice.
//
// 現在のレベルと枝の選択に対して子ノードの状態を計算。
//
// Parameters:
//   data: Frontier computation state array
//   level: Current level (edges remaining)
//   value: Branch choice (0 = don't select edge, 1 = select edge)
//
// パラメータ:
//   data: フロンティア計算状態配列
//   level: 現在のレベル（残りの辺数）
//   value: 枝の選択（0 = 辺を選ばない、1 = 辺を選ぶ）
//
// Returns:
//   Next level, or -1 to accept, or 0 to prune
//
// 戻り値:
//   次のレベル、または -1（受理）、または 0（枝刈り）
//
// Processing:
//   1. Initialize newly entering vertices with their own component ID
//   2. If edge is selected (value=1):
//      - Check for cycle (same component) → prune
//      - Merge components if different
//   3. At final level: check if graph is connected
//   4. For leaving vertices: verify they're properly connected
//
// 処理:
//   1. 新しくフロンティアに入る頂点を自身の成分 ID で初期化
//   2. 辺が選択された場合（value=1）:
//      - サイクルチェック（同じ成分）→ 枝刈り
//      - 異なる成分なら統合
//   3. 最終レベルで: グラフが連結かチェック
//   4. 出ていく頂点について: 適切に接続されているか検証
//
int SpanningTree::getChild(FrontierData* data, int level, int value) const {
    int edge_index = e - level; // 現在のレベルにおける辺の index / Current edge index
    const Graph::EdgeInfo& edge = G.edgeInfo(edge_index);   // edge_index における辺の情報 / Edge info at edge_index
    const std::vector<int>& entering_vs = fm.getEnteringVs(edge_index); // 新しく Frontier に入る頂点の集合 / Vertices entering frontier
    
    // Frontier に新しく入った頂点における計算状態を v に更新
    // Initialize newly entering vertices with their own component ID
    for (size_t i = 0; i < entering_vs.size(); ++i) {
        int v = entering_vs[i];
        setComp(data, v, v);
    }
    const std::vector<int>& frontier_vs = fm.getFrontierVs(edge_index); // Frontier となる頂点の集合 / Frontier vertices

    // 1-枝が選択された時の処理
    // Processing when edge is selected (1-branch)
    if(value == 1){
        short c1 = getComp(data, edge.v1);  // edge における一方の端点の成分 / Component of first endpoint
        short c2 = getComp(data, edge.v2);  // edge における他方の端点の成分 / Component of second endpoint

        if(c1 == c2) return 0;  // サイクルを形成している場合は枝刈り / Prune if cycle detected
        if(c1 != c2){
            short cmin = std::min(c1, c2);  // 小さい方の成分 / Smaller component
            short cmax = std::max(c1, c2);  // 大きい方の成分 / Larger component

            // フロンティアにおける頂点の計算状態が cmin と一致している場合は cmax に統一する
            // Merge components: update all cmin to cmax in frontier
            for (size_t i = 0; i < frontier_vs.size(); ++i){
                int v = frontier_vs[i];
                if(getComp(data, v) == cmin){
                    setComp(data, v, cmax);
                }
            }
        }
    }

    // 最後のレベルに到達した時の処理
    // Processing at final level
    if(level == 1){
        // edge の両端点における計算状態が一致しているならば全域木を形成しているため解集合とする
        // Accept if both endpoints have same component (connected graph)
        if(getComp(data, edge.v1) == getComp(data, edge.v2)) return -1;
        // それ以外の場合は形成していないため枝刈り
        // Otherwise prune (disconnected graph)
        return 0;
    }

    const std::vector<int>& leaving_vs = fm.getLeavingVs(edge_index);   // Frontier から出ていく頂点の集合 / Vertices leaving frontier
    for (size_t i = 0; i < leaving_vs.size(); ++i){
        int v = leaving_vs[i];
        bool comp_found = false;    // Frontier から適切に抜けているかを管理するフラグ / Flag for proper exit check
        
        // Frontier から出ていく頂点と現在の Frontier における頂点の組合せを全て見ていく
        // Check all combinations of leaving vertex and current frontier vertices
        for (size_t j = 0; j < frontier_vs.size(); ++j) {
            int w = frontier_vs[j];
            
            // 同じ頂点を見ている場合はスキップ
            // Skip if same vertex
            if (w == v) continue;
            
            bool already_left = false;  // w が Frontier から離れている頂点であるかを管理するフラグ / Flag for already left check
            for (size_t k = 0; k < i; ++k) {
                if (w == leaving_vs[k]) {
                    already_left = true;
                    break;
                }
            }
            
            // w が Frontier から離れている頂点である場合はスキップ
            // Skip if w already left frontier
            if(already_left) continue;
            
            // w が Frontier から適切に抜けているならばフラグを true にする
            // Set flag if properly connected
            if(getComp(data, v) == getComp(data, w)) comp_found = true;
            
            // v が Frontier から適切に抜けている場合はこれ以上の探索は不要
            // No need to search further if already found
            if(comp_found) break;
        }
        
        // v が Frontier から適切に抜けていない場合は枝刈り
        // Prune if vertex leaves without proper connection
        if(!comp_found) return 0;
        
        // v が Frontier から適切に抜けている場合はこれ以上計算状態を管理する必要がないため -1 とする
        // Mark as -1 if vertex properly exits (no longer need to track)
        setComp(data, v, -1);
    }
    
    // 次のレベルにおける辺を処理するためにインクリメント
    // Increment to process next edge
    edge_index++;
    return e - edge_index;
}
