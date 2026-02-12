// ============================================================================
// UnfoldingFilter.hpp
// ============================================================================
//
// What this file does:
//   Defines UnfoldingFilter class for ZDD subsetting based on MOPE.
//   Filters out spanning trees that contain all edges of a MOPE.
//
// このファイルの役割:
//   MOPE（重なりを持つ展開図）を用いた ZDD の部分集合抽出を定義。
//   MOPE の全ての辺を含む全域木を除外するフィルタ。
//
// Responsibility:
//   - Maintain bitmask state for MOPE edges
//   - Prune ZDD branches that form overlapping unfoldings
//   - Implement TdZdd DdSpec interface for filtering
//
// 責任範囲:
//   - MOPE の辺に対するビットマスク状態を管理
//   - 重なりを形成する ZDD の枝を枝刈り
//   - フィルタリングのための TdZdd DdSpec インターフェースを実装
//
// Phase 5 における位置づけ:
//   Core filtering logic for Phase 5.
//   Used iteratively with zddSubset() to exclude overlapping unfoldings.
//   Phase 5 のコアフィルタリングロジック。
//   zddSubset() と反復的に使用し、重なりを持つ展開図を除外。
//
// ============================================================================

#pragma once
#include <set>
#include <cstdint>
#include <tdzdd/DdSpec.hpp>

// ============================================================================
// UnfoldingFilter Class
// UnfoldingFilter クラス
// ============================================================================
//
// Purpose:
//   Filter ZDD to exclude spanning trees that contain all edges of a MOPE.
//   Use uint64_t bitmask to track MOPE edge inclusion.
//
// 目的:
//   MOPE の全ての辺を含む全域木を除外するように ZDD をフィルタ。
//   uint64_t ビットマスクで MOPE の辺の包含を追跡。
//
// Template Parameters (via DdSpec inheritance):
//   - State type: uint64_t (bitmask for up to 64 edges)
//   - Arity: 2 (binary decision diagram)
//
// テンプレートパラメータ（DdSpec 継承経由）:
//   - 状態型: uint64_t（最大 64 辺用のビットマスク）
//   - アリティ: 2（二分決定図）
//
// Algorithm:
//   For each edge level (top to bottom):
//   - If edge is NOT selected (0-branch): clear corresponding bit
//     - If all bits become 0: prune (MOPE would be formed)
//   - If edge is selected (1-branch): check if it's a MOPE edge
//     - If yes: clear all bits (MOPE is cut, no overlap possible)
//
// アルゴリズム:
//   各辺レベル（上から下）に対して:
//   - 辺が選ばれない（0-枝）: 対応ビットをクリア
//     - 全ビットが 0 になったら: 枝刈り（MOPE が形成される）
//   - 辺が選ばれる（1-枝）: MOPE の辺かチェック
//     - もしそうなら: 全ビットをクリア（MOPE が切断、重なり不可能）
//
// ============================================================================
class UnfoldingFilter : public tdzdd::DdSpec<UnfoldingFilter, uint64_t, 2> {
private:
    int const e;         // Number of edges in the graph / グラフの辺数
    std::set<int> edges; // Set of edge IDs in this MOPE / この MOPE に含まれる辺 ID の集合

public:
    // ========================================================================
    // Constructor
    // コンストラクタ
    // ========================================================================
    //
    // Parameters:
    //   e: Total number of edges in the graph
    //   edges: Set of edge IDs that form this MOPE
    //
    // パラメータ:
    //   e: グラフの全辺数
    //   edges: この MOPE を構成する辺 ID の集合
    //
    // ========================================================================
    UnfoldingFilter(int e, const std::set<int>& edges);

    // ========================================================================
    // getRoot
    // ========================================================================
    //
    // What this does:
    //   Initialize the bitmask state at the root of the ZDD.
    //   Set bits to 1 for all edges in the MOPE.
    //
    // この処理の内容:
    //   ZDD のルートでビットマスク状態を初期化。
    //   MOPE の全ての辺に対してビットを 1 にセット。
    //
    // Parameters:
    //   mate: Output parameter, initialized with MOPE edge bits set to 1
    //
    // パラメータ:
    //   mate: 出力パラメータ、MOPE の辺ビットを 1 に初期化
    //
    // Returns:
    //   Root level (number of edges)
    //
    // 戻り値:
    //   ルートレベル（辺の数）
    //
    // ========================================================================
    int getRoot(uint64_t& mate) const;

    // ========================================================================
    // getChild
    // ========================================================================
    //
    // What this does:
    //   Compute the next state based on edge selection at current level.
    //   Prune branches that would form a MOPE (overlapping unfolding).
    //
    // この処理の内容:
    //   現在レベルでの辺選択に基づいて次の状態を計算。
    //   MOPE を形成する（重なりを持つ展開図）枝を枝刈り。
    //
    // Parameters:
    //   mate: Current bitmask state (modified in-place)
    //   level: Current level in the ZDD (edge index from top)
    //   value: 0 (edge not selected) or 1 (edge selected)
    //
    // パラメータ:
    //   mate: 現在のビットマスク状態（インプレース変更）
    //   level: ZDD の現在レベル（上からの辺インデックス）
    //   value: 0（辺を選ばない）または 1（辺を選ぶ）
    //
    // Returns:
    //   - Next level (level - 1) if not at bottom
    //   - -1 if reached bottom (terminal)
    //   - 0 if pruned (MOPE would be formed)
    //
    // 戻り値:
    //   - 次のレベル（level - 1）最下層でない場合
    //   - -1 最下層到達（終端）
    //   - 0 枝刈り（MOPE が形成される）
    //
    // CRITICAL:
    //   This logic is from Reserch2024 reference implementation.
    //   DO NOT modify the core algorithm.
    //
    // 重要:
    //   このロジックは Reserch2024 参照実装由来。
    //   コアアルゴリズムを変更しないこと。
    //
    // ========================================================================
    int getChild(uint64_t& mate, int level, int value) const;
};
