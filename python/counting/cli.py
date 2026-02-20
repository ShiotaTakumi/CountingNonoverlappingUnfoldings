"""
Spanning Tree Pipeline - Integrated CLI

Handles:
- Unified execution of spanning tree enumeration, overlap filtering,
  and nonisomorphic counting via Burnside's lemma
- Four execution modes via two orthogonal flags:
    Phase 4:     spanning trees only (default)
    Phase 4→5:   + overlap filter (--no-overlap)
    Phase 4→6:   + Burnside (--noniso)
    Phase 4→5→6: + both (--no-overlap --noniso)
- Path resolution for polyhedron data
- Output directory management
- Real-time progress reporting

全域木パイプライン統合 CLI:
- 全域木列挙・重なりフィルタ・Burnside の補題による非同型数え上げの統一実行
- 2 つの直交フラグによる 4 モード:
    Phase 4:     全域木のみ（デフォルト）
    Phase 4→5:   + 重なりフィルタ（--no-overlap）
    Phase 4→6:   + Burnside（--noniso）
    Phase 4→5→6: + 両方（--no-overlap --noniso）
- 多面体データのパス解決
- 出力ディレクトリ管理
- リアルタイム進捗報告

Usage:
    # Phase 4 (spanning tree count only)
    PYTHONPATH=python python -m counting --poly <polyhedron_dir>

    # Phase 4→5 (+ overlap filter)
    PYTHONPATH=python python -m counting --poly <polyhedron_dir> --no-overlap

    # Phase 4→6 (+ nonisomorphic counting)
    PYTHONPATH=python python -m counting --poly <polyhedron_dir> --noniso

    # Phase 4→5→6 (+ both)
    PYTHONPATH=python python -m counting --poly <polyhedron_dir> --no-overlap --noniso
"""

import argparse
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional


def get_polyhedron_info(polyhedron_dir: Path) -> tuple[str, str]:
    """
    Extract class and name from polyhedron directory path.

    多面体ディレクトリパスから class と name を取得。

    Args:
        polyhedron_dir (Path): Path like data/polyhedra/johnson/n20

    Returns:
        tuple: (class, name) such as ('johnson', 'n20')
    """
    parts = polyhedron_dir.parts

    # Find 'polyhedra' in path
    # パス中の 'polyhedra' を探す
    try:
        idx = parts.index('polyhedra')
        poly_class = parts[idx + 1]
        poly_name = parts[idx + 2]
        return poly_class, poly_name
    except (ValueError, IndexError):
        # Fallback: use last two parts
        # フォールバック: 最後の 2 要素を使用
        if len(parts) >= 2:
            return parts[-2], parts[-1]
        else:
            return "unknown", "unknown"


