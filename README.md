# Counting Nonoverlapping Unfoldings

[![MIT](https://img.shields.io/badge/license-MIT-9e1836.svg?logo=&style=plastic)](LICENSE)
<img src="https://img.shields.io/badge/purpose-research-8A2BE2.svg?logo=&style=plastic">
<img src="https://img.shields.io/github/v/release/ShiotaTakumi/CountingNonoverlappingUnfoldings?include_prereleases&style=plastic">
<img src="https://img.shields.io/github/last-commit/ShiotaTakumi/CountingNonoverlappingUnfoldings?style=plastic">
<img src="https://img.shields.io/badge/MacOS-15.5-000000.svg?logo=macOS&style=plastic">
<img src="https://img.shields.io/badge/Shell-bash-FFD500.svg?logo=shell&style=plastic">
<img src="https://img.shields.io/badge/C++-GCC%2014.2.0-00599C.svg?logo=cplusplus&style=plastic">
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

Takumi Shiota, Yudai Enomoto, Masashi Gorobe, Takashi Horiyama, Tonan Kamata, Toshiki Saitoh and Ryuhei Uehara: "The Number of Non-overlapping Unfoldings in Convex Polyhedra", The 37th Canadian Conference on Computational Geometry (CCCG 2025), to appear, August 11-15, 2025, Toronto (Canada).

## Pipeline / パイプライン

The processing pipeline consists of five phases:

処理パイプラインは 5 つのフェーズで構成されています：

| Phase | Module | Description / 説明 |
|-------|--------|-------------------|
| Phase 1 | `edge_relabeling` | Pathwidth-optimized edge relabeling / パス幅最適化辺ラベル貼り替え |
| Phase 2 | `unfolding_expansion` | Isomorphic variant enumeration / 同型変種の列挙 |
| Phase 3 | `graph_export` | TdZdd input data generation / TdZdd 入力データ生成 |
| Phase 4 | `spanning_tree_zdd` | ZDD-based spanning tree enumeration / ZDD ベース全域木列挙 |
| Phase 5 | `spanning_tree_zdd` | MOPE-based non-overlapping filtering / MOPE ベース非重複フィルタリング |

Phase 4 and Phase 5 are executed together in a single C++ binary. `run_all` executes Phase 1 through Phase 5 in sequence with a single command.

Phase 4 と Phase 5 は単一の C++ バイナリで一緒に実行されます。`run_all` は Phase 1 から Phase 5 までを 1 コマンドで順に実行します。

## Prerequisites / 前提条件

- Python 3.12.0
- GCC 14.2.0
- [RotationalUnfolding](https://github.com/ShiotaTakumi/RotationalUnfolding) pipeline completed (Phase 1-3) for target polyhedra / 対象多面体について RotationalUnfolding パイプライン（Phase 1-3）が完了していること

## Quick Start / クイックスタート

```bash
# Build the C++ binaries / C++ バイナリのビルド
cd cpp/edge_relabeling && mkdir -p build && cd build && cmake .. && make && cd ../../..
cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make && cd ../../..

# Run the full pipeline / パイプラインの一括実行
PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n20
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

# Phase 4 & 5: ZDD construction + filtering / ZDD 構築 + フィルタリング
PYTHONPATH=python python -m spanning_tree_zdd \
  --grh data/polyhedra/johnson/n20/polyhedron.grh \
  --edge-sets data/polyhedra/johnson/n20/unfoldings_edge_sets.jsonl

# Drawing: SVG visualization / SVG 可視化
PYTHONPATH=python python -m drawing \
  --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
```

### Arguments / 引数

| Argument | Used by | Description / 説明 |
|----------|---------|-------------------|
| `--poly` | `run_all`, `edge_relabeling`, `graph_export` | Path to polyhedron data / 多面体データへのパス |
| `--exact` | `unfolding_expansion` | Path to RotationalUnfolding's exact.jsonl / exact.jsonl へのパス |
| `--grh` | `spanning_tree_zdd` | Path to polyhedron.grh / polyhedron.grh へのパス |
| `--edge-sets` | `spanning_tree_zdd` | Path to MOPE edge sets / MOPE 辺集合へのパス |
| `--jsonl` | `drawing` | Path to JSONL file for visualization / 可視化用 JSONL ファイルへのパス |
| `--no-labels` | `drawing` | Hide labels in SVG / SVG のラベルを非表示 |

## Directory Structure / ディレクトリ構成

```
CountingNonoverlappingUnfoldings/
├── cpp/                          # C++ binaries / C++ バイナリ
│   ├── edge_relabeling/          # Phase 1 binary (decompose wrapper)
│   │   └── src/main.cpp
│   └── spanning_tree_zdd/        # Phase 4 & 5 binary (ZDD + filtering)
│       └── src/
│           ├── main.cpp
│           ├── SpanningTree.hpp/cpp
│           ├── UnfoldingFilter.hpp
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
│   └── RUN_ALL.md
├── lib/                          # External libraries (DO NOT MODIFY) / 外部ライブラリ（変更不可）
│   ├── decompose/                # Pathwidth decomposition
│   ├── frontier_basic_tdzdd/     # Frontier manager
│   └── tdzdd/                    # TdZdd library
├── output/                       # Final results / 最終結果
│   └── polyhedra/
│       └── <class>/<name>/
│           └── spanning_tree/
│               └── result.json   # Phase 4 & 5 output
├── python/                       # Python CLI modules / Python CLI モジュール
│   ├── edge_relabeling/          # Phase 1
│   ├── unfolding_expansion/      # Phase 2
│   ├── graph_export/             # Phase 3
│   ├── spanning_tree_zdd/        # Phase 4 & 5 wrapper
│   ├── drawing/                  # Visualization utility / 可視化ユーティリティ
│   └── run_all/                  # Pipeline orchestrator / 一括実行
└── LICENSE
```

## Acknowledgements / 謝辞

This work was supported in part by JSPS KAKENHI Grant Numbers JP24KJ1816, JP22H03549, JP20K11673, JP24KJ1816 and JP25K24391, and by MEXT KAKENHI Grant JP20H05964.

本研究は JSPS 科研費 JP24KJ1816, JP22H03549, JP20K11673, JP24KJ1816, JP25K24391 および MEXT 科研費 JP20H05964 の助成を受けたものです。
