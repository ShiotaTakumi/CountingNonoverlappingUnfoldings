// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   Phase 4 + Phase 5 main program:
//   - Phase 4: Enumerates spanning trees using ZDD
//   - Phase 5: Filters out overlapping unfoldings (optional)
//   Reads polyhedron.grh, optionally reads edge_sets.jsonl (MOPEs),
//   constructs ZDD, applies filtering, outputs counts in JSON format.
//
// このファイルの役割:
//   Phase 4 + Phase 5 メインプログラム:
//   - Phase 4: ZDD を用いて全域木を列挙
//   - Phase 5: 重なりを持つ展開図をフィルタリング（オプション）
//   polyhedron.grh を読み込み、オプションで edge_sets.jsonl（MOPE）を読み込み、
//   ZDD を構築し、フィルタリングを適用し、個数を JSON 形式で出力。
//
// Responsibility in the project:
//   - Phase 4: Loads graph, constructs spanning tree ZDD
//   - Phase 5: Loads MOPEs, applies subsetting filters iteratively
//   - Measures timing for each phase separately
//   - Outputs structured results in JSON format
//
// プロジェクト内での責務:
//   - Phase 4: グラフを読み込み、全域木 ZDD を構築
//   - Phase 5: MOPE を読み込み、subsetting フィルタを反復適用
//   - 各フェーズの時間を個別に計測
//   - 構造化された結果を JSON 形式で出力
//
// Phase 4+5 における位置づけ:
//   Core binary for Phase 4 and Phase 5.
//   Called by Python's cli.py via subprocess.
//   Phase 4 と Phase 5 のコアバイナリ。
//   Python の cli.py から subprocess 経由で呼び出される。
//
// ============================================================================

#include <iostream>
#include <fstream>
#include <sstream>
#include <chrono>
#include <string>
#include <iomanip>
#include <vector>
#include <set>
#include <tdzdd/DdStructure.hpp>
#include <tdzdd/util/Graph.hpp>
#include "SpanningTree.hpp"
#include "BigUInt.hpp"
#include "UnfoldingFilter.hpp"

using tdzdd::Graph;
using namespace std;
using namespace std::chrono;

// ============================================================================
// extract_edges_from_json
// ============================================================================
//
// What this does:
//   Parse {"edges": [0, 1, 2, ...]} from a JSON line.
//   Extract edge IDs as a set of integers.
//
// この処理の内容:
//   JSON 行から {"edges": [0, 1, 2, ...]} をパース。
//   辺 ID を整数の集合として抽出。
//
// Parameters:
//   json_line: Single line from edge_sets.jsonl
//
// パラメータ:
//   json_line: edge_sets.jsonl からの 1 行
//
// Returns:
//   Set of edge IDs
//
// 戻り値:
//   辺 ID の集合
//
// Implementation:
//   Simple string parsing without external JSON library.
//   Finds "[" and "]", extracts numbers between them.
//
// 実装:
//   外部 JSON ライブラリを使わない簡易文字列パース。
//   "[" と "]" を見つけ、その間の数値を抽出。
//
// ============================================================================
set<int> extract_edges_from_json(const string& json_line) {
    set<int> edges;

    // Find the "[" and "]" positions
    // "[" と "]" の位置を探す
    size_t start = json_line.find('[');
    size_t end = json_line.find(']');

    if (start == string::npos || end == string::npos) {
        return edges;  // Return empty set if brackets not found / 括弧が見つからない場合は空集合を返す
    }

    // Extract the substring containing edge IDs
    // 辺 ID を含む部分文字列を抽出
    string edge_list = json_line.substr(start + 1, end - start - 1);

    // Parse comma-separated integers
    // カンマ区切りの整数をパース
    stringstream ss(edge_list);
    string token;
    while (getline(ss, token, ',')) {
        // Trim whitespace
        // 空白を削除
        size_t first = token.find_first_not_of(" \t");
        size_t last = token.find_last_not_of(" \t");

        if (first != string::npos && last != string::npos) {
            token = token.substr(first, last - first + 1);
            if (!token.empty()) {
                edges.insert(stoi(token));
            }
        }
    }

    return edges;
}

