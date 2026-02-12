// ============================================================================
// FrontierData.hpp
// ============================================================================
//
// What this file does:
//   Defines FrontierData structure for storing computation state in frontier.
//   Used by SpanningTree ZDD specification to track component connectivity.
//
// このファイルの役割:
//   フロンティアにおける計算状態を保存する FrontierData 構造体を定義。
//   SpanningTree ZDD 仕様が成分の連結性を追跡するために使用。
//
// Responsibility in the project:
//   - Provides state storage for each vertex in frontier
//   - Tracks component ID for connectivity checking
//   - Minimal structure for efficient ZDD construction
//
// プロジェクト内での責務:
//   - フロンティア内の各頂点の状態を保存
//   - 連結性チェックのための成分 ID を追跡
//   - 効率的な ZDD 構築のための最小限の構造
//
// ============================================================================

#pragma once

// ============================================================================
// FrontierData structure
// ============================================================================
//
// Stores computation state for vertices in the frontier.
// フロンティア内の頂点の計算状態を保存。
//
// Members:
//   comp: Component ID for connectivity tracking
//         0 = uninitialized
//         positive value = component ID (typically vertex ID)
//         -1 = vertex has left frontier
//
// メンバー:
//   comp: 連結性追跡のための成分 ID
//         0 = 未初期化
//         正の値 = 成分 ID（通常は頂点 ID）
//         -1 = 頂点がフロンティアを出た
//
class FrontierData{
public:
    short comp; // Frontier 中の頂点における component を表す変数 / Component ID for vertex in frontier
};
