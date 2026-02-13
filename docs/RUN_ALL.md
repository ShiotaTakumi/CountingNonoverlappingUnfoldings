# run_all — Full Pipeline Execution in a Single Command

**Status**: Implemented (Specification Frozen)
**Version**: 1.0.0
**Last Updated**: 2026-02-13

---

## Overview / 概要

`run_all` is a researcher-oriented utility that executes the entire counting non-overlapping unfoldings pipeline—from edge relabeling to MOPE-based filtering—with a single command and a single argument.

`run_all` は研究者向けユーティリティであり、非重複展開図カウントパイプライン全体（辺ラベル貼り替えから MOPE ベースのフィルタリングまで）を、1 つのコマンドと 1 つの引数で実行します。

**This is an orchestrator, not a processing module.** `run_all` does not implement any algorithm. It invokes Phase 1, Phase 2, Phase 3, Phase 4 & 5 as independent subprocesses, in a fixed order. Each phase runs its own CLI exactly as if the researcher had typed the command manually.

**これはオーケストレーターであり、処理モジュールではありません。** `run_all` はアルゴリズムを一切実装しません。Phase 1、Phase 2、Phase 3、Phase 4 & 5 を独立したサブプロセスとして固定順序で呼び出します。各フェーズは、研究者が手動でコマンドを入力した場合とまったく同じ CLI を実行します。

---

## Purpose and Motivation / 目的と動機

### Why run_all Exists / なぜ run_all が必要か

The counting pipeline consists of five independent stages (Phase 1-5). Running them manually requires multiple separate commands with careful path management. This is:

- **Error-prone**: A typo in one command produces inconsistent outputs across phases.
- **Tedious**: Researchers must wait for each phase to finish before starting the next.
- **Undocumented by default**: Without a single entry point, reproducing a full run requires knowledge of all phase commands and their input/output locations.

`run_all` eliminates these issues. It provides:

- **One command, minimal arguments**: `--poly` is the only required input.
- **Reproducibility by invocation**: A single shell command fully reproduces the pipeline.
- **Fail-fast behavior**: If any phase fails, execution stops immediately.

カウンティングパイプラインは 5 つの独立した段階（Phase 1-5）で構成されています。手動実行には、慎重なパス管理を伴う複数の個別コマンドが必要です。これは：

- **ミスを誘発する**: 1 つのコマンドのタイプミスがフェーズ間で不整合な出力を生む
- **煩雑である**: 各フェーズの完了を待ってから次を開始する必要がある
- **再現手順が暗黙知になる**: 単一のエントリポイントなしに完全な実行を再現するには、すべてのフェーズコマンドとその入出力場所の知識が必要

`run_all` はこれらの問題を排除します：

- **1 コマンド、最小限の引数**: `--poly` が必須の唯一の入力
- **呼び出しによる再現性**: 単一のシェルコマンドでパイプライン全体を再現可能
- **即時停止**: いずれかのフェーズが失敗した場合、実行は即座に停止

### What run_all Automates / run_all が自動化する範囲

|| Step | Module | Output |
||------|--------|--------|
|| Phase 1 | `edge_relabeling` | `polyhedron_relabeled.json`, `edge_mapping.json` |
|| Phase 2 | `unfolding_expansion` | `exact_relabeled.jsonl`, `unfoldings_overlapping_all.jsonl` |
|| Phase 3 | `graph_export` | `polyhedron.grh`, `unfoldings_edge_sets.jsonl` |
|| Phase 4 & 5 | `spanning_tree_zdd` (with filtering) | `spanning_tree/result.json` |

All phases are executed sequentially. Phase 4 and Phase 5 are combined in a single C++ binary execution.

すべてのフェーズは順次実行されます。Phase 4 と Phase 5 は単一の C++ バイナリ実行で結合されています。

---

## Usage / 使用方法

### Command / コマンド

```bash
PYTHONPATH=python python -m run_all --poly data/polyhedra/<class>/<name>
```

### Examples / 実行例

```bash
# Johnson solid n21
PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n21

# Antiprism a12
PYTHONPATH=python python -m run_all --poly data/polyhedra/antiprism/a12

# Archimedean solid s07
PYTHONPATH=python python -m run_all --poly data/polyhedra/archimedean/s07
```

