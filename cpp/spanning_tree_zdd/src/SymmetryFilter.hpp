// ============================================================================
// SymmetryFilter.hpp
// ============================================================================
//
// What this file does:
//   Defines SymmetryFilter<BitMask> template class for g-invariance filtering.
//   Given an edge permutation g, filters spanning trees T such that gT = T.
//   Used in Phase 6 for Burnside's lemma computation.
//
// このファイルの役割:
//   g-不変フィルタリングのための SymmetryFilter<BitMask> テンプレートクラスを定義。
//   辺置換 g が与えられたとき、gT = T を満たす全域木 T をフィルタリング。
//   Phase 6 の Burnside の補題計算で使用。
//
// Responsibility in the project:
//   - Implements TdZdd DdSpec interface for ZDD subsetting
//   - Enforces orbit consistency: edges in the same orbit under g must
//     all be selected or all not selected
//   - Uses bitmask for compact state representation (same as UnfoldingFilter)
//
// プロジェクト内での責務:
//   - ZDD subsetting のための TdZdd DdSpec インターフェースを実装
//   - 軌道の一貫性を強制: g による同一軌道の辺は全て選択 or 全て非選択
//   - コンパクトな状態表現のためビットマスクを使用（UnfoldingFilter と同様）
//
// Phase 6 における位置づけ:
//   Core filter for computing |T_g| in Burnside's lemma.
//   For each automorphism g ∈ Aut(Γ), this filter counts
//   spanning trees invariant under g.
//   Burnside の補題における |T_g| 計算のコアフィルタ。
//   各自己同型 g ∈ Aut(Γ) に対して、g の下で不変な全域木を数える。
//
// Design:
//   State = single BitMask (one bit per non-trivial orbit).
//   For each orbit, the "representative" is the edge with the smallest index.
//   Since ZDD processes edges from index 0 upward, the representative is
//   always processed first.
//
//   - Representative edge: record the selection value (0 or 1) in the bit
//   - Subsequent edges in orbit: enforce the same value; prune if inconsistent
//
//   The bitmask is initialized to 0. For representative edges:
//     value=0 → bit stays 0 → subsequent edges must also be 0
//     value=1 → bit set to 1 → subsequent edges must also be 1
//
// 設計:
//   状態 = 単一の BitMask（非自明軌道ごとに 1 ビット）。
//   各軌道の「代表辺」は最小インデックスの辺。
//   ZDD はインデックス 0 から順に辺を処理するため、代表辺が必ず先に処理される。
//
//   - 代表辺: 選択値（0 or 1）をビットに記録
//   - 軌道の後続辺: 同じ値を強制; 不整合なら枝刈り
//
//   ビットマスクは 0 で初期化。代表辺について:
//     value=0 → ビットは 0 のまま → 後続辺も 0 でなければならない
//     value=1 → ビットを 1 に設定 → 後続辺も 1 でなければならない
//
// ============================================================================

#pragma once
#include <vector>
#include <tdzdd/DdSpec.hpp>
#include "BigUInt.hpp"

// ============================================================================
// SymmetryFilter Template Class
// SymmetryFilter テンプレートクラス
// ============================================================================
//
// Template Parameters:
//   BitMask: Type used for bitmask operations (uint64_t or BigUInt<N>)
//
// テンプレートパラメータ:
//   BitMask: ビットマスク演算に使用する型（uint64_t または BigUInt<N>）
//
// ============================================================================
template<typename BitMask>
class SymmetryFilter
    : public tdzdd::DdSpec<SymmetryFilter<BitMask>, BitMask, 2> {
private:
    int const e;                          // Total number of edges / 全辺数
    std::vector<int> edge_to_orbit;       // edge index → orbit index (-1 if trivial)
    std::vector<bool> is_representative;  // is this edge the representative of its orbit?

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
    //   2. For non-trivial orbits (size > 1), assign orbit index and mark representative
    //   3. Representative = smallest edge index in each orbit
    //
    // 処理:
    //   1. 置換から辺軌道を計算
    //   2. 非自明軌道（サイズ > 1）に軌道インデックスを割り当て、代表辺をマーク
    //   3. 代表辺 = 各軌道の最小辺インデックス
    //
    // ========================================================================
    SymmetryFilter(int num_edges, const std::vector<int>& edge_perm)
        : e(num_edges),
          edge_to_orbit(num_edges, -1),
          is_representative(num_edges, false) {

        // Compute orbits from edge permutation
        // 辺置換から軌道を計算
        std::vector<bool> visited(e, false);
        int num_orbits = 0;

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
                int min_edge = *std::min_element(orbit.begin(), orbit.end());
                for (int edge_idx : orbit) {
                    edge_to_orbit[edge_idx] = orbit_id;
                    is_representative[edge_idx] = (edge_idx == min_edge);
                }
            }
        }
    }

    // ========================================================================
    // getRoot
    // ========================================================================
    //
    // Initialize bitmask to 0 (all orbits undecided / default to EXCLUDE).
    // ビットマスクを 0 に初期化（全軌道は未定 / デフォルトで EXCLUDE）。
    //
    // ========================================================================
    int getRoot(BitMask& state) const {
        state = BitMask();  // Zero initialization / ゼロ初期化
        return e;
    }

    // ========================================================================
    // getChild
    // ========================================================================
    //
    // Process edge selection at current level.
    //
    // If the edge belongs to a non-trivial orbit:
    //   - Representative edge: record the decision in the bitmask
    //     value=0: bit stays 0
    //     value=1: set bit to 1
    //   - Non-representative edge: enforce consistency with the recorded decision
    //     bit=0 and value=1: prune (orbit should be EXCLUDED)
    //     bit=1 and value=0: prune (orbit should be INCLUDED)
    //
    // 現在レベルでの辺選択を処理。
    //
    // 辺が非自明軌道に属する場合:
    //   - 代表辺: 判定をビットマスクに記録
    //     value=0: ビットは 0 のまま
    //     value=1: ビットを 1 に設定
    //   - 非代表辺: 記録された判定との一貫性を強制
    //     bit=0 かつ value=1: 枝刈り（軌道は EXCLUDE であるべき）
    //     bit=1 かつ value=0: 枝刈り（軌道は INCLUDE であるべき）
    //
    // ========================================================================
    int getChild(BitMask& state, int level, int value) const {
        int edge_index = e - level;
        int orbit = edge_to_orbit[edge_index];

        if (orbit >= 0) {
            BitMask orbit_bit = BigUIntHelper::BitMaskTraits<BitMask>::bit(orbit);

            if (is_representative[edge_index]) {
                // Representative edge: record decision
                // 代表辺: 判定を記録
                if (value == 1) {
                    state |= orbit_bit;  // Set bit / ビットを設定
                }
                // value=0: bit stays 0 (correct by initialization)
                // value=0: ビットは 0 のまま（初期化で正しい）
            } else {
                // Non-representative edge: enforce consistency
                // 非代表辺: 一貫性を強制
                bool orbit_included = (state & orbit_bit) != BitMask();

                if (orbit_included && value == 0) return 0;  // Expected INCLUDE, got EXCLUDE
                if (!orbit_included && value == 1) return 0;  // Expected EXCLUDE, got INCLUDE
            }
        }

        if (level == 1) return -1;  // Terminal / 終端
        return level - 1;
    }
};
