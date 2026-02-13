// ============================================================================
// main.cpp
// ============================================================================
//
// What this file does:
//   Phase 4 + Phase 5 + Phase 6 main program:
//   - Phase 4: Enumerates spanning trees using ZDD
//   - Phase 5: Filters out overlapping unfoldings (optional)
//   - Phase 6: Counts nonisomorphic unfoldings via Burnside's lemma (optional)
//   Reads polyhedron.grh, optionally reads edge_sets.jsonl (MOPEs) and
//   automorphisms.json, constructs ZDD, applies filtering, outputs counts
//   in JSON format.
//
// このファイルの役割:
//   Phase 4 + Phase 5 + Phase 6 メインプログラム:
//   - Phase 4: ZDD を用いて全域木を列挙
//   - Phase 5: 重なりを持つ展開図をフィルタリング（オプション）
//   - Phase 6: Burnside の補題で非同型展開図を数え上げ（オプション）
//   polyhedron.grh を読み込み、オプションで edge_sets.jsonl と
//   automorphisms.json を読み込み、ZDD を構築・フィルタリングし、
//   個数を JSON 形式で出力。
//
// Responsibility in the project:
//   - Phase 4: Loads graph, constructs spanning tree ZDD
//   - Phase 5: Loads MOPEs, applies subsetting filters iteratively
//   - Phase 6: Loads automorphisms, applies Burnside's lemma on ZDD
//   - Measures timing for each phase separately
//   - Outputs structured results in JSON format
//
// プロジェクト内での責務:
//   - Phase 4: グラフを読み込み、全域木 ZDD を構築
//   - Phase 5: MOPE を読み込み、subsetting フィルタを反復適用
//   - Phase 6: 自己同型を読み込み、ZDD 上で Burnside の補題を適用
//   - 各フェーズの時間を個別に計測
//   - 構造化された結果を JSON 形式で出力
//
// Phase 4+5+6 における位置づけ:
//   Core binary for Phase 4, Phase 5, and Phase 6.
//   Called by Python's cli.py via subprocess.
//   Phase 4, Phase 5, Phase 6 のコアバイナリ。
//   Python の cli.py から subprocess 経由で呼び出される。
//
// Usage:
//   Phase 4 only:     ./spanning_tree_zdd <polyhedron.grh>
//   Phase 4+5:        ./spanning_tree_zdd <polyhedron.grh> <edge_sets.jsonl>
//   Phase 4+6:        ./spanning_tree_zdd <polyhedron.grh> --automorphisms <automorphisms.json>
//   Phase 4+5+6:      ./spanning_tree_zdd <polyhedron.grh> <edge_sets.jsonl> --automorphisms <automorphisms.json>
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
#include <algorithm>
#include <tdzdd/DdStructure.hpp>
#include <tdzdd/util/Graph.hpp>
#include "SpanningTree.hpp"
#include "BigUInt.hpp"
#include "UnfoldingFilter.hpp"
#include "SymmetryFilter.hpp"

using tdzdd::Graph;
using namespace std;
using namespace std::chrono;

// ============================================================================
// Big integer string arithmetic
// 大整数文字列演算
// ============================================================================

// ============================================================================
// bigint_add
// ============================================================================
//
// Add two non-negative integers represented as strings.
// 文字列で表された 2 つの非負整数を加算。
//
// ============================================================================
string bigint_add(const string& a, const string& b) {
    string result;
    int carry = 0;
    int i = (int)a.size() - 1;
    int j = (int)b.size() - 1;

    while (i >= 0 || j >= 0 || carry) {
        int sum = carry;
        if (i >= 0) sum += a[i--] - '0';
        if (j >= 0) sum += b[j--] - '0';
        result += (char)('0' + sum % 10);
        carry = sum / 10;
    }

    reverse(result.begin(), result.end());
    return result;
}

