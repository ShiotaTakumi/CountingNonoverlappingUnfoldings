# drawing — Visualization Utility for Counting Pipeline

**Status**: Operational
**Last Updated**: 2026-02-12
**Purpose**: Counting パイプライン出力の可視化（JSONL → SVG）

---

## Overview / 概要

`drawing` モジュールは、Counting パイプラインの JSONL 出力を SVG ファイルとして可視化します。

**特徴**:
- RotationalUnfolding の `draw_raw.py` をベースに、Counting パイプライン専用に調整
- 幾何情報（`x`, `y`, `angle_deg`）を持つ任意の JSONL を描画可能
- 辺ラベル貼り替え後の `exact_relabeled.jsonl` の検証に最適

---

## Usage / 使い方

### 基本コマンド

```bash
cd /path/to/CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m drawing --jsonl <path_to_jsonl>
```

### オプション

- `--jsonl <path>`: 入力 JSONL ファイルのパス（必須）
- `--no-labels`: 面番号・辺番号を非表示（多角形のみ描画）

### 例

#### ラベル付きで描画（デフォルト）
```bash
PYTHONPATH=python python -m drawing --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
```

#### ラベルなしで描画
```bash
PYTHONPATH=python python -m drawing --jsonl data/polyhedra/archimedean/s12L/exact_relabeled.jsonl --no-labels
```

---

## Output / 出力

### 出力先

```
<polyhedron_dir>/draw/<jsonl_stem>/
```

#### 例
- 入力: `data/polyhedra/johnson/n20/exact_relabeled.jsonl`
- 出力: `data/polyhedra/johnson/n20/draw/exact_relabeled/`
  - `0.svg` — 1 レコード目
  - `1.svg` — 2 レコード目
  - ...

### SVG 仕様

- **座標系**: JSONL の `x`, `y` をそのまま使用
- **角度**: `angle_deg` を辺法線の向きとして解釈
- **スケール**: 正多角形の辺長 = 1、circumradius ベース
- **視覚要素**:
  - 面: 黒枠、塗りなし
  - 面番号: 中心に黒字（`--no-labels` 未指定時）
  - 辺番号: 共有辺上に赤字（`--no-labels` 未指定時）

---

## Module Structure / モジュール構造

```
python/drawing/
├── __init__.py       # パッケージ初期化
├── __main__.py       # エントリーポイント（python -m drawing）
├── cli.py            # CLI 実装
└── draw_raw.py       # SVG 描画ロジック（RotationalUnfolding から移植）
```

---

## Integration / 連携

### Phase 2 との連携

Phase 2 の `unfolding_expansion` が `exact_relabeled.jsonl` を生成した後、`drawing` で可視化することで、辺ラベル貼り替えの正確性を検証できます。

**ワークフロー例**:
```bash
# Step 1: 辺ラベル貼り替え
PYTHONPATH=python python -m unfolding_expansion --exact /path/to/exact.jsonl

# Step 2: 可視化
PYTHONPATH=python python -m drawing --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
```

### RotationalUnfolding との違い

| 項目 | RotationalUnfolding | CountingNonoverlappingUnfoldings |
|------|---------------------|----------------------------------|
| 入力 | `--poly <dir>` で polyhedron ディレクトリを指定 | `--jsonl <path>` で JSONL ファイルを直接指定 |
| 出力先 | `output/polyhedra/<class>/<name>/draw/<type>/` | `data/polyhedra/<class>/<name>/draw/<jsonl_stem>/` |
| 依存 | `poly_resolve` モジュール（リポジトリ構造に依存） | なし（JSONL パスから直接解決） |

---

## Implementation Notes / 実装メモ

### `draw_raw.py` について

- RotationalUnfolding の `python/drawing/draw_raw.py` を **そのままコピー** して使用
- 変更なし（スタンドアロンで動作するため）

### `cli.py` について

- CountingNonoverlappingUnfoldings 専用に新規実装
- `--jsonl` による直接パス指定方式を採用
- 出力ディレクトリは入力 JSONL のパスから自動解決

---

## Test Results / テスト結果

| Polyhedron | Records | SVG Files | Status |
|------------|---------|-----------|--------|
| johnson/n20 | 4 | 4 | ✅ |
| archimedean/s12L | 3 | 3 | ✅ |

---

## Future Work / 今後の拡張

1. **複数 JSONL の一括描画**:
   - 現在は 1 ファイルずつ指定が必要
   - ディレクトリ指定で複数ファイルを一括処理できると便利

2. **出力先のカスタマイズ**:
   - `--output-dir` オプションで出力先を明示的に指定可能にする

3. **描画スタイルのカスタマイズ**:
   - 色、線幅、フォントサイズなどの調整オプション

---

## References / 参考

- RotationalUnfolding: [`python/drawing/`](../../RotationalUnfolding/python/drawing/)
- Phase 2 Specification: [`docs/PHASE2_RELABELING_AND_ISOMORPHISM_EXPANSION_SPEC.md`](../../docs/PHASE2_RELABELING_AND_ISOMORPHISM_EXPANSION_SPEC.md)