// ============================================================================
// load_mopes_from_edge_sets
// ============================================================================
//
// What this does:
//   Read edge_sets.jsonl and extract all MOPE edge sets.
//   Each line in the file represents one MOPE.
//
// この処理の内容:
//   edge_sets.jsonl を読み込み、全ての MOPE 辺集合を抽出。
//   ファイルの各行が 1 つの MOPE を表す。
//
// Parameters:
//   edge_sets_file: Path to unfoldings_edge_sets.jsonl
//
// パラメータ:
//   edge_sets_file: unfoldings_edge_sets.jsonl へのパス
//
// Returns:
//   Vector of edge sets, one for each MOPE
//
// 戻り値:
//   MOPE ごとの辺集合のベクトル
//
// Example:
//   For s12L, this returns 72 edge sets (72 MOPEs).
//   For n20, this returns 40 edge sets (40 MOPEs).
//
// 例:
//   s12L の場合、72 個の辺集合（72 個の MOPE）を返す。
//   n20 の場合、40 個の辺集合（40 個の MOPE）を返す。
//
// ============================================================================
vector<set<int>> load_mopes_from_edge_sets(const string& edge_sets_file) {
    vector<set<int>> MOPEs;

    ifstream file(edge_sets_file);
    if (!file.is_open()) {
        cerr << "Error: Could not open " << edge_sets_file << endl;
        return MOPEs;
    }

    string line;
    int line_num = 0;
    while (getline(file, line)) {
        line_num++;

        // Skip empty lines
        // 空行をスキップ
        if (line.empty()) continue;

        // Parse {"edges": [0, 1, 2, ...]}
        // {"edges": [0, 1, 2, ...]} をパース
        set<int> edges = extract_edges_from_json(line);

        if (!edges.empty()) {
            MOPEs.push_back(edges);
        } else {
            cerr << "Warning: Empty edge set at line " << line_num << endl;
        }
    }

    file.close();
    return MOPEs;
}

