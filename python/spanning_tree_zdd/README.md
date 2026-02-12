# Phase 4: ZDD による全域木列挙

**Status**: 実装完了  
**Version**: 1.0.0  
**Last Updated**: 2026-02-12

---

## 概要

Phase 4 は、多面体グラフに対する ZDD（Zero-suppressed Binary Decision Diagram）ベースの全域木列挙を実装します。Phase 3 が生成した `polyhedron.grh` ファイルを入力として受け取り、TdZdd ライブラリを用いて全域木を表現する ZDD を構築し、その個数を JSON 形式で出力します。

**重要:** このフェーズは重なりフィルタリングを行いません。それは Phase 5 の責務です。Phase 4 では組合せ的に全域木の個数を数えるのみです。

---

## 目的と範囲

### Phase 4 が行うこと

1. **グラフの読み込み**: Phase 3 が生成した `polyhedron.grh` を読み込む
2. **ZDD 構築**: TdZdd を用いて全域木集合を ZDD として構築
3. **個数計算**: ZDD のカーディナリティ（解の個数）を計算
4. **時間計測**: ZDD 構築時間とカーディナリティ計算時間を計測
5. **JSON 出力**: 結果を構造化された JSON 形式で出力

### Phase 4 が行わないこと

- **重なり判定**: 展開図の重なり判定は Phase 5 の責務
- **展開図データの処理**: 展開図の辺集合データは使用しない
- **フィルタリング**: 非重複展開図の抽出は Phase 5 で実装
- **幾何計算**: 座標や角度の計算は行わない
- **バッチ処理**: 各多面体は個別に処理する必要がある

---

## 使用方法

### 前提条件

C++ バイナリをビルドする必要があります：

```bash
cd CountingNonoverlappingUnfoldings/cpp/spanning_tree_zdd
mkdir -p build
cd build
cmake ..
make
```

ビルド成功後、実行ファイル `spanning_tree_zdd` が `cpp/spanning_tree_zdd/build/` に生成されます。

### コマンドライン実行

```bash
cd CountingNonoverlappingUnfoldings
PYTHONPATH=python python -m spanning_tree_zdd --grh <path_to_polyhedron.grh>
```

### 実行例

**johnson/n20（五角柱台）:**

```bash
PYTHONPATH=python python -m spanning_tree_zdd \
  --grh data/polyhedra/johnson/n20/polyhedron.grh
```

出力例:
```
============================================================
Phase 4: Spanning Tree Enumeration
Polyhedron: johnson/n20
============================================================
Input: data/polyhedra/johnson/n20/polyhedron.grh
Output: output/polyhedra/johnson/n20/spanning_tree/result.json
============================================================
Running ZDD construction...
✓ Result saved to: output/polyhedra/johnson/n20/spanning_tree/result.json
============================================================
Vertices: 25
Edges: 45
Build time: 3.55 ms
Count time: 0.49 ms
Spanning tree count: 29821320745
============================================================
```

**archimedean/s12L（ねじれ立方体）:**

```bash
PYTHONPATH=python python -m spanning_tree_zdd \
  --grh data/polyhedra/archimedean/s12L/polyhedron.grh
```

出力例:
```
============================================================
Phase 4: Spanning Tree Enumeration
Polyhedron: archimedean/s12L
============================================================
Input: data/polyhedra/archimedean/s12L/polyhedron.grh
Output: output/polyhedra/archimedean/s12L/spanning_tree/result.json
============================================================
Running ZDD construction...
✓ Result saved to: output/polyhedra/archimedean/s12L/spanning_tree/result.json
============================================================
Vertices: 24
Edges: 60
Build time: 3.88 ms
Count time: 0.52 ms
Spanning tree count: 89904012853248
============================================================
```

---

## 入力ファイル

### polyhedron.grh (Phase 3 出力)

**Path:** `data/polyhedra/<class>/<name>/polyhedron.grh`

**形式:**
- プレーンテキスト、ヘッダーなし
- 1行1辺: `v1 v2`（空白区切り）
- 0-indexed 頂点
- 辺は edge_id 順（Phase 1 の順序を保持）

**例（johnson/n20 の最初の5行）:**
```
5 6
0 6
6 7
0 1
1 7
```

---

## 出力形式

### JSON ファイル出力

Phase 4 は結果を `output/polyhedra/<class>/<name>/spanning_tree/result.json` に保存します。

