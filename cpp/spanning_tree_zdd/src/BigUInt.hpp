// ============================================================================
// BigUInt.hpp
// ============================================================================
//
// What this file does:
//   Defines BigUInt<N> template class for arbitrary-width bitmasks.
//   Uses array of uint64_t blocks to represent N*64 bits.
//
// このファイルの役割:
//   任意ビット幅のビットマスクのための BigUInt<N> テンプレートクラスを定義。
//   uint64_t ブロックの配列を使って N*64 ビットを表現。
//
// Responsibility:
//   - Provide bitwise operations for ZDD filtering
//   - Support arbitrary bit widths in 64-bit increments
//   - Maintain performance through inlining and compile-time optimization
//
// 責任範囲:
//   - ZDD フィルタリングのためのビット演算を提供
//   - 64 ビット刻みで任意のビット幅をサポート
//   - インライン化とコンパイル時最適化でパフォーマンスを維持
//
// Design:
//   - Template parameter N specifies number of 64-bit blocks
//   - All operations are inlined for performance
//   - Compatible with TdZdd's DdSpec requirements
//
// 設計:
//   - テンプレートパラメータ N は 64 ビットブロックの数を指定
//   - 全ての演算はパフォーマンスのためにインライン化
//   - TdZdd の DdSpec 要件と互換
//
// ============================================================================

#pragma once
#include <cstdint>
#include <cstring>

// ============================================================================
// BigUInt Template Class
// BigUInt テンプレートクラス
// ============================================================================
//
// Template Parameters:
//   N: Number of 64-bit blocks (bit width = N * 64)
//
// テンプレートパラメータ:
//   N: 64 ビットブロックの数（ビット幅 = N * 64）
//
// Supported Operations:
//   - Bitwise OR (|=)
//   - Bitwise AND (&=)
//   - Bitwise NOT (~)
//   - Equality (==, !=)
//   - Zero check (!)
//   - Bit setting (static bit(int pos))
//
// サポートする演算:
//   - ビット論理和 (|=)
//   - ビット論理積 (&=)
//   - ビット否定 (~)
//   - 等価比較 (==, !=)
//   - ゼロチェック (!)
//   - ビット設定 (static bit(int pos))
//
// ============================================================================
template<size_t N>
class BigUInt {
private:
    uint64_t blocks[N];  // Array of 64-bit blocks / 64 ビットブロックの配列

public:
    // ========================================================================
    // Constructor
    // コンストラクタ
    // ========================================================================
    //
    // What this does:
    //   Initialize all blocks to zero.
    //
    // この処理の内容:
    //   全ブロックをゼロに初期化。
    //
    // ========================================================================
    inline BigUInt() {
        std::memset(blocks, 0, sizeof(blocks));
    }

    // ========================================================================
    // Bitwise OR Assignment (|=)
    // ビット論理和代入 (|=)
    // ========================================================================
    //
    // What this does:
    //   Perform bitwise OR with another BigUInt, updating this object.
    //
    // この処理の内容:
    //   別の BigUInt とビット論理和を実行し、このオブジェクトを更新。
    //
    // Parameters:
    //   rhs: Right-hand side operand
    //
    // パラメータ:
    //   rhs: 右辺オペランド
    //
    // Returns:
    //   Reference to this object
    //
    // 戻り値:
    //   このオブジェクトへの参照
    //
    // ========================================================================
    inline BigUInt& operator|=(const BigUInt& rhs) {
        for (size_t i = 0; i < N; ++i) {
            blocks[i] |= rhs.blocks[i];
        }
        return *this;
    }

    // ========================================================================
    // Bitwise AND Assignment (&=)
    // ビット論理積代入 (&=)
    // ========================================================================
    //
    // What this does:
    //   Perform bitwise AND with another BigUInt, updating this object.
    //
    // この処理の内容:
    //   別の BigUInt とビット論理積を実行し、このオブジェクトを更新。
    //
    // ========================================================================
    inline BigUInt& operator&=(const BigUInt& rhs) {
        for (size_t i = 0; i < N; ++i) {
            blocks[i] &= rhs.blocks[i];
        }
        return *this;
    }

    // ========================================================================
    // Bitwise NOT (~)
    // ビット否定 (~)
    // ========================================================================
    //
    // What this does:
    //   Return a new BigUInt with all bits inverted.
    //
    // この処理の内容:
    //   全ビットを反転した新しい BigUInt を返す。
    //
    // Returns:
    //   New BigUInt with inverted bits
    //
    // 戻り値:
    //   ビット反転した新しい BigUInt
    //
    // ========================================================================
    inline BigUInt operator~() const {
        BigUInt result;
        for (size_t i = 0; i < N; ++i) {
            result.blocks[i] = ~blocks[i];
        }
        return result;
    }