// ============================================================================
// run_filtering_with_bitmask
// ============================================================================
//
// What this does:
//   Template function to run Phase 5 filtering with specific BitMask type.
//   Uses UnfoldingFilter<BitMask> for filtering.
//   Displays progress for each MOPE.
//
// この処理の内容:
//   特定の BitMask 型で Phase 5 フィルタリングを実行するテンプレート関数。
//   フィルタリングに UnfoldingFilter<BitMask> を使用。
//   各 MOPE の進捗を表示。
//
// Template Parameters:
//   BitMask: Type for bitmask operations (uint64_t or BigUInt<N>)
//
// テンプレートパラメータ:
//   BitMask: ビットマスク演算の型（uint64_t または BigUInt<N>）
//
// Parameters:
//   dd: ZDD structure to filter (modified in-place)
//   MOPEs: Vector of MOPE edge sets
//   num_edges: Total number of edges in the graph
//
// パラメータ:
//   dd: フィルタする ZDD 構造（インプレース変更）
//   MOPEs: MOPE 辺集合のベクトル
//   num_edges: グラフの全辺数
//
// CRITICAL:
//   The subsetting loop structure must NOT be changed.
//   This is the verified algorithm from Reserch2024.
//
// 重要:
//   subsetting ループ構造は変更してはいけない。
//   これは Reserch2024 の検証済みアルゴリズム。
//
// ============================================================================
template<typename BitMask>
void run_filtering_with_bitmask(
    tdzdd::DdStructure<2>& dd,
    const vector<set<int>>& MOPEs,
    int num_edges
) {
    int total_mopes = MOPEs.size();
    
    // CRITICAL: This loop structure must NOT be changed
    // 重要: このループ構造は変更してはいけない
    // For each MOPE, apply subsetting to exclude overlapping unfoldings
    // 各 MOPE に対して、subsetting を適用し重なりを持つ展開図を除外
    for (int i = 0; i < MOPEs.size(); ++i) {
        // Display progress for user feedback
        // ユーザーフィードバック用に進捗を表示
        cerr << (i + 1) << "/" << total_mopes << endl;
        
        UnfoldingFilter<BitMask> filter(num_edges, MOPEs[i]);
        dd.zddSubset(filter);
        dd.zddReduce();
    }
}
// ============================================================================
// main function
// ============================================================================
//
// Input:
//   1. polyhedron.grh file path (required, argv[1])
//      Format: No header, one edge per line "v1 v2", 0-indexed vertices
//   2. edge_sets.jsonl file path (optional, argv[2])
//      Format: Each line is {"edges": [...]}, one MOPE per line
//
// 入力:
//   1. polyhedron.grh ファイルパス（必須、argv[1]）
//      形式: ヘッダーなし、1行1辺 "v1 v2"、0-indexed 頂点
//   2. edge_sets.jsonl ファイルパス（オプション、argv[2]）
//      形式: 各行は {"edges": [...]}, 1行1MOPE
//
// Output:
//   JSON to stdout with graph info, timing, and counts for Phase 4 and Phase 5
//
// 出力:
//   stdout に JSON 形式でグラフ情報、時間、Phase 4 と Phase 5 の個数を出力
//
// Processing:
//   Phase 4:
//     1. Load graph from .grh file using TdZdd's Graph::readEdges()
//     2. Construct ZDD for spanning trees with timing measurement
//     3. Calculate cardinality (all spanning trees count)
//   Phase 5 (optional, if edge_sets.jsonl is provided):
//     4. Load MOPEs from edge_sets.jsonl
//     5. For each MOPE, apply zddSubset() to filter out overlapping unfoldings
//     6. Calculate final cardinality (non-overlapping unfoldings count)
//
// 処理:
//   Phase 4:
//     1. TdZdd の Graph::readEdges() で .grh ファイルからグラフを読み込み
//     2. 時間計測しながら全域木の ZDD を構築
//     3. カーディナリティ計算（全全域木個数）
//   Phase 5（オプション、edge_sets.jsonl が指定された場合）:
//     4. edge_sets.jsonl から MOPE を読み込み
//     5. 各 MOPE に対して zddSubset() を適用し、重なりを持つ展開図を除外
//     6. 最終カーディナリティ計算（非重複展開図個数）
//
// ============================================================================
int main(int argc, char **argv) {
    // コマンドライン引数チェック
    // Check command-line arguments
    if (argc < 2 || argc > 3) {
        cerr << "Usage: " << argv[0] << " <polyhedron.grh> [edge_sets.jsonl]" << endl;
        cerr << "  polyhedron.grh: Required, graph file" << endl;
        cerr << "  edge_sets.jsonl: Optional, MOPE file for Phase 5 filtering" << endl;
        return 1;
    }

    string grh_file = string(argv[1]);
    string edge_sets_file = (argc == 3) ? string(argv[2]) : "";
    bool apply_filter = !edge_sets_file.empty();

    // ========================================================================
    // Phase 4: Spanning Tree Enumeration
    // Phase 4: 全域木列挙
    // ========================================================================

    // グラフの読み込み
    // Load graph from file
    Graph G;
    G.readEdges(grh_file);

    int num_vertices = G.vertexSize();
    int num_edges = G.edgeSize();

    // Check maximum supported edge count
    // サポートする最大辺数をチェック
    if (num_edges > 448) {
        cerr << "Error: Edge count (" << num_edges << ") exceeds maximum supported (448)." << endl;
        cerr << "To support more edges, extend the bit width selection in main.cpp" << endl;
        return 1;
    }

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
    string spanning_tree_count = dd.zddCardinality();
    auto end_count = high_resolution_clock::now();
    double count_time_ms = duration<double, milli>(end_count - start_count).count();

    // ========================================================================
    // Phase 5: Filtering (Optional)
    // Phase 5: フィルタリング（オプション）
    // ========================================================================

    string non_overlapping_count = spanning_tree_count;
    int num_mopes = 0;
    double subset_time_ms = 0.0;

    if (apply_filter) {
        // MOPE リストの読み込み
        // Load MOPE list from edge_sets.jsonl
        vector<set<int>> MOPEs = load_mopes_from_edge_sets(edge_sets_file);
        num_mopes = MOPEs.size();

        if (num_mopes == 0) {
            cerr << "Warning: No MOPEs loaded from " << edge_sets_file << endl;
        } else {
            // Subsetting ループ（時間計測）
            // Subsetting loop (measure time)
            auto start_subset = high_resolution_clock::now();

            // ====================================================================
            // Bit Width Selection / ビット幅選択
            // ====================================================================
            //
            // Select appropriate BitMask type based on edge count.
            // Automatically choose the smallest type that can hold all edges.
            //
            // 辺数に基づいて適切な BitMask 型を選択。
            // 全辺を保持できる最小の型を自動選択。
            //
            // Performance:
            //   - ≤64:  uint64_t (~5-10% faster than BigUInt<1>)
            //   - ≤128: BigUInt<2> (baseline)
            //   - ≤192: BigUInt<3> (~5% slower than BigUInt<2>)
            //   - ≤256: BigUInt<4> (~10% slower than BigUInt<2>)
            //   - etc.
            //
            // パフォーマンス:
            //   - ≤64:  uint64_t（BigUInt<1> より約 5-10% 速い）
            //   - ≤128: BigUInt<2>（ベースライン）
            //   - ≤192: BigUInt<3>（BigUInt<2> より約 5% 遅い）
            //   - ≤256: BigUInt<4>（BigUInt<2> より約 10% 遅い）
            //   - など
            //
            // ====================================================================

            if (num_edges <= 64) {
                // 1-64 edges: uint64_t (native type, fastest)
                // 1-64 辺: uint64_t（ネイティブ型、最速）
                run_filtering_with_bitmask<uint64_t>(dd, MOPEs, num_edges);
            } else if (num_edges <= 128) {
                // 65-128 edges: BigUInt<2> (2 * 64 = 128 bits)
                // 65-128 辺: BigUInt<2>（2 * 64 = 128 ビット）
                run_filtering_with_bitmask<BigUInt<2>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 192) {
                // 129-192 edges: BigUInt<3> (3 * 64 = 192 bits)
                // 129-192 辺: BigUInt<3>（3 * 64 = 192 ビット）
                run_filtering_with_bitmask<BigUInt<3>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 256) {
                // 193-256 edges: BigUInt<4> (4 * 64 = 256 bits)
                // 193-256 辺: BigUInt<4>（4 * 64 = 256 ビット）
                run_filtering_with_bitmask<BigUInt<4>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 320) {
                // 257-320 edges: BigUInt<5> (5 * 64 = 320 bits)
                // 257-320 辺: BigUInt<5>（5 * 64 = 320 ビット）
                run_filtering_with_bitmask<BigUInt<5>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 384) {
                // 321-384 edges: BigUInt<6> (6 * 64 = 384 bits)
                // 321-384 辺: BigUInt<6>（6 * 64 = 384 ビット）
                run_filtering_with_bitmask<BigUInt<6>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 448) {
                // 385-448 edges: BigUInt<7> (7 * 64 = 448 bits)
                // 385-448 辺: BigUInt<7>（7 * 64 = 448 ビット）
                run_filtering_with_bitmask<BigUInt<7>>(dd, MOPEs, num_edges);
            } else {
                // This should never happen due to earlier check
                // 前のチェックでここには到達しないはず
                cerr << "Error: Edge count exceeds maximum supported" << endl;
                return 1;
            }

            auto end_subset = high_resolution_clock::now();
            subset_time_ms = duration<double, milli>(end_subset - start_subset).count();

            // 非重複展開図の個数を計算
            // Calculate non-overlapping unfoldings count
            non_overlapping_count = dd.zddCardinality();
        }
    }

    // ========================================================================
    // JSON Output
    // JSON 出力
    // ========================================================================

    cout << "{" << endl;
    cout << "  \"input_file\": \"" << grh_file << "\"," << endl;
    cout << "  \"vertices\": " << num_vertices << "," << endl;
    cout << "  \"edges\": " << num_edges << "," << endl;

    // Phase 4 results
    // Phase 4 の結果
    cout << "  \"phase4\": {" << endl;
    cout << "    \"build_time_ms\": " << fixed << setprecision(2) << build_time_ms << "," << endl;
    cout << "    \"count_time_ms\": " << fixed << setprecision(2) << count_time_ms << "," << endl;
    cout << "    \"spanning_tree_count\": \"" << spanning_tree_count << "\"" << endl;
    cout << "  }," << endl;

    // Phase 5 results
    // Phase 5 の結果
    cout << "  \"phase5\": {" << endl;
    cout << "    \"filter_applied\": " << (apply_filter ? "true" : "false");

    if (apply_filter) {
        cout << "," << endl;
        cout << "    \"num_mopes\": " << num_mopes << "," << endl;
        cout << "    \"subset_time_ms\": " << fixed << setprecision(2) << subset_time_ms << "," << endl;
        cout << "    \"non_overlapping_count\": \"" << non_overlapping_count << "\"" << endl;
    } else {
        cout << endl;
    }

    cout << "  }" << endl;
    cout << "}" << endl;

    return 0;
}