**出力パス:**
```
output/
└── polyhedra/
    ├── johnson/
    │   └── n20/
    │       └── spanning_tree/
    │           └── result.json
    └── archimedean/
        └── s12L/
            └── spanning_tree/
                └── result.json
```

**JSON フィールド:**
- `input_file`: 入力ファイルのパス
- `vertices`: 頂点数
- `edges`: 辺数
- `build_time_ms`: ZDD 構築時間（ミリ秒）
- `count_time_ms`: カーディナリティ計算時間（ミリ秒）
- `spanning_tree_count`: 全域木の個数（文字列形式、大きな数値に対応）

**result.json の例:**
```json
{
  "input_file": "data/polyhedra/johnson/n20/polyhedron.grh",
  "vertices": 25,
  "edges": 45,
  "build_time_ms": 3.55,
  "count_time_ms": 0.49,
  "spanning_tree_count": "29821320745"
}
```

---

## テスト結果

### Test Case 1: johnson/n20

**入力:**
- ファイル: `data/polyhedra/johnson/n20/polyhedron.grh`
- 頂点数: 25
- 辺数: 45

**結果:**
- 全域木の個数: 29,821,320,745
- ZDD 構築時間: 約 5 ms
- カーディナリティ計算時間: 約 0.6 ms
- ステータス: ✅ 成功

### Test Case 2: archimedean/s12L

**入力:**
- ファイル: `data/polyhedra/archimedean/s12L/polyhedron.grh`
- 頂点数: 24
- 辺数: 60

**結果:**
- 全域木の個数: 89,904,012,853,248
- ZDD 構築時間: 約 4 ms
- カーディナリティ計算時間: 約 0.5 ms
- ステータス: ✅ 成功

### 検証項目

Phase 4 では以下を検証:

1. ✅ プログラムがエラーなく実行される
2. ✅ JSON 形式で正しく出力される
3. ✅ `spanning_tree_count` が正の整数である
4. ✅ 実行時間が妥当な範囲内である（数ミリ秒）

**注:** 値の正しさの厳密な検証は Phase 5 で行います（重なりフィルタリング実装後）。

---

## モジュール構成

```
python/spanning_tree_zdd/
├── __init__.py       # モジュール説明
├── __main__.py       # python -m spanning_tree_zdd のエントリーポイント
├── cli.py            # CLI 実装（C++ バイナリ実行とラップ）
└── README.md         # このファイル
```

**各モジュールの責務:**

| モジュール | 責務 |
|-----------|------|
| `cli.py` | コマンドライン引数解析、C++ バイナリ実行、JSON パース、結果表示 |
| `__main__.py` | Python モジュールとしての実行エントリーポイント |
| `__init__.py` | モジュールドキュメントと Phase 4 の役割説明 |

---

## アルゴリズム概要

### ZDD による全域木列挙

Phase 4 は **frontier-based search** アルゴリズムを用いて全域木を列挙します。

**アルゴリズムの流れ:**

1. **グラフの読み込み**
   - TdZdd の `Graph::readEdges()` で `.grh` ファイルを読み込み
   - 頂点は文字列として扱われ、内部で 1-indexed に変換される

2. **フロンティア管理**
   - `FrontierManager` がフロンティア（処理中の頂点集合）を管理
   - 各辺の処理時にフロンティアに入る頂点・出る頂点を追跡

3. **ZDD 構築**
   - `SpanningTree` クラスが ZDD の再帰的仕様を定義
   - 各辺について「選ぶ（1-枝）」「選ばない（0-枝）」を決定
   - サイクル形成をチェックし、枝刈りを実行
   - 最終的に連結グラフを形成する辺集合のみを受理

4. **カーディナリティ計算**
   - ZDD の解の個数を `zddCardinality()` で計算
   - TdZdd の BigNumber クラスで大きな数値にも対応

**時間計算量:** O(E × F × α(V))
- E = 辺数
- F = フロンティアサイズ（通常は O(√V)）
- α = Union-Find の逆アッカーマン関数

---

## C++ 実装との連携

Python 側は薄いラッパーで、実際の ZDD 構築は C++ バイナリが行います。

### C++ バイナリ

**場所:** `cpp/spanning_tree_zdd/build/spanning_tree_zdd`

**入力:** `polyhedron.grh` ファイルパス（コマンドライン引数）

**出力:** JSON 形式の結果（標準出力）

**使用ライブラリ:**
- TdZdd: ZDD 構築とカーディナリティ計算
- frontier_basic_tdzdd: フロンティア管理

### Python ラッパー