    // ========================================================================
    // Equality Operator (==)
    // 等価演算子 (==)
    // ========================================================================
    //
    // What this does:
    //   Compare two BigUInt values for equality.
    //
    // この処理の内容:
    //   2 つの BigUInt 値が等しいか比較。
    //
    // Returns:
    //   true if all blocks are equal, false otherwise
    //
    // 戻り値:
    //   全ブロックが等しければ true、そうでなければ false
    //
    // ========================================================================
    inline bool operator==(const BigUInt& rhs) const {
        for (size_t i = 0; i < N; ++i) {
            if (blocks[i] != rhs.blocks[i]) return false;
        }
        return true;
    }

    // ========================================================================
    // Inequality Operator (!=)
    // 非等価演算子 (!=)
    // ========================================================================
    inline bool operator!=(const BigUInt& rhs) const {
        return !(*this == rhs);
    }

    // ========================================================================
    // Logical NOT (Zero Check) (!)
    // 論理否定（ゼロチェック）(!)
    // ========================================================================
    //
    // What this does:
    //   Check if all bits are zero.
    //   Used in UnfoldingFilter to detect when MOPE is formed.
    //
    // この処理の内容:
    //   全ビットがゼロかチェック。
    //   UnfoldingFilter で MOPE が形成されたかを検出するために使用。
    //
    // Returns:
    //   true if all blocks are zero, false otherwise
    //
    // 戻り値:
    //   全ブロックがゼロなら true、そうでなければ false
    //
    // CRITICAL:
    //   This is used in getChild() to prune branches.
    //   Must return true only when ALL bits are zero.
    //
    // 重要:
    //   これは getChild() で枝刈りに使用される。
    //   全ビットがゼロの時のみ true を返さなければならない。
    //
    // ========================================================================
    inline bool operator!() const {
        for (size_t i = 0; i < N; ++i) {
            if (blocks[i] != 0) return false;
        }
        return true;
    }

    // ========================================================================
    // Bitwise AND (Binary Operator)
    // ビット論理積（二項演算子）
    // ========================================================================
    //
    // What this does:
    //   Perform bitwise AND and return a new BigUInt.
    //   Used in getChild() to test if a specific bit is set.
    //
    // この処理の内容:
    //   ビット論理積を実行し、新しい BigUInt を返す。
    //   getChild() で特定のビットが設定されているかテストするために使用。
    //
    // ========================================================================
    inline BigUInt operator&(const BigUInt& rhs) const {
        BigUInt result;
        for (size_t i = 0; i < N; ++i) {
            result.blocks[i] = blocks[i] & rhs.blocks[i];
        }
        return result;
    }

    // ========================================================================
    // Static Bit Setting Method
    // 静的ビット設定メソッド
    // ========================================================================
    //
    // What this does:
    //   Create a BigUInt with only the specified bit set to 1.
    //   Used for bit manipulation in getRoot() and getChild().
    //
    // この処理の内容:
    //   指定されたビットのみを 1 に設定した BigUInt を作成。
    //   getRoot() と getChild() でビット操作に使用。
    //
    // Parameters:
    //   pos: Bit position (0-indexed)
    //
    // パラメータ:
    //   pos: ビット位置（0 から始まる）
    //
    // Returns:
    //   BigUInt with only bit at position 'pos' set to 1
    //
    // 戻り値:
    //   位置 'pos' のビットのみが 1 の BigUInt
    //
    // Example:
    //   bit(0)  → 0x0000...0001
    //   bit(64) → 0x0001...0000 (in second block)
    //
    // 例:
    //   bit(0)  → 0x0000...0001
    //   bit(64) → 0x0001...0000（2番目のブロック）
    //
    // ========================================================================
    static inline BigUInt bit(int pos) {
        BigUInt result;
        int block_idx = pos / 64;
        int bit_idx = pos % 64;
        if (block_idx < static_cast<int>(N)) {
            result.blocks[block_idx] = 1ULL << bit_idx;
        }
        return result;
    }
};

// ============================================================================
// Specialization for uint64_t (N=1 case)
// uint64_t のための特殊化（N=1 の場合）
// ============================================================================
//
// Note:
//   uint64_t is a native type and doesn't have a static bit() method.
//   We provide a namespace-level function for compatibility.
//
// 注記:
//   uint64_t はネイティブ型で static bit() メソッドを持たない。
//   互換性のため名前空間レベルの関数を提供。
//
// ============================================================================

namespace BigUIntHelper {
    // ========================================================================
    // BitMaskTraits: Unified interface for bit operations
    // BitMaskTraits: ビット演算の統一インターフェース
    // ========================================================================
    //
    // Provides a uniform way to create bit masks for both uint64_t and BigUInt<N>.
    // uint64_t と BigUInt<N> の両方に対してビットマスクを作成する統一的な方法を提供。
    //
    // ========================================================================
    
    // Generic template: use BitMask::bit()
    // 汎用テンプレート: BitMask::bit() を使用
    template<typename BitMask>
    struct BitMaskTraits {
        static inline BitMask bit(int pos) {
            return BitMask::bit(pos);
        }
    };
    
    // Specialization for uint64_t
    // uint64_t の特殊化
    template<>
    struct BitMaskTraits<uint64_t> {
        static inline uint64_t bit(int pos) {
            return 1ULL << pos;
        }
    };
}
