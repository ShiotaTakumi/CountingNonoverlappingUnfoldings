# preprocess — Preprocessing Pipeline (Phase 1-3)

**Status**: Implemented (Specification Frozen)
**Version**: 2.0.0
**Last Updated**: 2026-02-08

---

## Overview / 概要

`preprocess` is a researcher-oriented utility that executes the preprocessing pipeline (Phase 1-3) with a single command and a single argument. It prepares all input data required for Phase 4-6 (`nonisomorphic` module).

`preprocess` は研究者向けユーティリティであり、前処理パイプライン（Phase 1-3）を 1 つのコマンドと 1 つの引数で実行します。Phase 4-6（`nonisomorphic` モジュール）に必要なすべての入力データを準備します。

**This is an orchestrator, not a processing module.** `preprocess` does not implement any algorithm. It invokes Phase 1, Phase 2, and Phase 3 as independent subprocesses, in a fixed order. Each phase runs its own CLI exactly as if the researcher had typed the command manually.

**これはオーケストレーターであり、処理モジュールではありません。** `preprocess` はアルゴリズムを一切実装しません。Phase 1、Phase 2、Phase 3 を独立したサブプロセスとして固定順序で呼び出します。各フェーズは、研究者が手動でコマンドを入力した場合とまったく同じ CLI を実行します。

---

## Purpose and Motivation / 目的と動機

### Why preprocess Exists / なぜ preprocess が必要か

The preprocessing pipeline consists of three independent stages (Phase 1-3). Running them manually requires multiple separate commands with careful path management. This is:

- **Error-prone**: A typo in one command produces inconsistent outputs across phases.
- **Tedious**: Researchers must wait for each phase to finish before starting the next.
- **Undocumented by default**: Without a single entry point, reproducing preprocessing requires knowledge of all phase commands and their input/output locations.

`preprocess` eliminates these issues. It provides:

- **One command, minimal arguments**: `--poly` is the only required input.
- **Reproducibility by invocation**: A single shell command fully reproduces the preprocessing.
- **Fail-fast behavior**: If any phase fails, execution stops immediately.

前処理パイプラインは 3 つの独立した段階（Phase 1-3）で構成されています。手動実行には、慎重なパス管理を伴う複数の個別コマンドが必要です。これは：

- **ミスを誘発する**: 1 つのコマンドのタイプミスがフェーズ間で不整合な出力を生む
- **煩雑である**: 各フェーズの完了を待ってから次を開始する必要がある
- **再現手順が暗黙知になる**: 単一のエントリポイントなしに前処理を再現するには、すべてのフェーズコマンドとその入出力場所の知識が必要

`preprocess` はこれらの問題を排除します：

- **1 コマンド、最小限の引数**: `--poly` が必須の唯一の入力
- **呼び出しによる再現性**: 単一のシェルコマンドで前処理全体を再現可能
- **即時停止**: いずれかのフェーズが失敗した場合、実行は即座に停止

### What preprocess Automates / preprocess が自動化する範囲

|| Step | Module | Output |
||------|--------|--------|
|| Phase 1 | `edge_relabeling` | `polyhedron_relabeled.json`, `edge_mapping.json` |
|| Phase 2 | `unfolding_expansion` | `exact_relabeled.jsonl`, `unfoldings_overlapping_all.jsonl` |
|| Phase 3 | `graph_export` | `polyhedron.grh`, `unfoldings_edge_sets.jsonl` |

All phases are executed sequentially. After completion, Phase 4-6 can be run via the `nonisomorphic` module.

すべてのフェーズは順次実行されます。完了後、Phase 4-6 は `nonisomorphic` モジュールで実行できます。

---

## Usage / 使用方法

### Command / コマンド

```bash
PYTHONPATH=python python -m preprocess --poly data/polyhedra/<class>/<name>
```

### Examples / 実行例

```bash
# Johnson solid n21
PYTHONPATH=python python -m preprocess --poly data/polyhedra/johnson/n21

# Antiprism a12
PYTHONPATH=python python -m preprocess --poly data/polyhedra/antiprism/a12

# Archimedean solid s07
PYTHONPATH=python python -m preprocess --poly data/polyhedra/archimedean/s07
```

### Arguments / 引数

