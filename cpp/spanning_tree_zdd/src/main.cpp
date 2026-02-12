// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   Phase 4 main program: Enumerates spanning trees using ZDD.
//   Reads polyhedron.grh, constructs ZDD, outputs count in JSON format.
//
// このファイルの役割:
//   Phase 4 メインプログラム: ZDD を用いて全域木を列挙。
//   polyhedron.grh を読み込み、ZDD を構築し、個数を JSON 形式で出力。
//
// Responsibility in the project:
//   - Loads graph from Phase 3 output (polyhedron.grh)
//   - Constructs ZDD for spanning tree enumeration using TdZdd
//   - Measures ZDD construction time and cardinality calculation time
//   - Outputs structured results in JSON format
//   - Does NOT perform overlap filtering (Phase 5 responsibility)
//
// プロジェクト内での責務:
//   - Phase 3 出力（polyhedron.grh）からグラフを読み込み
//   - TdZdd を用いて全域木列挙の ZDD を構築
//   - ZDD 構築時間とカーディナリティ計算時間を計測
//   - 構造化された結果を JSON 形式で出力
//   - 重なりフィルタリングは行わない（Phase 5 の責務）
//
// Phase 4 における位置づけ:
//   Core binary for Phase 4 spanning tree enumeration.
//   Called by Python's cli.py via subprocess.
//   Phase 4 全域木列挙のコアバイナリ。
//   Python の cli.py から subprocess 経由で呼び出される。
//
// ============================================================================

#include <iostream>
#include <chrono>
#include <string>
#include <iomanip>
#include <tdzdd/DdStructure.hpp>
#include <tdzdd/util/Graph.hpp>
#include "SpanningTree.hpp"

using tdzdd::Graph;
using namespace std;
using namespace std::chrono;

// ============================================================================
// main function
// ============================================================================
//
// Input:
//   polyhedron.grh file path (command-line argument)
//   Format: No header, one edge per line "v1 v2", 0-indexed vertices
//
// 入力:
//   polyhedron.grh ファイルパス（コマンドライン引数）
//   形式: ヘッダーなし、1行1辺 "v1 v2"、0-indexed 頂点
//
// Output:
//   JSON to stdout with graph info, timing, and spanning tree count
//
// 出力:
//   stdout に JSON 形式でグラフ情報、時間、全域木個数を出力
//
// Processing:
//   1. Load graph from .grh file using TdZdd's Graph::readEdges()
//   2. Construct ZDD for spanning trees with timing measurement
//   3. Calculate cardinality (solution count) with timing measurement
//   4. Output all information in JSON format
//
// 処理:
//   1. TdZdd の Graph::readEdges() で .grh ファイルからグラフを読み込み
//   2. 時間計測しながら全域木の ZDD を構築
//   3. 時間計測しながらカーディナリティ（解の個数）を計算
//   4. すべての情報を JSON 形式で出力
//
// ============================================================================
int main(int argc, char **argv) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <path_to_polyhedron.grh>" << endl;
        return 1;
    }
    
    string input_file = string(argv[1]);
    
    // グラフの読み込み
    // Load graph from file
    Graph G;
    G.readEdges(input_file);
    
    int num_vertices = G.vertexSize();
    int num_edges = G.edgeSize();
    
    // ZDD 構築（時間計測）
    // Construct ZDD (measure time)
    auto start_build = high_resolution_clock::now();
    SpanningTree ST(G);
    tdzdd::DdStructure<2> dd(ST, true);  // true = 自動縮約 / auto-reduce
    auto end_build = high_resolution_clock::now();
    double build_time_ms = duration<double, milli>(end_build - start_build).count();
    
    // カーディナリティ計算（時間計測）
    // Calculate cardinality (measure time)
    auto start_count = high_resolution_clock::now();
    string count = dd.zddCardinality();
    auto end_count = high_resolution_clock::now();
    double count_time_ms = duration<double, milli>(end_count - start_count).count();
    
    // JSON 出力
    // Output JSON
    cout << "{" << endl;
    cout << "  \"input_file\": \"" << input_file << "\"," << endl;
    cout << "  \"vertices\": " << num_vertices << "," << endl;
    cout << "  \"edges\": " << num_edges << "," << endl;
    cout << "  \"build_time_ms\": " << fixed << setprecision(2) << build_time_ms << "," << endl;
    cout << "  \"count_time_ms\": " << fixed << setprecision(2) << count_time_ms << "," << endl;
    cout << "  \"spanning_tree_count\": \"" << count << "\"" << endl;
    cout << "}" << endl;
    
    return 0;
}