def run_pipeline(
    polyhedron_dir: Path,
    apply_filter: bool = False,
    apply_burnside: bool = True,
    output_base: Optional[Path] = None,
    split_depth: int = 0
) -> None:
    """
    Execute the spanning tree pipeline with configurable phases.

    設定可能なフェーズで全域木パイプラインを実行。

    Modes:
        apply_filter=False, apply_burnside=True  → Phase 4→6
        apply_filter=True,  apply_burnside=True  → Phase 4→5→6
        apply_filter=True,  apply_burnside=False → Phase 4→5

    Args:
        polyhedron_dir (Path): Path to polyhedron directory
        apply_filter (bool): Enable Phase 5 overlap filtering
        apply_burnside (bool): Enable Phase 6 Burnside's lemma
        output_base (Path, optional): Base directory for output/

    Outputs:
        - output/polyhedra/<class>/<name>/spanning_tree/result.json
    """
    # デフォルト設定
    if output_base is None:
        output_base = Path.cwd()

    # 多面体情報を取得
    poly_class, poly_name = get_polyhedron_info(polyhedron_dir)

    # モード文字列を構築
    # Build mode description string
    if apply_filter and apply_burnside:
        mode_str = "Phase 4→5→6 (Filter + Burnside)"
        phases = "Phase 4+5+6"
    elif apply_filter:
        mode_str = "Phase 4→5 (Filter)"
        phases = "Phase 4+5"
    elif apply_burnside:
        mode_str = "Phase 4→6 (Burnside)"
        phases = "Phase 4+6"
    else:
        mode_str = "Phase 4 (Spanning tree count)"
        phases = "Phase 4"

    print("=" * 60)
    print(f"Spanning Tree Pipeline: {mode_str}")
    print(f"  Polyhedron: {poly_class}/{poly_name}")
    print(f"  Input:      {polyhedron_dir}")
    print("=" * 60)
    print()

    # ファイルパスの設定
    grh_file = polyhedron_dir / "polyhedron.grh"
    edge_sets_file = polyhedron_dir / "unfoldings_edge_sets.jsonl"
    automorphisms_file = polyhedron_dir / "automorphisms.json"
    output_dir = output_base / "output" / "polyhedra" / poly_class / poly_name / "spanning_tree"
    result_file = output_dir / "result.json"

    # 入力ファイルの検証
    # Validate input files
    if not grh_file.exists():
        print(f"Error: File not found: {grh_file}")
        sys.exit(1)

    if apply_filter and not edge_sets_file.exists():
        print(f"Error: Edge sets file not found: {edge_sets_file}")
        print("  Phase 5 filtering requires unfoldings_edge_sets.jsonl")
        print("  Run Phase 3 first to generate this file.")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # ステップ数を決定
    # Determine total steps
    total_steps = 1  # C++ 実行は常に最後の 1 ステップ
    if apply_burnside:
        total_steps = 2  # 自己同型読み込み + C++ 実行
    current_step = 0

    # ====================================================================
    # Step: 自己同型データ読み込み（Phase 6 が有効な場合のみ）
    # Step: Load automorphisms (only if Phase 6 is enabled)
    # ====================================================================
    if apply_burnside:
        current_step += 1
        print(f"[Step {current_step}/{total_steps}] Loading automorphisms...")

        if not automorphisms_file.exists():
            print(f"Error: automorphisms.json not found: {automorphisms_file}")
            print("  Run Phase 3 (graph_export) first to generate this file.")
            sys.exit(1)

        with open(automorphisms_file, 'r') as f:
            automorphisms_data = json.load(f)

        group_order = automorphisms_data["group_order"]
        print(f"  Group order: {group_order}")
        print(f"  Loaded from: {automorphisms_file}")
        print()

    # ====================================================================
    # Step: C++ spanning_tree_zdd 実行
    # Step: Run C++ spanning_tree_zdd
    # ====================================================================
    current_step += 1
    print(f"[Step {current_step}/{total_steps}] Running C++ spanning_tree_zdd ({phases})...")

    # C++ バイナリのパスを解決
    cpp_binary = (
        Path(__file__).parent.parent.parent
        / "cpp" / "spanning_tree_zdd" / "build" / "spanning_tree_zdd"
    )

    if not cpp_binary.exists():
        print(f"Error: C++ binary not found: {cpp_binary}")
        print("Please build it first:")
        print("  cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make")
        sys.exit(1)

    # C++ コマンドを構築
    # Build C++ command
    cmd = [str(cpp_binary), str(grh_file)]

    if apply_filter:
        cmd.append(str(edge_sets_file))

    if apply_burnside:
        cmd.extend(["--automorphisms", str(automorphisms_file)])

    if split_depth > 0:
        cmd.extend(["--split-depth", str(split_depth)])

    # stdout をフラッシュして、C++ の stderr と順序が混ざらないようにする
    # Flush stdout so Python output appears before C++ stderr
    sys.stdout.flush()

    # C++ 実行（stderr はリアルタイム表示、stdout のみキャプチャ）
    # Execute C++ (stderr streams in real-time, only stdout is captured)
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=None,  # stderr → 端末にリアルタイム出力
            text=True,
            check=True
        )

        # stdout は JSON
        json_output = result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Error: C++ binary failed (exit code {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to run C++ binary: {e}")
        sys.exit(1)

    # JSON をパース
    try:
        result_data = json.loads(json_output)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON output: {e}")
        print("Output was:", json_output)
        sys.exit(1)

    # result.json に保存
    with open(result_file, 'w') as f:
        json.dump(result_data, f, indent=2)

    print()
    print(f"Saved: {result_file}")
    print()

    # ====================================================================
    # 結果サマリー
    # Results summary
    # ====================================================================
    print("=" * 60)
    print(f"Pipeline Complete! ({mode_str})")
    print()
    print("Results:")

    # Phase 4
    print(f"  Spanning trees (labeled):    {result_data['phase4']['spanning_tree_count']}")

    # Phase 5
    if apply_filter and 'phase5' in result_data:
        p5 = result_data['phase5']
        if p5.get('filter_applied'):
            print(f"  Non-overlapping (labeled):   {p5.get('non_overlapping_count', 'N/A')}")
            print(f"  MOPEs applied:               {p5.get('num_mopes', 'N/A')}")

    # Phase 6
    if apply_burnside and 'phase6' in result_data:
        p6 = result_data['phase6']
        if p6.get('burnside_applied'):
            print(f"  Nonisomorphic:               {p6['nonisomorphic_count']}")
            print(f"  Group order |Aut(Γ)|:        {p6['group_order']}")

    print()
    print(f"Output: {result_file}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Spanning tree pipeline with optional overlap filtering "
            "and nonisomorphic counting via Burnside's lemma.\n"
            "全域木パイプライン: 重なりフィルタおよび Burnside の補題による非同型数え上げ"
        )
    )

    parser.add_argument(
        "--poly",
        type=str,
        required=True,
        help="多面体ディレクトリへのパス（例: data/polyhedra/johnson/n20）"
    )

    parser.add_argument(
        "--no-overlap",
        action="store_true",
        help="Phase 5 重なりフィルタを有効化（unfoldings_edge_sets.jsonl が必要）"
    )

    parser.add_argument(
        "--noniso",
        action="store_true",
        help="Phase 6 Burnside の補題による非同型数え上げを有効化"
    )

    parser.add_argument(
        "--split-depth",
        type=int,
        default=0,
        help="ZDD を 2^N パーティションに分割しピークメモリ削減（デフォルト: 0 = 分割なし）"
    )

    parser.add_argument(
        "--output-base",
        type=str,
        default=None,
        help="出力ベースディレクトリ（デフォルト: カレントディレクトリ）"
    )

    args = parser.parse_args()

    polyhedron_dir = Path(args.poly)

    if not polyhedron_dir.exists():
        print(f"Error: Directory not found: {polyhedron_dir}")
        sys.exit(1)

    apply_filter = args.no_overlap
    apply_burnside = args.noniso
    output_base = Path(args.output_base) if args.output_base else None

    try:
        run_pipeline(polyhedron_dir, apply_filter, apply_burnside, output_base,
                     split_depth=args.split_depth)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
