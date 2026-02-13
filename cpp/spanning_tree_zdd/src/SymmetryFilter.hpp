// ============================================================================
// SymmetryFilter.hpp
// ============================================================================
//
// What this file does:
//   Defines SymmetryFilter class for g-invariance filtering on ZDD.
//   Given an edge permutation g, filters spanning trees T such that gT = T.
//   Used in Phase 6 for Burnside's lemma computation.
//
// このファイルの役割:
//   ZDD 上の g-不変フィルタリングのための SymmetryFilter クラスを定義。
//   辺置換 g が与えられたとき、gT = T を満たす全域木 T をフィルタリング。
//   Phase 6 の Burnside の補題計算で使用。
//
// Responsibility in the project:
//   - Implements TdZdd DdSpec interface for ZDD subsetting
//   - Enforces orbit consistency: edges in the same orbit under g must
//     all be selected or all not selected
//   - Single-pass processing (one ZDD traversal per automorphism)
//
// プロジェクト内での責務:
//   - ZDD subsetting のための TdZdd DdSpec インターフェースを実装
//   - 軌道の一貫性を強制: g による同一軌道の辺は全て選択 or 全て非選択
//   - シングルパス処理（自己同型1つにつき ZDD 走査1回）
//
// Phase 6 における位置づけ:
//   Core filter for computing |T_g| in Burnside's lemma.
//   For each automorphism g ∈ Aut(Γ), this filter counts
//   spanning trees invariant under g.
//   Burnside の補題における |T_g| 計算のコアフィルタ。
//   各自己同型 g ∈ Aut(Γ) に対して、g の下で不変な全域木を数える。
//
// ============================================================================

#pragma once
#include <vector>
#include <tdzdd/DdSpec.hpp>

// ============================================================================
// SymmetryFilter class
// ============================================================================
//
// ZDD specification for filtering g-invariant spanning trees.
// Uses PodArrayDdSpec with per-orbit decision tracking.
//
// g-不変全域木のフィルタリングのための ZDD 仕様。
// 軌道ごとの判定追跡を伴う PodArrayDdSpec を使用。
//
// State (per orbit):
//   0 = UNDECIDED (no edge in this orbit processed yet)
//   1 = EXCLUDE (first edge was not selected → all must be excluded)
//   2 = INCLUDE (first edge was selected → all must be included)
//
// 状態（軌道ごと）:
//   0 = 未定（この軌道の辺がまだ処理されていない）
//   1 = 除外（最初の辺が非選択 → 全て除外されるべき）
//   2 = 包含（最初の辺が選択 → 全て包含されるべき）
//
// ============================================================================
class SymmetryFilter
    : public tdzdd::PodArrayDdSpec<SymmetryFilter, char, 2> {
private:
    int const e;                    // Total number of edges / 全辺数
    int num_orbits;                 // Number of non-trivial orbits / 非自明軌道の数
    std::vector<int> edge_to_orbit; // edge index → orbit index (-1 if trivial)
                                    // 辺インデックス → 軌道インデックス（自明なら -1）

public:
    // ========================================================================
    // Constructor
    // コンストラクタ
    // ========================================================================
    //
    // Parameters:
    //   num_edges: Total number of edges in the graph
    //   edge_perm: Edge permutation [σ(0), σ(1), ..., σ(E-1)]
    //
    // パラメータ:
    //   num_edges: グラフの全辺数
    //   edge_perm: 辺置換 [σ(0), σ(1), ..., σ(E-1)]
    //
    // Processing:
    //   1. Compute edge orbits from the permutation
    //   2. Assign orbit indices to non-trivial orbits (size > 1)
    //   3. Set array size for state tracking
    //
    // 処理:
    //   1. 置換から辺軌道を計算
    //   2. 非自明軌道（サイズ > 1）に軌道インデックスを割り当て
    //   3. 状態追跡のための配列サイズを設定
    //
    // ========================================================================
    SymmetryFilter(int num_edges, const std::vector<int>& edge_perm)
        : e(num_edges), num_orbits(0), edge_to_orbit(num_edges, -1) {

        // Compute orbits from edge permutation
        // 辺置換から軌道を計算
        std::vector<bool> visited(e, false);

        for (int i = 0; i < e; ++i) {
            if (visited[i]) continue;

            // Trace the orbit of edge i
            // 辺 i の軌道をたどる
            std::vector<int> orbit;
            int j = i;
            while (!visited[j]) {
                visited[j] = true;
                orbit.push_back(j);
                j = edge_perm[j];
            }

            // Only assign orbit index for non-trivial orbits (size > 1)
            // 非自明軌道（サイズ > 1）にのみ軌道インデックスを割り当て
            if (orbit.size() > 1) {
                int orbit_id = num_orbits++;
                for (int edge_idx : orbit) {
                    edge_to_orbit[edge_idx] = orbit_id;
                }
            }
        }

        // Set state array size to number of non-trivial orbits
        // 状態配列サイズを非自明軌道の数に設定
        // Minimum 1 to avoid zero-size array issues
        // ゼロサイズ配列の問題を避けるため最小 1
        setArraySize(std::max(1, num_orbits));
    }

    // ========================================================================
    // getRoot
    // ========================================================================
    //
    // Initialize state: all orbits UNDECIDED.
    // 状態を初期化: 全軌道を未定。
    //
    // ========================================================================
    int getRoot(char* state) const {
        for (int i = 0; i < num_orbits; ++i) {
            state[i] = 0; // UNDECIDED / 未定
        }
        return e;
    }

    // ========================================================================
    // getChild
    // ========================================================================
    //
    // Process edge selection at current level.
    // If the edge belongs to a non-trivial orbit:
    //   - First edge in orbit: record the decision (INCLUDE or EXCLUDE)
    //   - Subsequent edges: enforce consistency (prune if inconsistent)
    //
    // 現在レベルでの辺選択を処理。
    // 辺が非自明軌道に属する場合:
    //   - 軌道の最初の辺: 判定を記録（包含 or 除外）
    //   - 以降の辺: 一貫性を強制（不整合なら枝刈り）
    //
    // ========================================================================
    int getChild(char* state, int level, int value) const {
        int edge_index = e - level;
        int orbit = edge_to_orbit[edge_index];

        if (orbit >= 0) {
            if (state[orbit] == 0) {
                // First edge in this orbit: record decision
                // この軌道の最初の辺: 判定を記録
                state[orbit] = (value == 0) ? 1 : 2;
            } else {
                // Subsequent edge: enforce consistency
                // 以降の辺: 一貫性を強制
                if (state[orbit] == 1 && value == 1) return 0; // Expected EXCLUDE, got INCLUDE
                if (state[orbit] == 2 && value == 0) return 0; // Expected INCLUDE, got EXCLUDE
            }
        }

        if (level == 1) return -1; // Terminal / 終端
        return level - 1;
    }
};