// ============================================================================
// bigint_divide
// ============================================================================
//
// Divide a non-negative integer (string) by a small positive integer.
// Returns quotient as string. Remainder is stored in `remainder` parameter.
//
// 文字列で表された非負整数を小さい正の整数で割る。
// 商を文字列として返す。余りは `remainder` パラメータに格納。
//
// ============================================================================
string bigint_divide(const string& a, int b, int& remainder) {
    string result;
    long long rem = 0;
    for (char c : a) {
        rem = rem * 10 + (c - '0');
        result += (char)('0' + (int)(rem / b));
        rem %= b;
    }
    remainder = (int)rem;

    // Remove leading zeros
    // 先頭のゼロを削除
    size_t start = result.find_first_not_of('0');
    if (start == string::npos) return "0";
    return result.substr(start);
}

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
// ============================================================================
set<int> extract_edges_from_json(const string& json_line) {
    set<int> edges;

    size_t start = json_line.find('[');
    size_t end = json_line.find(']');

    if (start == string::npos || end == string::npos) {
        return edges;
    }

    string edge_list = json_line.substr(start + 1, end - start - 1);

    stringstream ss(edge_list);
    string token;
    while (getline(ss, token, ',')) {
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
//
// この処理の内容:
//   edge_sets.jsonl を読み込み、全ての MOPE 辺集合を抽出。
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
        if (line.empty()) continue;

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
// load_automorphisms
// ============================================================================
//
// What this does:
//   Read automorphisms.json and extract edge permutations and group order.
//   Format: {"group_order": N, "edge_permutations": [[...], [...], ...]}
//
// この処理の内容:
//   automorphisms.json を読み込み、辺置換と群位数を抽出。
//   形式: {"group_order": N, "edge_permutations": [[...], [...], ...]}
//
// ============================================================================
bool load_automorphisms(
    const string& automorphisms_file,
    int& group_order,
    vector<vector<int>>& edge_permutations
) {
    ifstream file(automorphisms_file);
    if (!file.is_open()) {
        cerr << "Error: Could not open " << automorphisms_file << endl;
        return false;
    }

    // Read entire file into string
    // ファイル全体を文字列に読み込み
    string content((istreambuf_iterator<char>(file)),
                    istreambuf_iterator<char>());
    file.close();

    // Extract group_order
    // group_order を抽出
    {
        size_t pos = content.find("\"group_order\"");
        if (pos == string::npos) {
            cerr << "Error: group_order not found in " << automorphisms_file << endl;
            return false;
        }
        pos = content.find(':', pos);
        if (pos == string::npos) return false;
        pos++;
        // Skip whitespace
        while (pos < content.size() && (content[pos] == ' ' || content[pos] == '\t')) pos++;
        string num_str;
        while (pos < content.size() && content[pos] >= '0' && content[pos] <= '9') {
            num_str += content[pos++];
        }
        group_order = stoi(num_str);
    }

    // Extract edge_permutations
    // edge_permutations を抽出
    {
        size_t pos = content.find("\"edge_permutations\"");
        if (pos == string::npos) {
            cerr << "Error: edge_permutations not found in " << automorphisms_file << endl;
            return false;
        }
        pos = content.find('[', pos);
        if (pos == string::npos) return false;
        pos++; // Skip outer '['

        // Parse each inner array
        // 各内部配列をパース
        while (pos < content.size()) {
            // Find next '['
            pos = content.find('[', pos);
            if (pos == string::npos) break;

            size_t end = content.find(']', pos);
            if (end == string::npos) break;

            // Extract numbers between '[' and ']'
            string arr_str = content.substr(pos + 1, end - pos - 1);
            vector<int> perm;
            stringstream ss(arr_str);
            string token;
            while (getline(ss, token, ',')) {
                size_t first = token.find_first_not_of(" \t\n\r");
                size_t last = token.find_last_not_of(" \t\n\r");
                if (first != string::npos && last != string::npos) {
                    token = token.substr(first, last - first + 1);
                    if (!token.empty()) {
                        perm.push_back(stoi(token));
                    }
                }
            }

            if (!perm.empty()) {
                edge_permutations.push_back(perm);
            }

            pos = end + 1;

            // Check if we've reached the outer ']'
            // 外側の ']' に到達したかチェック
            size_t next_bracket = content.find_first_of("[]", pos);
            if (next_bracket != string::npos && content[next_bracket] == ']') {
                // Check if there's no '[' before this ']'
                size_t next_open = content.find('[', pos);
                if (next_open == string::npos || next_open > next_bracket) {
                    break; // End of outer array
                }
            }
        }
    }

    return true;
}

// ============================================================================
// run_filtering_with_bitmask
// ============================================================================
//
// What this does:
//   Template function to run Phase 5 filtering with specific BitMask type.
//   Uses UnfoldingFilter<BitMask> for filtering.
//
// この処理の内容:
//   特定の BitMask 型で Phase 5 フィルタリングを実行するテンプレート関数。
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
    for (int i = 0; i < (int)MOPEs.size(); ++i) {
        cerr << (i + 1) << "/" << total_mopes << endl;

        UnfoldingFilter<BitMask> filter(num_edges, MOPEs[i]);
        dd.zddSubset(filter);
        dd.zddReduce();
    }
}

// ============================================================================
// run_burnside_with_bitmask
// ============================================================================
//
// What this does:
//   Apply Burnside's lemma on the ZDD using SymmetryFilter<BitMask>.
//   For each automorphism g, count g-invariant spanning trees |T_g|.
//   Sum all |T_g| and divide by |Aut(Γ)| to get nonisomorphic count.
//
// この処理の内容:
//   SymmetryFilter<BitMask> を用いて ZDD 上で Burnside の補題を適用。
//   各自己同型 g に対して g-不変全域木 |T_g| を数える。
//   全 |T_g| を合計し |Aut(Γ)| で割って非同型個数を得る。
//
// Template Parameters:
//   BitMask: Type for bitmask operations (uint64_t or BigUInt<N>)
//            Used by SymmetryFilter for orbit decision tracking.
//
// テンプレートパラメータ:
//   BitMask: ビットマスク演算の型（uint64_t または BigUInt<N>）
//            SymmetryFilter が軌道判定の追跡に使用。
//
// Parameters:
//   dd: ZDD structure (NOT modified - copied for each automorphism)
//   edge_permutations: List of edge permutations (one per automorphism)
//   group_order: |Aut(Γ)|
//   num_edges: Total number of edges
//   invariant_counts: Output vector of |T_g| strings
//   burnside_sum: Output sum of all |T_g|
//   nonisomorphic_count: Output: burnside_sum / group_order
//
// パラメータ:
//   dd: ZDD 構造（変更されない - 各自己同型ごとにコピー）
//   edge_permutations: 辺置換のリスト（自己同型1つにつき1つ）
//   group_order: |Aut(Γ)|
//   num_edges: 全辺数
//   invariant_counts: 出力: |T_g| 文字列のベクトル
//   burnside_sum: 出力: 全 |T_g| の合計
//   nonisomorphic_count: 出力: burnside_sum / group_order
//
// ============================================================================
template<typename BitMask>
void run_burnside_with_bitmask(
    const tdzdd::DdStructure<2>& dd,
    const vector<vector<int>>& edge_permutations,
    int group_order,
    int num_edges,
    vector<string>& invariant_counts,
    string& burnside_sum,
    string& nonisomorphic_count
) {
    burnside_sum = "0";
    int total = edge_permutations.size();

    for (int i = 0; i < total; ++i) {
        cerr << "Phase 6: automorphism " << (i + 1) << "/" << total << endl;

        const vector<int>& perm = edge_permutations[i];

        // Check if this is the identity permutation
        // 恒等置換かチェック
        bool is_identity = true;
        for (int j = 0; j < num_edges; ++j) {
            if (perm[j] != j) {
                is_identity = false;
                break;
            }
        }

        string count;
        if (is_identity) {
            // Identity: all spanning trees are invariant
            // 恒等置換: 全ての全域木が不変
            count = dd.zddCardinality();
            cerr << "  (identity) |T_g| = " << count << endl;
        } else {
            // Non-identity: apply SymmetryFilter<BitMask>
            // 非恒等置換: SymmetryFilter<BitMask> を適用
            tdzdd::DdStructure<2> dd_copy(dd);
            SymmetryFilter<BitMask> filter(num_edges, perm);
            dd_copy.zddSubset(filter);
            dd_copy.zddReduce();
            count = dd_copy.zddCardinality();
            cerr << "  |T_g| = " << count << endl;
        }

        invariant_counts.push_back(count);
        burnside_sum = bigint_add(burnside_sum, count);
    }

    // Divide by group order
    // 群位数で割る
    int remainder = 0;
    nonisomorphic_count = bigint_divide(burnside_sum, group_order, remainder);

    if (remainder != 0) {
        cerr << "WARNING: Burnside sum " << burnside_sum
             << " is not divisible by group order " << group_order
             << " (remainder = " << remainder << ")" << endl;
        cerr << "This indicates a bug in the computation!" << endl;
    }
}

// ============================================================================
// main function
// ============================================================================
//
// Usage:
//   Phase 4 only:     ./spanning_tree_zdd <polyhedron.grh>
//   Phase 4+5:        ./spanning_tree_zdd <polyhedron.grh> <edge_sets.jsonl>
//   Phase 4+6:        ./spanning_tree_zdd <polyhedron.grh> --automorphisms <file.json>
//   Phase 4+5+6:      ./spanning_tree_zdd <polyhedron.grh> <edge_sets.jsonl> --automorphisms <file.json>
//
// ============================================================================
int main(int argc, char **argv) {
    // ========================================================================
    // Argument parsing
    // 引数解析
    // ========================================================================
    string grh_file;
    string edge_sets_file;
    string automorphisms_file;

    for (int i = 1; i < argc; i++) {
        string arg = argv[i];
        if (arg == "--automorphisms" && i + 1 < argc) {
            automorphisms_file = argv[++i];
        } else if (grh_file.empty()) {
            grh_file = arg;
        } else if (edge_sets_file.empty()) {
            edge_sets_file = arg;
        } else {
            cerr << "Error: Unexpected argument: " << arg << endl;
            cerr << "Usage: " << argv[0]
                 << " <polyhedron.grh> [edge_sets.jsonl] [--automorphisms automorphisms.json]"
                 << endl;
            return 1;
        }
    }

    if (grh_file.empty()) {
        cerr << "Usage: " << argv[0]
             << " <polyhedron.grh> [edge_sets.jsonl] [--automorphisms automorphisms.json]"
             << endl;
        return 1;
    }

    bool apply_filter = !edge_sets_file.empty();
    bool apply_burnside = !automorphisms_file.empty();

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
        cerr << "Error: Edge count (" << num_edges
             << ") exceeds maximum supported (448)." << endl;
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
        vector<set<int>> MOPEs = load_mopes_from_edge_sets(edge_sets_file);
        num_mopes = MOPEs.size();

        if (num_mopes == 0) {
            cerr << "Warning: No MOPEs loaded from " << edge_sets_file << endl;
        } else {
            auto start_subset = high_resolution_clock::now();

            if (num_edges <= 64) {
                run_filtering_with_bitmask<uint64_t>(dd, MOPEs, num_edges);
            } else if (num_edges <= 128) {
                run_filtering_with_bitmask<BigUInt<2>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 192) {
                run_filtering_with_bitmask<BigUInt<3>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 256) {
                run_filtering_with_bitmask<BigUInt<4>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 320) {
                run_filtering_with_bitmask<BigUInt<5>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 384) {
                run_filtering_with_bitmask<BigUInt<6>>(dd, MOPEs, num_edges);
            } else if (num_edges <= 448) {
                run_filtering_with_bitmask<BigUInt<7>>(dd, MOPEs, num_edges);
            } else {
                cerr << "Error: Edge count exceeds maximum supported" << endl;
                return 1;
            }

            auto end_subset = high_resolution_clock::now();
            subset_time_ms = duration<double, milli>(end_subset - start_subset).count();

            non_overlapping_count = dd.zddCardinality();
        }
    }

    // ========================================================================
    // Phase 6: Nonisomorphic Counting (Optional)
    // Phase 6: 非同型数え上げ（オプション）
    // ========================================================================

    int group_order = 0;
    vector<string> invariant_counts;
    string burnside_sum;
    string nonisomorphic_count;
    double burnside_time_ms = 0.0;

    if (apply_burnside) {
        // Load automorphisms
        // 自己同型を読み込み
        vector<vector<int>> edge_permutations;
        if (!load_automorphisms(automorphisms_file, group_order, edge_permutations)) {
            cerr << "Error: Failed to load automorphisms from "
                 << automorphisms_file << endl;
            return 1;
        }

        cerr << "Loaded " << edge_permutations.size()
             << " automorphisms (group order " << group_order << ")" << endl;

        // Verify consistency
        // 一貫性の検証
        if ((int)edge_permutations.size() != group_order) {
            cerr << "Warning: Number of permutations (" << edge_permutations.size()
                 << ") != group_order (" << group_order << ")" << endl;
        }

        for (const auto& perm : edge_permutations) {
            if ((int)perm.size() != num_edges) {
                cerr << "Error: Permutation size (" << perm.size()
                     << ") != num_edges (" << num_edges << ")" << endl;
                return 1;
            }
        }

        // Apply Burnside's lemma on the current ZDD
        // (which is the Phase 4 ZDD if Phase 5 was not applied,
        //  or the Phase 5 ZDD if Phase 5 was applied)
        // 現在の ZDD に Burnside の補題を適用
        // （Phase 5 未適用なら Phase 4 の ZDD、
        //   Phase 5 適用済みなら Phase 5 の ZDD）
        auto start_burnside = high_resolution_clock::now();

        // ====================================================================
        // Bit Width Selection for SymmetryFilter
        // SymmetryFilter のビット幅選択
        // ====================================================================
        //
        // Select BitMask type based on edge count (>= number of orbits).
        // 辺数（>= 軌道数）に基づいて BitMask 型を選択。
        //
        // ====================================================================
        if (num_edges <= 64) {
            run_burnside_with_bitmask<uint64_t>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 128) {
            run_burnside_with_bitmask<BigUInt<2>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 192) {
            run_burnside_with_bitmask<BigUInt<3>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 256) {
            run_burnside_with_bitmask<BigUInt<4>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 320) {
            run_burnside_with_bitmask<BigUInt<5>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 384) {
            run_burnside_with_bitmask<BigUInt<6>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else if (num_edges <= 448) {
            run_burnside_with_bitmask<BigUInt<7>>(
                dd, edge_permutations, group_order, num_edges,
                invariant_counts, burnside_sum, nonisomorphic_count);
        } else {
            cerr << "Error: Edge count exceeds maximum supported" << endl;
            return 1;
        }

        auto end_burnside = high_resolution_clock::now();
        burnside_time_ms = duration<double, milli>(end_burnside - start_burnside).count();
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
    cout << "    \"build_time_ms\": " << fixed << setprecision(2)
         << build_time_ms << "," << endl;
    cout << "    \"count_time_ms\": " << fixed << setprecision(2)
         << count_time_ms << "," << endl;
    cout << "    \"spanning_tree_count\": \"" << spanning_tree_count << "\""
         << endl;
    cout << "  }," << endl;

    // Phase 5 results
    // Phase 5 の結果
    cout << "  \"phase5\": {" << endl;
    cout << "    \"filter_applied\": " << (apply_filter ? "true" : "false");

    if (apply_filter) {
        cout << "," << endl;
        cout << "    \"num_mopes\": " << num_mopes << "," << endl;
        cout << "    \"subset_time_ms\": " << fixed << setprecision(2)
             << subset_time_ms << "," << endl;
        cout << "    \"non_overlapping_count\": \"" << non_overlapping_count
             << "\"" << endl;
    } else {
        cout << endl;
    }

    cout << "  }";

    // Phase 6 results
    // Phase 6 の結果
    if (apply_burnside) {
        cout << "," << endl;
        cout << "  \"phase6\": {" << endl;
        cout << "    \"burnside_applied\": true," << endl;
        cout << "    \"group_order\": " << group_order << "," << endl;
        cout << "    \"burnside_time_ms\": " << fixed << setprecision(2)
             << burnside_time_ms << "," << endl;
        cout << "    \"burnside_sum\": \"" << burnside_sum << "\"," << endl;
        cout << "    \"nonisomorphic_count\": \"" << nonisomorphic_count
             << "\"," << endl;
        cout << "    \"invariant_counts\": [" << endl;
        for (size_t i = 0; i < invariant_counts.size(); ++i) {
            cout << "      \"" << invariant_counts[i] << "\"";
            if (i + 1 < invariant_counts.size()) cout << ",";
            cout << endl;
        }
        cout << "    ]" << endl;
        cout << "  }";
    }

    cout << endl;
    cout << "}" << endl;

    return 0;
}
