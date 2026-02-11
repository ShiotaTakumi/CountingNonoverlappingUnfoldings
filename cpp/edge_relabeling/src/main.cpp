/**
 * @file main.cpp
 * @brief Edge Relabeling - decompose によるパス幅最適化
 * @details lib/decompose のパス分解アルゴリズムを用いて、
 *          多面体グラフの辺順序を最適化する
 * @date 2026-02-08
 * @author Takumi SHIOTA
 */

#include <iostream>
#include "../../../lib/decompose/graph.cpp"
#include "../../../lib/decompose/decompose.cpp"
#include "../../../lib/decompose/convertEdgePermutation.cpp"

using namespace std;

/**
 * @brief main 関数
 * @details 標準入力から .grh ファイルを読み込み、
 *          パス分解により辺順序を最適化して標準出力に書き出す
 */
int main() {
    // 標準入力からグラフを読み込む
    Graph G = readGraph();
    
    // パス分解を実行（時間制限: 30秒、ビーム幅: 60）
    auto res = decompose(G, 30.0, 60);
    
    // 頂点順序から辺順序を計算
    vector<pair<int, int>> edgePermutation = convertEdgePermutation(G, res);
    
    // 辺数の検証
    if (edgePermutation.size() != G.numEdges()) {
        cerr << "Error: edgePermutation size (" << edgePermutation.size() 
             << ") != G.numEdges() (" << G.numEdges() << ")" << endl;
        return 1;
    }
    
    // ヘッダーを出力（p edge <頂点数> <辺数>）
    cout << "p edge " << G.numVertices() << ' ' << edgePermutation.size() << endl;
    
    // 最適化された辺順序を出力（e u v 形式、1-indexed）
    for (size_t i = 0; i < edgePermutation.size(); ++i) {
        int u = edgePermutation[i].first;
        int v = edgePermutation[i].second;
        cout << "e " << u+1 << ' ' << v+1 << endl;
    }
    
    return 0;
}