### Arguments / 引数

|| Argument | Required | Description |
||----------|----------|-------------|
|| `--poly data/polyhedra/CLASS/NAME` | Yes | Path to polyhedron data directory (e.g., `data/polyhedra/johnson/n21`). Shell Tab completion is supported. / 多面体データディレクトリへのパス。Tab 補完対応。 |

---

## Prerequisites / 前提条件

`run_all` requires:

1. **RotationalUnfolding pipeline completion**: The following files must exist in RotationalUnfolding repository:
   - `RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json` (Phase 1 input)
   - `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl` (Phase 2 input)

2. **Hardcoded path**: Currently assumes RotationalUnfolding is at `/Users/tshiota/Github/RotationalUnfolding`. This will be made configurable in future versions.

3. **C++ binary**: `cpp/spanning_tree_zdd/build/spanning_tree_zdd` must be built (see Phase 4/5 documentation).

`run_all` は以下を必要とします：

1. **RotationalUnfolding パイプラインの完了**: RotationalUnfolding リポジトリに以下のファイルが存在する必要があります：
   - `RotationalUnfolding/data/polyhedra/<class>/<name>/polyhedron.json`（Phase 1 入力）
   - `RotationalUnfolding/output/polyhedra/<class>/<name>/exact.jsonl`（Phase 2 入力）

2. **ハードコードされたパス**: 現在 RotationalUnfolding が `/Users/tshiota/Github/RotationalUnfolding` にあることを仮定しています。将来のバージョンで設定可能にする予定です。

3. **C++ バイナリ**: `cpp/spanning_tree_zdd/build/spanning_tree_zdd` がビルドされている必要があります（Phase 4/5 ドキュメント参照）。

---

## Execution Order / 実行順序

`run_all` executes exactly four steps, in this fixed order. The order is not configurable.

`run_all` は正確に 4 つのステップを、この固定順序で実行します。順序は変更できません。

### Step 1: Phase 1 — Edge Relabeling / 辺ラベル貼り替え

```
[run_all] Phase 1: edge_relabeling
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
[run_all] Phase 2: unfolding_expansion
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
[run_all] Phase 3: graph_export
```

Invokes:

```bash
python -m graph_export --poly data/polyhedra/<class>/<name>/polyhedron_relabeled.json
```

- Reads relabeled polyhedron (read-only).
- Generates TdZdd-compatible graph representation.
- Produces `polyhedron.grh` and `unfoldings_edge_sets.jsonl` in `data/polyhedra/<class>/<name>/`.
- Overwrites existing files.

### Step 4: Phase 4 & 5 — Spanning Tree ZDD with Filtering / ZDD 構築とフィルタリング

```
[run_all] Phase 4 & 5: spanning_tree_zdd (with filtering)
```

Invokes:

```bash
python -m spanning_tree_zdd --grh data/polyhedra/<class>/<name>/polyhedron.grh --edge-sets data/polyhedra/<class>/<name>/unfoldings_edge_sets.jsonl
```

- Reads polyhedron graph and MOPE edge sets (read-only).
- Constructs spanning tree ZDD (Phase 4).
- Applies MOPE-based filtering (Phase 5).
- Produces `output/polyhedra/<class>/<name>/spanning_tree/result.json`.
- Overwrites existing files.

---

## Output Directory Structure / 出力ディレクトリ構造

After a complete `run_all` execution, the directory structure is as follows:

`run_all` の完全な実行後、ディレクトリ構造は以下のようになります：

```
data/polyhedra/<class>/<name>/
├── polyhedron_relabeled.json     # Phase 1: relabeled polyhedron structure
├── edge_mapping.json             # Phase 1: old → new edge ID mapping
├── exact_relabeled.jsonl         # Phase 2: relabeled exact unfoldings
├── unfoldings_overlapping_all.jsonl  # Phase 2: expanded isomorphic variants
├── polyhedron.grh                # Phase 3: TdZdd graph format
└── unfoldings_edge_sets.jsonl    # Phase 3: MOPE edge sets

output/polyhedra/<class>/<name>/
└── spanning_tree/
    └── result.json               # Phase 4 & 5: final count with statistics
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
  ↓ Phase 4 & 5: spanning_tree_zdd (filtering)
output/polyhedra/<class>/<name>/spanning_tree/result.json
```

