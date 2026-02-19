// ============================================================================
// InvariantCounter.hpp
// ============================================================================
//
// ZddSubsetter と同じアーキテクチャで g-不変全域木のカーディナリティを計算。
// 元 ZDD を read-only で参照し、subset ZDD を構築してからカウント。
//
// ZddSubsetter との違い:
//   - 元 ZDD の deep copy 不要（derefLevel を呼ばない）
//   - zddReduce 不要（カーディナリティは unreduced ZDD でも正確）
//   - DdSweeper 不要（dead node cleanup は不要、カウントするだけ）
//
// メモリの利点:
//   - ピークメモリ = 元 ZDD + subset ZDD + work tables
//   - deep copy の 2 倍、zddReduce の 2 倍を回避
//
// ============================================================================

#pragma once

#include <vector>
#include <string>
#include <cstring>
#include <cstdio>
#include <cmath>
#include <tdzdd/DdStructure.hpp>
#include <tdzdd/dd/DdBuilder.hpp>
#include <tdzdd/util/MemoryPool.hpp>
#include <tdzdd/util/MyHashTable.hpp>
#include <tdzdd/util/MyList.hpp>
#include <tdzdd/util/BigNumber.hpp>
#include "BigUInt.hpp"

// ============================================================================
// count_invariant_trees
// ============================================================================
//
// ZddSubsetter と同じ work[level][col] + MyListOnPool + MyHashTable 構造で
// subset ZDD を構築し、そのカーディナリティを返す。
//
// ============================================================================
template<typename BitMask>
std::string count_invariant_trees(
    const tdzdd::DdStructure<2>& dd,
    int num_edges,
    const std::vector<int>& edge_perm
) {
    using namespace tdzdd;

    // ------------------------------------------------------------------
    // SymmetryFilter と同等の軌道情報構築
    // ------------------------------------------------------------------
    std::vector<int> edge_to_orbit(num_edges, -1);
    std::vector<bool> is_representative(num_edges, false);
    {
        std::vector<bool> visited(num_edges, false);
        int num_orbits = 0;
        for (int i = 0; i < num_edges; ++i) {
            if (visited[i]) continue;
            int j = i;
            std::vector<int> orbit;
            while (!visited[j]) {
                visited[j] = true;
                orbit.push_back(j);
                j = edge_perm[j];
            }
            if (orbit.size() > 1) {
                int orbit_id = num_orbits++;
                int min_edge = *std::min_element(orbit.begin(), orbit.end());
                for (int idx : orbit) {
                    edge_to_orbit[idx] = orbit_id;
                    is_representative[idx] = (idx == min_edge);
                }
            }
        }
    }

    // ------------------------------------------------------------------
    // 入力 ZDD からルート情報を取得
    // ------------------------------------------------------------------
    const auto& input = dd.getDiagram();
    NodeId root_id;
    int root_level;
    {
        NodeId tmpRoot;
        root_level = const_cast<DdStructure<2>&>(dd).getRoot(tmpRoot);
        root_id = tmpRoot;
    }

    if (root_level <= 0) {
        return (root_id == 1) ? "1" : "0";
    }

    // ------------------------------------------------------------------
    // SpecNode レイアウト (DdBuilderBase と同じ)
    //   [0]: srcPtr / nodeId (union)
    //   [1..]: BitMask state
    // ------------------------------------------------------------------
    static constexpr int headerSize = 1;

    union SpecNode {
        NodeId* srcPtr;
        int64_t code;
    };

    auto srcPtr = [](SpecNode* p) -> NodeId*& {
        return p[0].srcPtr;
    };
    auto nodeId_ref = [](SpecNode* p) -> NodeId& {
        return *reinterpret_cast<NodeId*>(&p[0].code);
    };
    auto state = [](SpecNode* p) -> BitMask* {
        return reinterpret_cast<BitMask*>(p + headerSize);
    };
    auto state_const = [](SpecNode const* p) -> const BitMask* {
        return reinterpret_cast<const BitMask*>(p + headerSize);
    };

    int specNodeSize = headerSize +
        (sizeof(BitMask) + sizeof(SpecNode) - 1) / sizeof(SpecNode);

    // ------------------------------------------------------------------
    // ハッシュ関数 / 等価判定（BitMask 用）
    // ------------------------------------------------------------------
    struct Hasher {
        size_t operator()(SpecNode const* p) const {
            const uint64_t* data = reinterpret_cast<const uint64_t*>(
                p + headerSize);
            constexpr size_t n = (sizeof(BitMask) + 7) / 8;
            size_t h = 0;
            for (size_t i = 0; i < n; ++i) {
                h ^= data[i] * 11400714819323198485ULL;
                h = (h << 13) | (h >> 51);
            }
            return h;
        }

        bool operator()(SpecNode const* a, SpecNode const* b) const {
            return std::memcmp(a + headerSize, b + headerSize,
                               sizeof(BitMask)) == 0;
        }
    };

    using UniqTable = MyHashTable<SpecNode*, Hasher, Hasher>;

    // ------------------------------------------------------------------
    // getChild 相当のロジック（inline）
    // ------------------------------------------------------------------
    auto applyFilter = [&](BitMask& st, int level, int value) -> int {
        int edge_index = num_edges - level;
        int orbit = edge_to_orbit[edge_index];

        if (orbit >= 0) {
            BitMask orbit_bit = BigUIntHelper::BitMaskTraits<BitMask>::bit(orbit);

            if (is_representative[edge_index]) {
                if (value == 1) {
                    st |= orbit_bit;
                }
            } else {
                bool orbit_included = (st & orbit_bit) != BitMask();
                if (orbit_included && value == 0) return 0;
                if (!orbit_included && value == 1) return 0;
            }
        }

        if (level == 1) return -1;
        return level - 1;
    };

    // downTable: 入力 ZDD の 0-枝を辿って zerosupLevel まで下る
    auto downTable = [&](NodeId& f, int b, int zerosupLevel) -> int {
        if (zerosupLevel < 0) zerosupLevel = 0;
        f = (*input)[f.row()][f.col()].branch[b];
        while (f.row() > zerosupLevel) {
            f = (*input)[f.row()][f.col()].branch[0];
        }
        return (f == 1) ? -1 : f.row();
    };

    // downSpec: フィルタ状態を zerosupLevel まで下る
    auto downSpec = [&](BitMask& st, int level, int b, int zerosupLevel) -> int {
        if (zerosupLevel < 0) zerosupLevel = 0;
        int i = applyFilter(st, level, b);
        while (i > zerosupLevel) {
            i = applyFilter(st, i, 0);
        }
        return i;
    };

    // ------------------------------------------------------------------
    // 初期化: getRoot 相当
    // ------------------------------------------------------------------
    BitMask rootState{};
    int specLevel = num_edges;  // SymmetryFilter.getRoot returns e

    // ルートの同期: specLevel と root_level を合わせる
    int k = root_level;
    int n = specLevel;

    while (n != 0 && k != 0 && n != k) {
        if (n < k) {
            k = downTable(root_id, 0, n);
        } else {
            n = downSpec(rootState, n, 0, k);
        }
    }

    if (n <= 0 || k <= 0) {
        return (n != 0 && k != 0) ? "1" : "0";
    }

    int topLevel = n;

    // ------------------------------------------------------------------
    // ZddSubsetter と同じ構造の work テーブル
    // ------------------------------------------------------------------
    NodeTableHandler<2> outputHandler;
    NodeTableEntity<2>& output = outputHandler.init(topLevel + 1);

    DataTable<MyListOnPool<SpecNode>> work(topLevel + 1);
    MemoryPools pools;
    pools.resize(topLevel + 1);

    NodeId outputRoot;

    // ルートノードの登録
    {
        size_t m = (*input)[topLevel].size();
        work[topLevel].resize(m);

        SpecNode* p0 = work[topLevel][root_id.col()].alloc_front(
            pools[topLevel], specNodeSize);
        *state(p0) = rootState;
        srcPtr(p0) = &outputRoot;  // ルートの srcPtr は outputRoot を指す
    }

    // ------------------------------------------------------------------
    // Phase 1: トップダウン subset 構築（ZddSubsetter::subset と同じ構造）
    // ------------------------------------------------------------------
    for (int i = topLevel; i >= 1; --i) {
        size_t const m = (*input)[i].size();
        size_t mm = 0;

        if (work[i].empty()) work[i].resize(m);

        // Pass 1: 状態の統合と出力ノード ID の割り当て
        for (size_t j = 0; j < m; ++j) {
            MyListOnPool<SpecNode>& list = work[i][j];
            size_t listSize = list.size();

            if (listSize >= 2) {
                Hasher hasher;
                UniqTable uniq(listSize * 2, hasher, hasher);

                for (auto t = list.begin(); t != list.end(); ++t) {
                    SpecNode* p = *t;
                    SpecNode*& p0 = uniq.add(p);

                    if (p0 == p) {
                        // 新規状態: 出力ノード ID を割り当て
                        NodeId* sp = srcPtr(p);  // save before overwrite
                        NodeId nid(i, mm++);
                        nodeId_ref(p) = nid;
                        if (sp) *sp = nid;
                    } else {
                        // 重複状態: SymmetryFilter は merge_states をデフォルト
                        // (0 = merge成功) で実装しているため、常に統合
                        NodeId* sp = srcPtr(p);  // save before overwrite
                        NodeId target = nodeId_ref(p0);
                        if (sp) *sp = target;
                        nodeId_ref(p) = 1;  // unused marker
                    }
                }
            } else if (listSize == 1) {
                SpecNode* p = list.front();
                NodeId* sp = srcPtr(p);  // save before overwrite
                NodeId nid(i, mm++);
                nodeId_ref(p) = nid;
                if (sp) *sp = nid;
            }
        }

        // 出力テーブルの行を初期化
        output.initRow(i, mm);
        Node<2>* const outi = output[i].data();
        size_t jj = 0;

        // Pass 2: 各ノードの子を計算
        for (size_t j = 0; j < m; ++j) {
            MyListOnPool<SpecNode>& list = work[i][j];

            for (auto t = list.begin(); t != list.end(); ++t) {
                SpecNode* p = *t;

                if (nodeId_ref(p) == 1) {
                    // unused (重複状態で統合済み) — スキップ
                    continue;
                }

                Node<2>& q = outi[jj];

                for (int b = 0; b < 2; ++b) {
                    // フィルタ状態のコピー
                    BitMask tmpState = *state(p);

                    // 入力 ZDD の子ノードを辿る
                    NodeId f(i, j);
                    int kk = downTable(f, b, i - 1);
                    int ii = downSpec(tmpState, i, b, kk);

                    while (ii != 0 && kk != 0 && ii != kk) {
                        if (ii < kk) {
                            kk = downTable(f, 0, ii);
                        } else {
                            ii = downSpec(tmpState, ii, 0, kk);
                        }
                    }

                    if (ii <= 0 || kk <= 0) {
                        // 終端
                        q.branch[b] = (ii != 0 && kk != 0) ? NodeId(0, 1) : NodeId(0, 0);
                    } else {
                        // 非終端の子: work テーブルに登録
                        if (work[ii].empty()) work[ii].resize((*input)[ii].size());
                        SpecNode* pp = work[ii][f.col()].alloc_front(
                            pools[ii], specNodeSize);
                        *state(pp) = tmpState;
                        srcPtr(pp) = &q.branch[b];
                    }
                }

                ++jj;
            }
        }

        // このレベルの work と pool を解放
        work[i].clear();
        pools[i].clear();
    }

    // work と pools を完全に解放
    work.init(0);
    pools.clear();

    // ------------------------------------------------------------------
    // Phase 2: 出力 ZDD のカーディナリティ計算（ボトムアップ）
    // ------------------------------------------------------------------
    // TdZdd の BigNumber + MemoryPools で計算（Cardinality.hpp と同じ方式）
    int outTop = outputRoot.row();
    if (outTop <= 0) {
        return (outputRoot == 1) ? "1" : "0";
    }

    MemoryPools countPools;
    countPools.resize(outTop + 1);

    int maxWords = (int)std::ceil((double)outTop * std::log2(2.0) / 63.0) + 1;
    BigNumber tmp1;
    tmp1.setArray(countPools[outTop].allocate<uint64_t>(maxWords));

    DataTable<BigNumber> countWork(outTop + 1);

    // 終端の初期化
    {
        countWork[0].resize(2);
        countWork[0][0].setArray(countPools[0].allocate<uint64_t>(1));
        countWork[0][0].store(uint64_t(0));
        countWork[0][1].setArray(countPools[0].allocate<uint64_t>(1));
        countWork[0][1].store(uint64_t(1));
    }

    // ボトムアップ走査
    for (int i = 1; i <= outTop; ++i) {
        size_t const m = output[i].size();
        countWork[i].resize(m);

        for (size_t j = 0; j < m; ++j) {
            // n = values[0] + values[1] (ZDD cardinality)
            size_t w;
            NodeId f0 = output[i][j].branch[0];
            NodeId f1 = output[i][j].branch[1];

            w = tmp1.store(countWork[f0.row()][f0.col()]);
            w = tmp1.add(countWork[f1.row()][f1.col()]);

            countWork[i][j].setArray(countPools[i].allocate<uint64_t>(w));
            countWork[i][j].store(tmp1);
        }
    }

    std::string result = countWork[outputRoot.row()][outputRoot.col()];

    return result;
}