|| Argument | Required | Description |
||----------|----------|-------------|
|| `--poly data/polyhedra/CLASS/NAME` | Yes | Path to polyhedron data directory (e.g., `data/polyhedra/johnson/n21`). Shell Tab completion is supported. / 多面体データディレクトリへのパス。Tab 補完対応。 |

### After Preprocessing / 前処理後

After `preprocess` completes, Phase 4-6 can be run:

`preprocess` 完了後、Phase 4-6 を実行できます：

```bash
# Phase 4 (spanning tree enumeration) / 全域木列挙
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/<class>/<name>

# Phase 4→5 (+ overlap filtering) / + 重なりフィルタリング
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/<class>/<name> --filter

# Phase 4→6 (+ nonisomorphic counting) / + 非同型数え上げ
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/<class>/<name> --noniso

# Phase 4→5→6 (+ both) / + 両方
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/<class>/<name> --filter --noniso
```

---

## Prerequisites / 前提条件

`preprocess` requires:

1. **RotationalUnfolding pipeline completion**: The following files must exist in RotationalUnfolding repository:
   - `RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json` (Phase 1 input)
   - `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl` (Phase 2 input)

2. **Hardcoded path**: Currently assumes RotationalUnfolding is at `/Users/tshiota/Github/RotationalUnfolding`. This will be made configurable in future versions.

3. **C++ binary (Phase 1)**: `cpp/edge_relabeling/build/` must be built (see Phase 1 documentation).

`preprocess` は以下を必要とします：

1. **RotationalUnfolding パイプラインの完了**: RotationalUnfolding リポジトリに以下のファイルが存在する必要があります：
   - `RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json`（Phase 1 入力）
   - `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl`（Phase 2 入力）

2. **ハードコードされたパス**: 現在 RotationalUnfolding が `/Users/tshiota/Github/RotationalUnfolding` にあることを仮定しています。将来のバージョンで設定可能にする予定です。

3. **C++ バイナリ（Phase 1）**: `cpp/edge_relabeling/build/` がビルドされている必要があります（Phase 1 ドキュメント参照）。

---

## Execution Order / 実行順序

`preprocess` executes exactly three steps, in this fixed order. The order is not configurable.

`preprocess` は正確に 3 つのステップを、この固定順序で実行します。順序は変更できません。

### Step 1: Phase 1 — Edge Relabeling / 辺ラベル貼り替え

```
[preprocess] Phase 1: edge_relabeling
```

Invokes:

```bash
python -m edge_relabeling --poly /path/to/RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json
```

- Reads polyhedron structure from RotationalUnfolding.
- Applies pathwidth optimization to edge labeling.
- Produces `polyhedron_relabeled.json` and `edge_mapping.json` in `data/polyhedra/<class>/<name>/`.
- Overwrites existing files.

### Step 2: Phase 2 — Unfolding Expansion / 展開図展開

```
[preprocess] Phase 2: unfolding_expansion
```

Invokes:

```bash
python -m unfolding_expansion --exact /path/to/RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl
```

- Reads exact unfoldings from RotationalUnfolding (read-only).
- Applies edge relabeling and expands to all isomorphic variants.
- Produces `exact_relabeled.jsonl` and `unfoldings_overlapping_all.jsonl` in `data/polyhedra/<class>/<name>/`.
- Overwrites existing files.

### Step 3: Phase 3 — Graph Data Conversion / グラフデータ変換

```
[preprocess] Phase 3: graph_export
```

Invokes:

```bash
python -m graph_export --poly data/polyhedra/<class>/<name>/polyhedron_relabeled.json
```

- Reads relabeled polyhedron (read-only).
- Generates TdZdd-compatible graph representation.
- Produces `polyhedron.grh` and `unfoldings_edge_sets.jsonl` in `data/polyhedra/<class>/<name>/`.
- Overwrites existing files.

---

## Output Directory Structure / 出力ディレクトリ構造

After a complete `preprocess` execution, the directory structure is as follows:

`preprocess` の完全な実行後、ディレクトリ構造は以下のようになります：

```
data/polyhedra/<class>/<name>/
├── polyhedron_relabeled.json     # Phase 1: relabeled polyhedron structure
├── edge_mapping.json             # Phase 1: old → new edge ID mapping
├── exact_relabeled.jsonl         # Phase 2: relabeled exact unfoldings
├── unfoldings_overlapping_all.jsonl  # Phase 2: expanded isomorphic variants
├── polyhedron.grh                # Phase 3: TdZdd graph format
└── unfoldings_edge_sets.jsonl    # Phase 3: MOPE edge sets
```

