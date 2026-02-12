// ============================================================================
// SpanningTree.hpp
// ============================================================================
//
// What this file does:
//   Defines SpanningTree class: ZDD specification for spanning tree enumeration.
//   Implements TdZdd's PodArrayDdSpec interface with frontier-based search.
//
// このファイルの役割:
//   SpanningTree クラスの定義: 全域木列挙のための ZDD 仕様。
//   フロンティアベース探索で TdZdd の PodArrayDdSpec インターフェースを実装。
//
// Responsibility in the project:
//   - Implements ZDD recursive specification for spanning trees
//   - Uses frontier-based search algorithm to track component connectivity
//   - Integrates with FrontierManager for efficient frontier management
//   - Prunes invalid solutions (cycles, disconnected components)
//   - Based on Reserch2024/SpanningTree implementation
//
// プロジェクト内での責務:
//   - 全域木のための ZDD 再帰的仕様を実装
//   - フロンティアベース探索アルゴリズムで連結成分を追跡
//   - 効率的なフロンティア管理のために FrontierManager と統合
//   - 無効な解（サイクル、非連結成分）を枝刈り
//   - Reserch2024/SpanningTree の実装をベース
//
// Phase 4 における位置づけ:
//   Core algorithm for ZDD-based spanning tree enumeration.
//   Phase 4 の ZDD ベース全域木列挙のコアアルゴリズム。
//
// ============================================================================

#pragma once

#include <vector>
#include <tdzdd/DdSpec.hpp>
#include <tdzdd/util/Graph.hpp>
#include <FrontierManager.hpp>
#include "FrontierData.hpp"

// ============================================================================
// SpanningTree class
// ============================================================================
//
// ZDD specification for spanning tree enumeration using frontier-based search.
// Inherits from TdZdd's PodArrayDdSpec with FrontierData state.
//
// フロンティアベース探索を用いた全域木列挙のための ZDD 仕様。
// FrontierData 状態で TdZdd の PodArrayDdSpec を継承。
//
// ============================================================================
class SpanningTree: public tdzdd::PodArrayDdSpec<SpanningTree, FrontierData, 2>{
private:
    const tdzdd::Graph& G;      // 入力グラフ / Input graph
    const short v;              // 頂点の数 / Number of vertices
    const int e;                // 辺の数 / Number of edges
    const FrontierManager fm;   // Frontier を管理するオブジェクト / Frontier manager
    
    // Frontier における計算状態を初期化
    // Initialize computation state in frontier
    void initializeComp(FrontierData* data) const;
    
    // 頂点 v における component の値を更新
    // Update component value for vertex v
    void setComp(FrontierData* data, short v, short c) const;
    
    // 頂点 v における component の値を取得
    // Get component value for vertex v
    short getComp(FrontierData* data, short v) const;

public:
    // コンストラクタ
    // Constructor
    SpanningTree(const tdzdd::Graph& G);
    
    // 根節点における計算状態を格納
    // Store computation state at root node
    int getRoot(FrontierData* data) const;
    
    // 子節点の計算状態を計算
    // Compute computation state for child node
    // level: 現在のレベル / Current level
    // value: 選択された枝の種類（0 or 1）/ Selected branch type (0 or 1)
    // return: 次のレベル（-1 なら受理、0 なら枝刈り）/ Next level (-1 = accept, 0 = prune)
    int getChild(FrontierData* data, int level, int value) const;
};
