// ============================================================================
// verify.cpp — Independent verification of Phase 6 (Burnside)
// ============================================================================
//
// Enumerates all non-overlapping spanning trees from ZDD, then applies
// automorphism-based canonical form to count nonisomorphic unfoldings.
//
// Usage:
//   ./verify <polyhedron_data_dir>
//
// Example:
//   ./verify data/polyhedra/johnson/n54
//
// ============================================================================

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <set>
#include <algorithm>

#include <tdzdd/DdStructure.hpp>
#include <tdzdd/util/Graph.hpp>
#include "SpanningTree.hpp"
#include "UnfoldingFilter.hpp"

using namespace std;

// ============================================================================
// Parse {"edges": [0, 1, 2, ...]} from a JSON line
// ============================================================================
set<int> extract_edges(const string& line) {
    set<int> edges;
    size_t start = line.find('[');
    size_t end = line.find(']');
    if (start == string::npos || end == string::npos) return edges;

    string nums = line.substr(start + 1, end - start - 1);
    stringstream ss(nums);
    string token;
    while (getline(ss, token, ',')) {
        size_t f = token.find_first_not_of(" \t");
        size_t l = token.find_last_not_of(" \t");
        if (f != string::npos && l != string::npos) {
            edges.insert(stoi(token.substr(f, l - f + 1)));
        }
    }
    return edges;
}

// ============================================================================
// Load MOPEs from edge_sets.jsonl
// ============================================================================
vector<set<int>> load_mopes(const string& path) {
    vector<set<int>> mopes;
    ifstream file(path);
    if (!file.is_open()) {
        cerr << "Error: Cannot open " << path << endl;
        return mopes;
    }
    string line;
    while (getline(file, line)) {
        if (line.empty()) continue;
        set<int> e = extract_edges(line);
        if (!e.empty()) mopes.push_back(e);
    }
    return mopes;
}

// ============================================================================
// Load automorphisms (edge permutations) from automorphisms.json
// ============================================================================
vector<vector<int>> load_automorphisms(const string& path, int& group_order) {
    vector<vector<int>> perms;
    ifstream file(path);
    if (!file.is_open()) {
        cerr << "Error: Cannot open " << path << endl;
        return perms;
    }

    string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
    file.close();

    // Extract group_order
    {
        size_t pos = content.find("\"group_order\"");
        pos = content.find(':', pos);
        pos++;
        while (pos < content.size() && (content[pos] == ' ' || content[pos] == '\t')) pos++;
        size_t end = pos;
        while (end < content.size() && isdigit(content[end])) end++;
        group_order = stoi(content.substr(pos, end - pos));
    }

    // Extract edge_permutations
    size_t pos = content.find("\"edge_permutations\"");
    pos = content.find('[', pos);
    pos++; // skip outer '['

    // Find matching outer ']' by counting brackets
    int depth = 1;
    size_t outer_end = pos;
    while (outer_end < content.size() && depth > 0) {
        if (content[outer_end] == '[') depth++;
        else if (content[outer_end] == ']') depth--;
        outer_end++;
    }

    while (pos < outer_end) {
        size_t arr_start = content.find('[', pos);
        if (arr_start == string::npos || arr_start >= outer_end) break;
        size_t arr_end = content.find(']', arr_start);
        if (arr_end == string::npos || arr_end >= outer_end) break;

        string arr = content.substr(arr_start + 1, arr_end - arr_start - 1);
        vector<int> perm;
        stringstream ss(arr);
        string token;
        while (getline(ss, token, ',')) {
            size_t f = token.find_first_not_of(" \t\n");
            size_t l = token.find_last_not_of(" \t\n");
            if (f != string::npos && l != string::npos) {
                perm.push_back(stoi(token.substr(f, l - f + 1)));
            }
        }
        if (!perm.empty()) perms.push_back(perm);
        pos = arr_end + 1;
    }

    return perms;
}

// ============================================================================
// Apply edge permutation to a spanning tree (edge set)
// ============================================================================
vector<int> apply_permutation(const set<int>& tree, const vector<int>& perm) {
    vector<int> result;
    result.reserve(tree.size());
    for (int e : tree) {
        result.push_back(perm[e]);
    }
    sort(result.begin(), result.end());
    return result;
}

