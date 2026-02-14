# Counting Nonoverlapping Unfoldings

[![MIT](https://img.shields.io/badge/license-MIT-9e1836.svg?logo=&style=plastic)](LICENSE)
<img src="https://img.shields.io/badge/purpose-research-8A2BE2.svg?logo=&style=plastic">
<img src="https://img.shields.io/github/v/release/ShiotaTakumi/CountingNonoverlappingUnfoldings?include_prereleases&style=plastic">
<img src="https://img.shields.io/github/last-commit/ShiotaTakumi/CountingNonoverlappingUnfoldings?style=plastic">
<img src="https://img.shields.io/badge/MacOS-26.2-000000.svg?logo=macOS&style=plastic">
<img src="https://img.shields.io/badge/Shell-bash-FFD500.svg?logo=shell&style=plastic">
<img src="https://img.shields.io/badge/C++-GCC%2015.2.0-00599C.svg?logo=cplusplus&style=plastic">
<img src="https://img.shields.io/badge/Python-3.12.0-3776AB.svg?logo=python&style=plastic">

## AI Tool Disclosure / AI ツール使用に関する開示

The codebase reorganization, refactoring, and documentation of this project were conducted using the [Cursor](https://www.cursor.com/) editor with the **Claude Opus 4.6 Thinking** model. The AI was used as an assistive tool; all design decisions and research responsibility remain with the author.

本プロジェクトのコード整理・リファクタリング・ドキュメント整備において、[Cursor](https://www.cursor.com/) エディタおよび **Claude Opus 4.6 Thinking** モデルを補助ツールとして使用しました。設計判断および研究上の責任はすべて著者に帰属します。

## Overview / 概要

This program counts the number of non-overlapping edge unfoldings of a given convex regular-faced polyhedron, using ZDD (Zero-suppressed Binary Decision Diagram) and MOPE-based filtering.

与えられた凸正面多面体の非重複辺展開図の個数を、ZDD（ゼロ抑制型二分決定図）と MOPE ベースのフィルタリングにより数え上げるプログラムです。

## Algorithm Details / アルゴリズムの詳細

Please refer to the following paper for details:

詳細は以下の論文を参照してください：

- [SEG+25] Takumi Shiota, Yudai Enomoto, Masashi Gorobe, Takashi Horiyama, Tonan Kamata, Toshiki Saitoh and Ryuhei Uehara: "The Number of Non-overlapping Unfoldings in Convex Polyhedra", The 37th Canadian Conference on Computational Geometry (CCCG 2025), to appear, August 11-15, 2025, Toronto (Canada).
- [HS13] Takashi Horiyama and Wataru Shoji. The number of different unfoldings of polyhedra. In 24th International Symposium on Algorithms and Computation, volume 8283 of LNCS, pages 623-633. Springer, 2013.

## Pipeline / パイプライン

The processing pipeline consists of six phases:

処理パイプラインは 6 つのフェーズで構成されています：

| Phase | Module | Description / 説明 |
|-------|--------|-------------------|
| Phase 1 | `edge_relabeling` | Pathwidth-optimized edge relabeling / パス幅最適化辺ラベル貼り替え |
| Phase 2 | `unfolding_expansion` | Isomorphic variant enumeration / 同型変種の列挙 |
| Phase 3 | `graph_export` | TdZdd input data generation / TdZdd 入力データ生成 |
| Phase 4 | `counting` | ZDD-based spanning tree enumeration / ZDD ベース全域木列挙 |
| Phase 5 | `counting` | MOPE-based non-overlapping filtering / MOPE ベース非重複フィルタリング |
| Phase 6 | `counting` | Nonisomorphic counting via Burnside's lemma / Burnside の補題による非同型数え上げ |

Phase 4, 5, and 6 share a single C++ binary and are controlled by the `counting` Python module with orthogonal flags (`--no-overlap` for Phase 5, `--noniso` for Phase 6). `preprocess` executes Phase 1-3 in sequence with a single command to prepare input data.

Phase 4, 5, 6 は単一の C++ バイナリを共有し、`counting` Python モジュールの直交フラグ（`--no-overlap` で Phase 5、`--noniso` で Phase 6）で制御されます。`preprocess` は Phase 1-3 を 1 コマンドで順に実行し、入力データを準備します。

## Prerequisites / 前提条件

- Python 3.12.0
- GCC 14.2.0
- [RotationalUnfolding](https://github.com/ShiotaTakumi/RotationalUnfolding) pipeline completed (Phase 1-3) for target polyhedra / 対象多面体について RotationalUnfolding パイプライン（Phase 1-3）が完了していること

## Quick Start / クイックスタート

```bash
# Build the C++ binaries / C++ バイナリのビルド
cd cpp/edge_relabeling && mkdir -p build && cd build && cmake .. && make && cd ../../..
cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make && cd ../../..

# Run preprocessing (Phase 1-3) / 前処理の一括実行
PYTHONPATH=python python -m preprocess --poly data/polyhedra/johnson/n20
```

### Running Individual Phases / 個別フェーズの実行

```bash
# Phase 1: Edge relabeling / 辺ラベル貼り替え
PYTHONPATH=python python -m edge_relabeling \
  --poly /path/to/RotationalUnfolding/data/polyhedra/johnson/n20/polyhedron.json

# Phase 2: Unfolding expansion / 展開図展開
PYTHONPATH=python python -m unfolding_expansion \
  --exact /path/to/RotationalUnfolding/output/polyhedra/johnson/n20/exact.jsonl

# Phase 3: Graph data conversion / グラフデータ変換
PYTHONPATH=python python -m graph_export \
  --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json

# Phase 4: Spanning tree enumeration / 全域木列挙
PYTHONPATH=python python -m counting \
  --poly data/polyhedra/johnson/n20

# Phase 4→5: + Non-overlapping filtering / + 非重複フィルタリング
PYTHONPATH=python python -m counting \
  --poly data/polyhedra/johnson/n20 --no-overlap

# Phase 4→6: + Nonisomorphic counting / + 非同型数え上げ
PYTHONPATH=python python -m counting \
  --poly data/polyhedra/johnson/n20 --noniso

# Phase 4→5→6: + Both / + 両方
PYTHONPATH=python python -m counting \
  --poly data/polyhedra/johnson/n20 --no-overlap --noniso

# Drawing: Partial unfolding SVG visualization / 部分展開図 SVG 可視化
PYTHONPATH=python python -m drawing \
  --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
```

### Arguments / 引数

| Argument | Used by | Description / 説明 |
|----------|---------|-------------------|
| `--poly` | `preprocess`, `edge_relabeling`, `graph_export`, `counting` | Path to polyhedron data / 多面体データへのパス |
| `--exact` | `unfolding_expansion` | Path to RotationalUnfolding's exact.jsonl / exact.jsonl へのパス |
| `--no-overlap` | `counting` | Enable Phase 5 overlap filtering / Phase 5 重なりフィルタを有効化 |
| `--noniso` | `counting` | Enable Phase 6 nonisomorphic counting / Phase 6 非同型数え上げを有効化 |
| `--jsonl` | `drawing` | Path to JSONL file for visualization / 可視化用 JSONL ファイルへのパス |
| `--no-labels` | `drawing` | Hide labels in SVG / SVG のラベルを非表示 |

> **Note / 注記**: The `drawing` module currently supports **partial unfolding visualization only** (MOPE-based overlapping partial unfoldings). Full unfolding visualization (complete spanning tree unfoldings) is planned for a future release, with `--partial` / `--full` flags to select the drawing mode.
>
> `drawing` モジュールは現在、**部分展開図の可視化のみ**（MOPE ベースの重なり部分展開図）をサポートしています。完全展開図の可視化（全域木展開図）は将来のリリースで `--partial` / `--full` フラグによるモード選択とともに実装予定です。

## Directory Structure / ディレクトリ構成

```
CountingNonoverlappingUnfoldings/
├── cpp/                          # C++ binaries / C++ バイナリ
│   ├── edge_relabeling/          # Phase 1 binary (decompose wrapper)
│   │   └── src/main.cpp
│   └── spanning_tree_zdd/        # Phase 4/5/6 binary (ZDD + filtering + Burnside)
│       └── src/
│           ├── main.cpp
│           ├── SpanningTree.hpp/cpp
│           ├── UnfoldingFilter.hpp
│           ├── SymmetryFilter.hpp
│           ├── BigUInt.hpp
│           └── FrontierData.hpp
├── data/                         # Intermediate data / 中間データ
│   └── polyhedra/
│       └── <class>/<name>/
│           ├── polyhedron_relabeled.json  # Phase 1 output
│           ├── edge_mapping.json          # Phase 1 output
│           ├── exact_relabeled.jsonl      # Phase 2 output
│           ├── unfoldings_overlapping_all.jsonl  # Phase 2 output
│           ├── polyhedron.grh             # Phase 3 output
│           └── unfoldings_edge_sets.jsonl # Phase 3 output
├── docs/                         # Design documents / 設計書
│   ├── PHASE1_EDGE_RELABELING.md
│   ├── PHASE2_UNFOLDING_EXPANSION.md
│   ├── PHASE3_GRAPH_DATA_CONVERSION.md
│   ├── PHASE4_SPANNING_TREE_ENUMERATION.md
│   ├── PHASE5_FILTERING.md
│   ├── PHASE6_NONISOMORPHIC_COUNTING.md
│   └── PREPROCESS.md
├── lib/                          # External libraries (DO NOT MODIFY) / 外部ライブラリ（変更不可）
│   ├── decompose/                # Pathwidth decomposition
│   ├── frontier_basic_tdzdd/     # Frontier manager
│   └── tdzdd/                    # TdZdd library
├── output/                       # Final results / 最終結果
│   └── polyhedra/
│       └── <class>/<name>/
│           └── spanning_tree/
│               └── result.json   # Phase 4/5/6 output
├── python/                       # Python CLI modules / Python CLI モジュール
│   ├── edge_relabeling/          # Phase 1
│   ├── unfolding_expansion/      # Phase 2
│   ├── graph_export/             # Phase 3
│   ├── counting/                 # Phase 4/5/6 pipeline CLI
│   ├── drawing/                  # Visualization utility / 可視化ユーティリティ
│   └── preprocess/               # Preprocessing orchestrator (Phase 1-3) / 前処理オーケストレーター
└── LICENSE
```

## Acknowledgements / 謝辞

This work was supported in part by JSPS KAKENHI Grant Numbers JP24KJ1816, JP22H03549, JP20K11673, JP24KJ1816 and JP25K24391, and by MEXT KAKENHI Grant JP20H05964.

本研究は JSPS 科研費 JP24KJ1816, JP22H03549, JP20K11673, JP24KJ1816, JP25K24391 および MEXT 科研費 JP20H05964 の助成を受けたものです。