Python の `cli.py` は以下を行います:

1. コマンドライン引数のパース
2. 入力ファイルとバイナリの存在確認
3. .grh ファイルのパスから多面体情報（class/name）を抽出
4. C++ バイナリを `subprocess` で実行
5. JSON 出力をパース
6. `output/polyhedra/<class>/<name>/spanning_tree/result.json` に保存
7. 人間が読みやすい形式で結果を表示

---

## Phase 5 への準備

Phase 4 は Phase 5（重なりフィルタリング）の準備として、以下を提供します:

1. **ZDD 構築の実証**: TdZdd 統合が正しく動作することを確認
2. **ベースライン個数**: フィルタリング前の全域木個数を提供
3. **実行時間の基準**: ZDD 構築の性能基準を確立
4. **拡張可能な設計**: Phase 5 で制約条件を追加しやすい構造

Phase 5 では、`SpanningTree` に加えて以下を実装予定:

- `UnfoldingFilter`: 展開図の重なり判定
- 制約条件の統合: ZDD のサブセット演算で非重複展開図を抽出

---

## エラーハンドリング

### 一般的なエラーと対処法

**1. Binary not found**

```
FileNotFoundError: Binary not found: cpp/spanning_tree_zdd/build/spanning_tree_zdd
```

**対処法:** C++ バイナリをビルドしてください。

```bash
cd cpp/spanning_tree_zdd/build
cmake .. && make
```

**2. Input file not found**

```
FileNotFoundError: Input file not found: data/polyhedra/johnson/n20/polyhedron.grh
```

**対処法:** Phase 3 を実行して `polyhedron.grh` を生成してください。

```bash
PYTHONPATH=python python -m graph_export \
  --poly data/polyhedra/johnson/n20/polyhedron_relabeled.json
```

**3. Unexpected path format**

```
ValueError: Unexpected path format: <path>
Expected: data/polyhedra/<class>/<name>/polyhedron.grh
```

**対処法:** 入力ファイルのパスが正しい形式（`data/polyhedra/<class>/<name>/polyhedron.grh`）であることを確認してください。

**4. C++ binary failed**

```
RuntimeError: C++ binary failed: <error message>
```

**対処法:** エラーメッセージを確認し、入力ファイルの形式が正しいか確認してください。

## 出力ファイルの確認

結果が正しく保存されたか確認:

```bash
# ファイルの存在確認
ls -l output/polyhedra/johnson/n20/spanning_tree/result.json

# JSON の内容確認
cat output/polyhedra/johnson/n20/spanning_tree/result.json | python3 -m json.tool
```

---

## パフォーマンス

### 実行時間

**johnson/n20:**
- ZDD 構築: 約 5 ms
- カーディナリティ計算: 約 0.6 ms
- 合計: 約 6 ms

**archimedean/s12L:**
- ZDD 構築: 約 4 ms
- カーディナリティ計算: 約 0.5 ms
- 合計: 約 5 ms

### スケーラビリティ

Phase 4 は小〜中規模のグラフ（頂点数 20-30、辺数 40-70）で高速に動作します。より大きなグラフでも、フロンティアサイズが小さければ効率的に処理できます。

---

## 関連ドキュメント

- **Phase 3 仕様:** `docs/PHASE3_GRAPH_DATA_CONVERSION.md`
- **Phase 4 仕様:** `docs/PHASE4_SPANNING_TREE_ENUMERATION.md`（作成予定）
- **Phase 4 実装計画:** `.cursor/plans/phase_4_implementation_plan_*.plan.md`
- **TdZdd ドキュメント:** `lib/tdzdd/`
- **FrontierManager:** `lib/frontier_basic_tdzdd/FrontierManager.hpp`

---

## 実装状況

| タスク | ステータス |
|--------|----------|
| ✅ ディレクトリ構造作成 | 完了 |
| ✅ SpanningTree コードのコピー | 完了 |
| ✅ main.cpp 実装 | 完了 |
| ✅ CMakeLists.txt 作成 | 完了 |
| ✅ C++ バイナリビルド | 完了 |
| ✅ johnson/n20 テスト | 完了 |
| ✅ archimedean/s12L テスト | 完了 |
| ✅ Python CLI 実装 | 完了 |
| ✅ Python エンドツーエンドテスト | 完了 |
| ✅ README.md 作成 | 完了 |
| ⏳ 正式仕様書作成 | 次のステップ |

---

**Phase 4 実装完了日:** 2026-02-12