// ============================================================================
// Compute canonical form: lexicographically smallest under all automorphisms
// ============================================================================
vector<int> canonical_form(const set<int>& tree, const vector<vector<int>>& perms) {
    vector<int> canonical(tree.begin(), tree.end());
    for (const auto& perm : perms) {
        vector<int> mapped = apply_permutation(tree, perm);
        if (mapped < canonical) {
            canonical = mapped;
        }
    }
    return canonical;
}

// ============================================================================
// Main
// ============================================================================
int main(int argc, char** argv) {
    if (argc < 2) {
        cerr << "Usage: " << argv[0] << " <polyhedron_data_dir>" << endl;
        cerr << "Example: " << argv[0] << " data/polyhedra/johnson/n54" << endl;
        return 1;
    }

    string data_dir = argv[1];
    if (data_dir.back() != '/') data_dir += '/';

    const string grh_file = data_dir + "polyhedron.grh";
    const string edge_sets_file = data_dir + "unfoldings_edge_sets.jsonl";
    const string auto_file = data_dir + "automorphisms.json";

    // --- Phase 4: Build spanning tree ZDD ---
    cerr << "Phase 4: Building spanning tree ZDD..." << endl;
    tdzdd::Graph G;
    {
        ifstream file(grh_file);
        if (!file.is_open()) {
            cerr << "Error: Cannot open " << grh_file << endl;
            return 1;
        }
        string line;
        while (getline(file, line)) {
            if (line.empty()) continue;
            stringstream ss(line);
            int u, v;
            if (ss >> u >> v) {
                G.addEdge(to_string(u), to_string(v));
            }
        }
    }
    G.update();

    SpanningTree ST(G);
    tdzdd::DdStructure<2> dd(ST, true);
    string spanning_count = dd.zddCardinality();
    cerr << "Phase 4: spanning trees = " << spanning_count << endl;

    // --- Phase 5: Apply MOPE filters ---
    cerr << "Phase 5: Applying MOPE filters..." << endl;
    vector<set<int>> mopes = load_mopes(edge_sets_file);
    cerr << "  MOPEs loaded: " << mopes.size() << endl;

    int num_edges = G.edgeSize();
    for (int i = 0; i < (int)mopes.size(); ++i) {
        UnfoldingFilter<uint64_t> filter(num_edges, mopes[i]);
        dd.zddSubset(filter);
        dd.zddReduce();
    }
    string nonoverlap_count = dd.zddCardinality();
    cerr << "Phase 5: non-overlapping = " << nonoverlap_count << endl;

    // --- Enumerate all non-overlapping spanning trees from ZDD ---
    // ZDD iterator returns level numbers (1-indexed), not edge indices.
    // Level i corresponds to edge index (num_edges - i).
    cerr << "Enumerating all non-overlapping spanning trees..." << endl;
    vector<set<int>> trees;
    for (auto it = dd.begin(); it != dd.end(); ++it) {
        const set<int>& levels = *it;
        set<int> edge_set;
        for (int level : levels) {
            edge_set.insert(num_edges - level);
        }
        trees.push_back(edge_set);
    }
    cerr << "Enumerated: " << trees.size() << endl;

    // --- Phase 6 verification: canonical form ---
    cerr << "Phase 6 verification: computing canonical forms..." << endl;
    int group_order = 0;
    vector<vector<int>> perms = load_automorphisms(auto_file, group_order);
    cerr << "  Group order: " << group_order << endl;
    cerr << "  Permutations loaded: " << perms.size() << endl;

    set<vector<int>> canonical_set;
    int count = 0;
    for (const auto& tree : trees) {
        canonical_set.insert(canonical_form(tree, perms));
        count++;
        if (count % 10000 == 0) {
            cerr << "  Processed: " << count << "/" << trees.size() << endl;
        }
    }

    cerr << endl;
    cerr << "=== Verification Results ===" << endl;
    cerr << "  Spanning trees:        " << spanning_count << endl;
    cerr << "  Non-overlapping:       " << nonoverlap_count << endl;
    cerr << "  Enumerated:            " << trees.size() << endl;
    cerr << "  Nonisomorphic:         " << canonical_set.size() << endl;

    // Output nonisomorphic count to stdout for scripting
    cout << canonical_set.size() << endl;

    bool pass = (to_string(trees.size()) == nonoverlap_count);
    if (!pass) {
        cerr << "  FAIL: enumerated count != non-overlapping count" << endl;
    }

    return pass ? 0 : 1;
}
