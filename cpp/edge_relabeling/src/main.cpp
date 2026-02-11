// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   Wrapper for lib/decompose to perform pathwidth-based edge reordering.
//   Reads .grh file from stdin, optimizes edge order, outputs to stdout.
//
// このファイルの役割:
//   lib/decompose のラッパーでパス幅に基づく辺順序の最適化を実行。
//   stdin から .grh ファイルを読み込み、辺順序を最適化し、stdout に出力。
//
// Responsibility in the project:
//   - Invokes lib/decompose (external black-box program)
//   - Converts vertex ordering to edge ordering via convertEdgePermutation
//   - Outputs .grh file in the same format as input (p edge header + e lines)
//   - Converts internal 0-indexed vertices back to 1-indexed for output
//   - Does NOT modify the decompose algorithm itself
//
// プロジェクト内での責務:
//   - lib/decompose（外部ブラックボックスプログラム）を呼び出し
//   - convertEdgePermutation により頂点順序を辺順序に変換
//   - 入力と同じ形式（p edge ヘッダー + e 行）で .grh ファイルを出力
//   - 内部の 0-indexed 頂点を出力用に 1-indexed に変換
//   - decompose アルゴリズム自体は変更しない
//
// Phase 1 における位置づけ:
//   Core binary for Phase 1 edge relabeling.
//   Called by Python's decompose_runner.py via subprocess.
//   Phase 1 辺ラベル貼り直しのコアバイナリ。
//   Python の decompose_runner.py から subprocess 経由で呼び出される。
//
// ============================================================================

#include <iostream>
#include "../../../lib/decompose/graph.cpp"
#include "../../../lib/decompose/decompose.cpp"
#include "../../../lib/decompose/convertEdgePermutation.cpp"

using namespace std;

// ============================================================================
// main function
// ============================================================================
//
// Input:
//   .grh file from stdin (p edge header + e lines, 1-indexed vertices)
//
// 入力:
//   stdin からの .grh ファイル（p edge ヘッダー + e 行、1-indexed 頂点）
//
// Output:
//   Optimized .grh file to stdout (same format, reordered edges)
//
// 出力:
//   stdout への最適化された .grh ファイル（同じ形式、辺の順序が変更）
//
// Processing:
//   1. Read graph from stdin (readGraph converts 1-indexed to 0-indexed internally)
//   2. Run decompose with time limit 30s and beam width 60
//   3. Convert vertex ordering to edge ordering
//   4. Validate edge count consistency
//   5. Output header and edges (convert back to 1-indexed)
//
// 処理:
//   1. stdin からグラフを読み込み（readGraph が内部で 1-indexed を 0-indexed に変換）
//   2. 時間制限 30 秒、ビーム幅 60 で decompose を実行
//   3. 頂点順序を辺順序に変換
//   4. 辺数の一貫性を検証
//   5. ヘッダーと辺を出力（1-indexed に変換し直す）
//
// ============================================================================
int main() {
    // 標準入力からグラフを読み込む
    // Read graph from stdin
    Graph G = readGraph();
    
    // パス分解を実行（時間制限: 30秒、ビーム幅: 60）
    // Run path decomposition (time limit: 30s, beam width: 60)
    auto res = decompose(G, 30.0, 60);
    
    // 頂点順序から辺順序を計算
    // Convert vertex ordering to edge ordering
    vector<pair<int, int>> edgePermutation = convertEdgePermutation(G, res);
    
    // 辺数の検証
    // Validate edge count
    if (edgePermutation.size() != G.numEdges()) {
        cerr << "Error: edgePermutation size (" << edgePermutation.size() 
             << ") != G.numEdges() (" << G.numEdges() << ")" << endl;
        return 1;
    }
    
    // ヘッダーを出力（p edge <頂点数> <辺数>）
    // Output header (p edge <num_vertices> <num_edges>)
    cout << "p edge " << G.numVertices() << ' ' << edgePermutation.size() << endl;
    
    // 最適化された辺順序を出力（e u v 形式、1-indexed）
    // Output optimized edge ordering (e u v format, 1-indexed)
    for (size_t i = 0; i < edgePermutation.size(); ++i) {
        int u = edgePermutation[i].first;
        int v = edgePermutation[i].second;
        cout << "e " << u+1 << ' ' << v+1 << endl;
    }
    
    return 0;
}