### File Relationships / ファイル間の関係

```
RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json
  ↓ Phase 1: edge_relabeling
data/polyhedra/<class>/<name>/polyhedron_relabeled.json
  ↓ Phase 3: graph_export
data/polyhedra/<class>/<name>/polyhedron.grh

RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl
  ↓ Phase 2: unfolding_expansion
data/polyhedra/<class>/<name>/unfoldings_overlapping_all.jsonl
  ↓ Phase 3: graph_export
data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
  ↓ Phase 4-6: nonisomorphic
output/polyhedra/<class>/<name>/spanning_tree/result.json
```

Each downstream output depends on its upstream input. After preprocessing, Phase 4-6 operates on the generated data.

各下流出力は上流入力に依存します。前処理後、Phase 4-6 が生成されたデータに対して動作します。

---

## Guarantees / 保証事項

### Pipeline Integrity / パイプラインの整合性

- **Each phase is invoked as an independent subprocess.** `preprocess` does not import or call any phase's internal functions. Each phase runs its own CLI entry point.
- **No data is generated by `preprocess` itself.** All JSON/JSONL files are produced by their respective phases.
- **Existing outputs are overwritten.** Each phase overwrites its own output file if it already exists. This is the intended behavior.
- **Failure stops the pipeline.** If any phase exits with a non-zero status, `preprocess` terminates immediately. Subsequent phases are not executed.
- **Order is deterministic.** Phase 1 → Phase 2 → Phase 3. Always.

- **各フェーズは独立したサブプロセスとして呼び出される。** `preprocess` はいかなるフェーズの内部関数もインポート・呼び出ししない。各フェーズは自身の CLI エントリポイントを実行する。
- **`preprocess` 自体はデータを生成しない。** すべての JSON/JSONL ファイルはそれぞれのフェーズが生成する。
- **既存の出力は上書きされる。** 各フェーズは自身の出力ファイルが既に存在する場合、上書きする。これは意図された動作である。
- **失敗はパイプラインを停止する。** いずれかのフェーズがゼロ以外のステータスで終了した場合、`preprocess` は即座に終了する。後続フェーズは実行されない。
- **順序は決定論的である。** Phase 1 → Phase 2 → Phase 3。常に。

### Architectural Separation / アーキテクチャ的分離

- **All phases are independent modules.** `preprocess` does not create coupling between them.
- **Each phase's code is untouched.** `preprocess` exists in `python/preprocess/` and does not modify any file in other phase directories.
- **RotationalUnfolding dependency is explicit.** Phase 1 and Phase 2 require RotationalUnfolding outputs. This cross-repository dependency is documented and checked at runtime.

- **すべてのフェーズは独立したモジュールである。** `preprocess` はそれらの間の結合を生み出さない。
- **各フェーズのコードは変更されない。** `preprocess` は `python/preprocess/` に存在し、他のフェーズディレクトリ内のいかなるファイルも変更しない。
- **RotationalUnfolding 依存は明示的である。** Phase 1 と Phase 2 は RotationalUnfolding の出力を必要とする。このリポジトリ間依存は文書化され、実行時にチェックされる。

---

## Non-Guarantees / 非保証事項

- **Partial outputs from failed runs are not cleaned up.** If Phase 3 fails, Phase 1 and Phase 2 outputs remain in the directory. This is by design—earlier phases' outputs are valid and reusable.
- **RotationalUnfolding path is hardcoded.** Currently assumes `/Users/tshiota/Github/RotationalUnfolding`. Future versions will support configuration.

- **失敗した実行の部分出力はクリーンアップされない。** Phase 3 が失敗した場合、Phase 1 と Phase 2 の出力はディレクトリに残る。これは設計上の意図であり、前段フェーズの出力は有効かつ再利用可能である。
- **RotationalUnfolding パスはハードコード。** 現在 `/Users/tshiota/Github/RotationalUnfolding` を仮定している。将来のバージョンで設定をサポート予定。

---

## Use Cases / 想定ユースケース

### Preprocessing for a New Polyhedron / 新しい多面体の前処理

