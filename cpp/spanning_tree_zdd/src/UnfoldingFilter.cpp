// ============================================================================
// UnfoldingFilter.cpp
// ============================================================================
//
// What this file does:
//   Implements UnfoldingFilter class methods.
//   Core logic for MOPE-based ZDD subsetting to exclude overlapping unfoldings.
//
// このファイルの役割:
//   UnfoldingFilter クラスのメソッドを実装。
//   MOPE ベースの ZDD 部分集合抽出のコアロジック（重なり除外）。
//
// ============================================================================

#include "UnfoldingFilter.hpp"

// ============================================================================
// Constructor Implementation
// コンストラクタの実装
// ============================================================================
UnfoldingFilter::UnfoldingFilter(int e, const std::set<int>& edges)
    : e(e), edges(edges) {}

// ============================================================================
// getRoot Implementation
// getRoot の実装
// ============================================================================
//
// What this does:
//   Initialize bitmask with MOPE edges set to 1.
//   Each edge ID in the MOPE corresponds to a bit position.
//
// この処理の内容:
//   MOPE の辺に対応するビットを 1 に初期化。
//   MOPE の各辺 ID がビット位置に対応。
//
// Example:
//   If MOPE contains edges {1, 4, 7} and e=10:
//   mate will have bits 1, 4, 7 set to 1.
//
// 例:
//   MOPE が辺 {1, 4, 7} を含み e=10 の場合:
//   mate はビット 1, 4, 7 が 1 になる。
//
// ============================================================================
int UnfoldingFilter::getRoot(uint64_t& mate) const {
    mate = 0;  // Initialize all bits to 0 / 全ビットを 0 に初期化

    // Set bit to 1 for each edge in MOPE
    // MOPE の各辺に対してビットを 1 にセット
    for (int edge_id : edges) {
        mate |= (1ULL << edge_id);
    }

    return e;  // Return root level / ルートレベルを返す
}

// ============================================================================
// getChild Implementation
// getChild の実装
// ============================================================================
//
// What this does:
//   Process edge selection at current level and update bitmask state.
//   Prune if MOPE would be formed (all edges selected).
//
// この処理の内容:
//   現在レベルでの辺選択を処理し、ビットマスク状態を更新。
//   MOPE が形成される（全辺が選ばれる）場合は枝刈り。
//
// Algorithm (DO NOT CHANGE):
//   If value == 0 (edge NOT selected):
//     - Clear the bit for this edge
//     - If all bits become 0: prune (all MOPE edges are NOT selected,
//       meaning the spanning tree contains all MOPE edges)
//   If value == 1 (edge IS selected):
//     - If this edge is in MOPE: clear all bits
//       (MOPE is cut by this edge, no overlap possible)
//
// アルゴリズム（変更不可）:
//   value == 0（辺が選ばれない）の場合:
//     - この辺のビットをクリア
//     - 全ビットが 0 になったら: 枝刈り（全 MOPE 辺が選ばれていない、
//       つまり全域木が全 MOPE 辺を含む）
//   value == 1（辺が選ばれる）の場合:
//     - この辺が MOPE に含まれるなら: 全ビットをクリア
//       （MOPE がこの辺で切断、重なり不可能）
//
// CRITICAL NOTE:
//   This logic is from Reserch2024/EnumerateNonoverlappingEdgeUnfolding.
//   The algorithm has been verified to work correctly.
//   DO NOT modify this logic.
//
// 重要:
//   このロジックは Reserch2024/EnumerateNonoverlappingEdgeUnfolding 由来。
//   アルゴリズムは正しく動作することが検証済み。
//   このロジックを変更しないこと。
//
// ============================================================================
int UnfoldingFilter::getChild(uint64_t& mate, int level, int value) const {
    if (value == 0) {  // 0-branch: edge NOT selected / 0-枝: 辺を選ばない
        if (mate) {    // Only process if mate is non-zero / mate が非ゼロの時のみ処理
            // Create mask for current level's bit
            // 現在レベルのビット用マスクを作成
            uint64_t mask = 1ULL << (e - level);

            // Clear the bit for this edge
            // この辺のビットをクリア
            mate &= ~mask;

            // If all bits are now 0, prune this branch
            // 全ビットが 0 になったら、この枝を枝刈り
            // (This means all MOPE edges are in the spanning tree = overlap)
            // （これは全 MOPE 辺が全域木に含まれる = 重なり）
            if (!mate) return 0;
        }
    } else {  // 1-branch: edge IS selected / 1-枝: 辺を選ぶ
        // If this edge is in MOPE, clear all bits
        // この辺が MOPE に含まれるなら、全ビットをクリア
        // (MOPE is cut by this edge, so no overlap is possible)
        // （MOPE がこの辺で切断されるため、重なりは不可能）
        if (mate & (1ULL << (e - level))) {
            mate = 0;
        }
    }

    // Check if we've reached the bottom level
    // 最下層に到達したかチェック
    if (level == 1) return -1;  // Terminal / 終端

    // Move to next level
    // 次のレベルへ移動
    return --level;
}