Each downstream output depends on its upstream input. The final result is the count of non-overlapping unfoldings.

各下流出力は上流入力に依存します。最終結果は非重複展開図の個数です。

---

## Guarantees / 保証事項

### Pipeline Integrity / パイプラインの整合性

- **Each phase is invoked as an independent subprocess.** `run_all` does not import or call any phase's internal functions. Each phase runs its own CLI entry point.
- **No data is generated by `run_all` itself.** All JSON/JSONL files are produced by their respective phases.
- **Existing outputs are overwritten.** Each phase overwrites its own output file if it already exists. This is the intended behavior.
- **Failure stops the pipeline.** If any phase exits with a non-zero status, `run_all` terminates immediately. Subsequent phases are not executed.
- **Order is deterministic.** Phase 1 → Phase 2 → Phase 3 → Phase 4 & 5. Always.

- **各フェーズは独立したサブプロセスとして呼び出される。** `run_all` はいかなるフェーズの内部関数もインポート・呼び出ししない。各フェーズは自身の CLI エントリポイントを実行する。
- **`run_all` 自体はデータを生成しない。** すべての JSON/JSONL ファイルはそれぞれのフェーズが生成する。
- **既存の出力は上書きされる。** 各フェーズは自身の出力ファイルが既に存在する場合、上書きする。これは意図された動作である。
- **失敗はパイプラインを停止する。** いずれかのフェーズがゼロ以外のステータスで終了した場合、`run_all` は即座に終了する。後続フェーズは実行されない。
- **順序は決定論的である。** Phase 1 → Phase 2 → Phase 3 → Phase 4 & 5。常に。

### Architectural Separation / アーキテクチャ的分離

- **All phases are independent modules.** `run_all` does not create coupling between them.
- **Each phase's code is untouched.** `run_all` exists in `python/run_all/` and does not modify any file in other phase directories.
- **RotationalUnfolding dependency is explicit.** Phase 1 and Phase 2 require RotationalUnfolding outputs. This cross-repository dependency is documented and checked at runtime.

- **すべてのフェーズは独立したモジュールである。** `run_all` はそれらの間の結合を生み出さない。
- **各フェーズのコードは変更されない。** `run_all` は `python/run_all/` に存在し、他のフェーズディレクトリ内のいかなるファイルも変更しない。
- **RotationalUnfolding 依存は明示的である。** Phase 1 と Phase 2 は RotationalUnfolding の出力を必要とする。このリポジトリ間依存は文書化され、実行時にチェックされる。

---

## Non-Guarantees / 非保証事項

- **Execution time is not bounded.** Phase 4 & 5 use ZDD operations which can be time-consuming for large polyhedra. For complex cases (e.g., s12L), execution may take hours or days.
- **Partial outputs from failed runs are not cleaned up.** If Phase 3 fails, Phase 1 and Phase 2 outputs remain in the directory. This is by design—earlier phases' outputs are valid and reusable.
- **RotationalUnfolding path is hardcoded.** Currently assumes `/Users/tshiota/Github/RotationalUnfolding`. Future versions will support configuration.

- **実行時間は保証されない。** Phase 4 & 5 は ZDD 演算を使用し、大きな多面体では時間がかかる場合がある。複雑なケース（例：s12L）では、実行に数時間〜数日かかることがある。
- **失敗した実行の部分出力はクリーンアップされない。** Phase 3 が失敗した場合、Phase 1 と Phase 2 の出力はディレクトリに残る。これは設計上の意図であり、前段フェーズの出力は有効かつ再利用可能である。
- **RotationalUnfolding パスはハードコード。** 現在 `/Users/tshiota/Github/RotationalUnfolding` を仮定している。将来のバージョンで設定をサポート予定。

---

## Use Cases / 想定ユースケース

### Full Pipeline Execution / パイプライン一括実行