A researcher studying a specific polyhedron runs the preprocessing pipeline:

特定の多面体を研究する際に、前処理パイプラインを実行する：

```bash
PYTHONPATH=python python -m preprocess --poly data/polyhedra/johnson/n21
```

Then runs Phase 4-6 as needed:

その後、必要に応じて Phase 4-6 を実行する：

```bash
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n21 --filter --noniso
```

### Reproducibility / 再現性

For paper artifacts or shared experiments, the full pipeline is reproducible with two commands:

論文アーティファクトや共有実験において、パイプライン全体が 2 つのコマンドで再現可能です：

```bash
# Preprocessing (Phase 1-3) / 前処理
PYTHONPATH=python python -m preprocess --poly data/polyhedra/johnson/n21

# Counting (Phase 4-6) / 数え上げ
PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n21 --filter --noniso
```

---

## Log Output / ログ出力

`preprocess` prints step markers to stdout before each phase. All subprocess output (stdout and stderr) is passed through without suppression.

`preprocess` は各フェーズの前にステップマーカーを stdout に出力します。すべてのサブプロセス出力（stdout・stderr）は抑制されずにそのまま表示されます。

```
[preprocess] Pipeline start: data/polyhedra/johnson/n21
[preprocess] Python: /path/to/python
[preprocess] Polyhedron (RotationalUnfolding): /path/to/RotationalUnfolding/data/polyhedra/johnson/n21/polyhedron.json
[preprocess] Exact unfoldings: /path/to/RotationalUnfolding/output/polyhedra/johnson/n21/exact.jsonl

[preprocess] Phase 1: edge_relabeling
... (Phase 1 output) ...

[preprocess] Phase 2: unfolding_expansion
... (Phase 2 output) ...

[preprocess] Phase 3: graph_export
... (Phase 3 output) ...

[preprocess] All preprocessing steps completed for: data/polyhedra/johnson/n21
[preprocess] Phase 4-6 can now be run with:
  PYTHONPATH=python python -m nonisomorphic --poly data/polyhedra/johnson/n21 [--filter] [--noniso]
```

On failure, the pipeline terminates with an error message indicating which step failed:

失敗時、パイプラインはどのステップで失敗したかを示すエラーメッセージと共に終了します：

```
[preprocess] FAILED at: Phase 3: graph_export (exit code 1)
```

---

## Module Location / モジュール配置

```
python/preprocess/
├── __init__.py
└── __main__.py
```

`preprocess` is a standalone package. It has no dependencies on other phases at the Python import level. All invocations are via `subprocess.run()`.

`preprocess` は独立したパッケージです。Python import レベルで他のフェーズへの依存はありません。すべての呼び出しは `subprocess.run()` 経由です。

---

## References / 参考資料

### Specification and Implementation

- **Phase 1 specification**: `docs/PHASE1_EDGE_RELABELING.md`
- **Phase 2 specification**: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- **Phase 3 specification**: `docs/PHASE3_GRAPH_DATA_CONVERSION.md`
- **Phase 4 specification**: `docs/PHASE4_SPANNING_TREE_ENUMERATION.md`
- **Phase 5 specification**: `docs/PHASE5_FILTERING.md`
- **Phase 6 specification**: `docs/PHASE6_NONISOMORPHIC_COUNTING.md`
- **preprocess implementation**: `python/preprocess/`

### 仕様と実装

- **Phase 1 仕様**: `docs/PHASE1_EDGE_RELABELING.md`
- **Phase 2 仕様**: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- **Phase 3 仕様**: `docs/PHASE3_GRAPH_DATA_CONVERSION.md`
- **Phase 4 仕様**: `docs/PHASE4_SPANNING_TREE_ENUMERATION.md`
- **Phase 5 仕様**: `docs/PHASE5_FILTERING.md`
- **Phase 6 仕様**: `docs/PHASE6_NONISOMORPHIC_COUNTING.md`
- **preprocess 実装**: `python/preprocess/`

---

**Document Status**: This document describes the **frozen specification** of `preprocess` as of 2026-02-08. The execution order and orchestration logic defined here are stable.

**文書ステータス**: この文書は 2026-02-08 時点での `preprocess` の**凍結された仕様**を記述します。ここで定義される実行順序とオーケストレーションロジックは安定しています。
