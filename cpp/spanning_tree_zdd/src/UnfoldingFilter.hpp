// ============================================================================
// UnfoldingFilter.hpp
// ============================================================================
//
// What this file does:
//   Defines UnfoldingFilter<BitMask> template class for MOPE-based filtering.
//   Generic version that works with any BitMask type (uint64_t, BigUInt<N>).
//
// このファイルの役割:
//   MOPE ベースのフィルタリングのための UnfoldingFilter<BitMask> テンプレートクラスを定義。
//   任意の BitMask 型（uint64_t, BigUInt<N>）で動作する汎用版。
//
// Responsibility:
//   - Implement TdZdd DdSpec interface for ZDD subsetting
//   - Filter out spanning trees that contain all edges of a MOPE
//   - Support arbitrary bit widths through BitMask template parameter
//
// 責任範囲:
//   - ZDD subsetting のための TdZdd DdSpec インターフェースを実装
//   - MOPE の全辺を含む全域木を除外
//   - BitMask テンプレートパラメータを通じて任意のビット幅をサポート
//
// CRITICAL:
//   The core algorithm (getRoot, getChild) is from Reserch2024 reference.
//   DO NOT modify the logic, only adapt to generic BitMask operations.
//
// 重要:
//   コアアルゴリズム（getRoot, getChild）は Reserch2024 参照実装由来。
//   ロジックを変更せず、汎用的な BitMask 演算に適応させるのみ。
//
// ============================================================================

#pragma once
#include <set>
#include <type_traits>
#include <tdzdd/DdSpec.hpp>
#include "BigUInt.hpp"

// ============================================================================
// UnfoldingFilter Template Class
// UnfoldingFilter テンプレートクラス
// ============================================================================
//
// Template Parameters:
//   BitMask: Type used for bitmask operations (uint64_t or BigUInt<N>)
//
// テンプレートパラメータ:
//   BitMask: ビットマスク演算に使用する型（uint64_t または BigUInt<N>）
//
// Requirements for BitMask:
//   - Default constructor (zero initialization)
//   - operator|= (bitwise OR assignment)
//   - operator&= (bitwise AND assignment)
//   - operator~ (bitwise NOT)
//   - operator== (equality)
//   - operator!= (inequality)
//   - operator! (zero check)
//   - operator& (binary AND)
//   - static bit(int pos) (create bitmask with bit at pos set)
//
// BitMask の要件:
//   - デフォルトコンストラクタ（ゼロ初期化）
//   - operator|=（ビット論理和代入）
//   - operator&=（ビット論理積代入）
//   - operator~（ビット否定）
//   - operator==（等価）
//   - operator!=（非等価）
//   - operator!（ゼロチェック）
//   - operator&（二項 AND）
//   - static bit(int pos)（pos のビットを設定したビットマスクを作成）
//
// ============================================================================
template<typename BitMask>
class UnfoldingFilter : public tdzdd::DdSpec<UnfoldingFilter<BitMask>, BitMask, 2> {
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
    UnfoldingFilter(int e, const std::set<int>& edges)
        : e(e), edges(edges) {}

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
    // Algorithm (from Reserch2024):
    //   mate = 0
    //   for each edge in MOPE:
    //       mate |= (1 << edge)
    //   return e
    //
    // アルゴリズム（Reserch2024 由来）:
    //   mate = 0
    //   MOPE の各辺について:
    //       mate |= (1 << edge)
    //   e を返す
    //
    // ========================================================================
    int getRoot(BitMask& mate) const {
        mate = BitMask();  // Zero initialization / ゼロ初期化
        
        // Set bit for each edge in MOPE
        // MOPE の各辺に対してビットを設定
        for (int edge_id : edges) {
            mate |= BigUIntHelper::BitMaskTraits<BitMask>::bit(edge_id);
        }
        
        return e;  // Return root level / ルートレベルを返す
    }

public:

    // ========================================================================
    // getChild
    // ========================================================================
    //
    // What this does:
    //   Process edge selection at current level and update bitmask state.
    //   Prune if MOPE would be formed (all MOPE edges are in spanning tree).
    //
    // この処理の内容:
    //   現在レベルでの辺選択を処理し、ビットマスク状態を更新。
    //   MOPE が形成される（全 MOPE 辺が全域木に含まれる）場合は枝刈り。
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
    // Algorithm (from Reserch2024 - DO NOT CHANGE):
    //   if value == 0:  // Edge NOT selected
    //       if mate != 0:
    //           mask = 1 << (e - level)
    //           mate &= ~mask
    //           if mate == 0: return 0  // Prune
    //   else:  // Edge IS selected
    //       if (mate & (1 << (e - level))) != 0:
    //           mate = 0
    //   if level == 1: return -1
    //   return level - 1
    //
    // アルゴリズム（Reserch2024 由来 - 変更不可）:
    //   value == 0 の場合:  // 辺が選ばれない
    //       mate != 0 なら:
    //           mask = 1 << (e - level)
    //           mate &= ~mask
    //           mate == 0 なら: 0 を返す  // 枝刈り
    //   それ以外:  // 辺が選ばれる
    //       (mate & (1 << (e - level))) != 0 なら:
    //           mate = 0
    //   level == 1 なら: -1 を返す
    //   level - 1 を返す
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
    // ========================================================================
    int getChild(BitMask& mate, int level, int value) const {
        if (value == 0) {  // 0-branch: edge NOT selected / 0-枝: 辺を選ばない
            // Check if mate is non-zero
            // mate が非ゼロかチェック
            if (mate != BitMask()) {
                // Create mask for current level's bit
                // 現在レベルのビット用マスクを作成
                BitMask mask = BigUIntHelper::BitMaskTraits<BitMask>::bit(e - level);
                
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
            // Check if this edge is in MOPE
            // この辺が MOPE に含まれるかチェック
            BitMask test_bit = BigUIntHelper::BitMaskTraits<BitMask>::bit(e - level);
            BitMask result = mate & test_bit;
            
            // If this edge is in MOPE, clear all bits
            // この辺が MOPE に含まれるなら、全ビットをクリア
            // (MOPE is cut by this edge, so no overlap is possible)
            // （MOPE がこの辺で切断されるため、重なりは不可能）
            if (result != BitMask()) {
                mate = BitMask();
            }
        }
        
        // Check if we've reached the bottom level
        // 最下層に到達したかチェック
        if (level == 1) return -1;  // Terminal / 終端
        
        // Move to next level
        // 次のレベルへ移動
        return --level;
    }
};