A researcher studying a specific polyhedron runs the entire pipeline from scratch:

特定の多面体を研究する際に、パイプライン全体をゼロから実行する：

```bash
PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n21
```

This produces all outputs (relabeled polyhedron, expanded unfoldings, graph data, final count) in a single invocation.

これにより、すべての出力（貼り替え済み多面体、展開図、グラフデータ、最終カウント）が単一の呼び出しで生成されます。

### Reproducibility / 再現性

For paper artifacts or shared experiments, the full pipeline is reproducible with a single command:

論文アーティファクトや共有実験において、パイプライン全体が単一のコマンドで再現可能です：

```bash
# Reproduce the complete result for johnson n21
PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n21
```

The command is self-contained (assuming RotationalUnfolding prerequisite is met).

コマンドは自己完結しています（RotationalUnfolding の前提条件が満たされている場合）。

---

## Log Output / ログ出力

`run_all` prints step markers to stdout before each phase. All subprocess output (stdout and stderr) is passed through without suppression.

`run_all` は各フェーズの前にステップマーカーを stdout に出力します。すべてのサブプロセス出力（stdout・stderr）は抑制されずにそのまま表示されます。

```
[run_all] Pipeline start: data/polyhedra/johnson/n21
[run_all] Python: /path/to/python
[run_all] Polyhedron (RotationalUnfolding): /path/to/RotationalUnfolding/data/polyhedra/johnson/n21/polyhedron.json
[run_all] Exact unfoldings: /path/to/RotationalUnfolding/output/polyhedra/johnson/n21/exact.jsonl

[run_all] Phase 1: edge_relabeling
... (Phase 1 output) ...

[run_all] Phase 2: unfolding_expansion
... (Phase 2 output) ...

[run_all] Phase 3: graph_export
... (Phase 3 output) ...

[run_all] Phase 4 & 5: spanning_tree_zdd (with filtering)
... (Phase 4 & 5 output) ...

[run_all] All steps completed for: data/polyhedra/johnson/n21
[run_all] Results: output/polyhedra/johnson/n21/spanning_tree/result.json
```

On failure, the pipeline terminates with an error message indicating which step failed:

失敗時、パイプラインはどのステップで失敗したかを示すエラーメッセージと共に終了します：

```
[run_all] FAILED at: Phase 3: graph_export (exit code 1)
```

---

## Module Location / モジュール配置

```
python/run_all/
├── __init__.py
└── __main__.py
```

`run_all` is a standalone package. It has no dependencies on other phases at the Python import level. All invocations are via `subprocess.run()`.

`run_all` は独立したパッケージです。Python import レベルで他のフェーズへの依存はありません。すべての呼び出しは `subprocess.run()` 経由です。

---

## References / 参考資料

### Specification and Implementation

- **Phase 1 specification**: `docs/PHASE1_EDGE_RELABELING.md`
- **Phase 2 specification**: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- **Phase 3 specification**: `docs/PHASE3_GRAPH_DATA_CONVERSION.md`
- **Phase 4 specification**: `docs/PHASE4_SPANNING_TREE_ENUMERATION.md`
- **Phase 5 specification**: `docs/PHASE5_FILTERING.md`
- **run_all implementation**: `python/run_all/`

### 仕様と実装

- **Phase 1 仕様**: `docs/PHASE1_EDGE_RELABELING.md`
- **Phase 2 仕様**: `docs/PHASE2_UNFOLDING_EXPANSION.md`
- **Phase 3 仕様**: `docs/PHASE3_GRAPH_DATA_CONVERSION.md`
- **Phase 4 仕様**: `docs/PHASE4_SPANNING_TREE_ENUMERATION.md`
- **Phase 5 仕様**: `docs/PHASE5_FILTERING.md`
- **run_all 実装**: `python/run_all/`

---

**Document Status**: This document describes the **frozen specification** of `run_all` as of 2026-02-13. The execution order and orchestration logic defined here are stable.

**文書ステータス**: この文書は 2026-02-13 時点での `run_all` の**凍結された仕様**を記述します。ここで定義される実行順序とオーケストレーションロジックは安定しています。
