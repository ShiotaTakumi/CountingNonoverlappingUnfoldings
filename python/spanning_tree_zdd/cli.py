"""
CLI - Phase 4 + Phase 5: ZDD-based Spanning Tree Enumeration and Filtering

Handles:
- Command-line argument parsing for Phase 4 and Phase 5
- C++ binary execution and result collection
- JSON output file management for output/ directory
- Progress reporting and result display
- Does NOT modify any data files

CLI — Phase 4 + Phase 5: ZDD による全域木列挙とフィルタリング:
- Phase 4 と Phase 5 のコマンドライン引数解析
- C++ バイナリ実行と結果収集
- output/ ディレクトリへの JSON 出力ファイル管理
- 進捗報告と結果表示
- データファイルは一切変更しない

Responsibility in Phase 4 + Phase 5:
- Phase 4: Provides user-facing CLI for spanning tree counting
- Phase 5: Optionally applies MOPE-based filtering for non-overlapping unfoldings
- Wraps C++ binary execution in Python environment
- Validates input files and binary existence
- Saves results to output/polyhedra/<class>/<name>/spanning_tree/result.json
- Reports results in human-readable format

Phase 4 + Phase 5 における責務:
- Phase 4: 全域木数え上げのためのユーザー向け CLI を提供
- Phase 5: オプションで MOPE ベースのフィルタリングで非重複展開図を抽出
- Python 環境で C++ バイナリ実行をラップ
- 入力ファイルとバイナリの存在を検証
- output/polyhedra/<class>/<name>/spanning_tree/result.json に結果を保存
- 人間が読みやすい形式で結果を報告
"""

import argparse
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple


def get_polyhedron_info_from_grh(grh_path: Path) -> Tuple[str, str]:
    """
    Extract class and name from .grh file path.

    .grh ファイルのパスから class と name を抽出。

    Args:
        grh_path: Path to polyhedron.grh file
                  Expected: data/polyhedra/<class>/<name>/polyhedron.grh

    Returns:
        tuple: (class, name) such as ('johnson', 'n20')

    Raises:
        ValueError: If path format is unexpected
    """
    parts = grh_path.parts

    # Expected path: data/polyhedra/<class>/<name>/polyhedron.grh
    # or absolute path ending with: .../data/polyhedra/<class>/<name>/polyhedron.grh
    try:
        polyhedra_idx = parts.index('polyhedra')
        poly_class = parts[polyhedra_idx + 1]
        poly_name = parts[polyhedra_idx + 2]
        return poly_class, poly_name
    except (ValueError, IndexError):
        raise ValueError(
            f"Unexpected path format: {grh_path}\n"
            f"Expected: data/polyhedra/<class>/<name>/polyhedron.grh"
        )


def run_spanning_tree_count(
    polyhedron_grh_path: Path,
    binary_path: Path,
    edge_sets_path: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Run C++ binary to count spanning trees and optionally filter overlapping unfoldings.

    C++ バイナリを実行して全域木を数え、オプションで重なりを持つ展開図をフィルタ。

    Args:
        polyhedron_grh_path: Path to polyhedron.grh
        binary_path: Path to C++ executable
        edge_sets_path: Optional path to unfoldings_edge_sets.jsonl for Phase 5

    Returns:
        dict: JSON output parsed as dictionary

    Raises:
        RuntimeError: If C++ binary execution fails
        ValueError: If output format is invalid
    """
    # Build command
    # コマンドを構築
    cmd = [str(binary_path), str(polyhedron_grh_path)]
    if edge_sets_path:
        cmd.append(str(edge_sets_path))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"C++ binary failed: {result.stderr}")

    # JSON パース
    try:
        output_json = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON output: {e}\nOutput: {result.stdout}")

    return output_json


def save_result_json(result: Dict[str, Any], output_path: Path) -> None:
    """
    Save spanning tree count result to JSON file.

    全域木数え上げ結果を JSON ファイルに保存。

    Args:
        result: Result dictionary from C++ binary
        output_path: Path to output JSON file
    """
    # Create parent directory if needed
    # 親ディレクトリが存在しない場合は作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with pretty-printing
    # 整形して保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def main():
    """
    Main CLI entry point for Phase 4 + Phase 5.

    Phase 4 + Phase 5 のメイン CLI エントリーポイント。

    Parses command-line arguments, validates inputs, runs C++ binary,
    saves results to output/ directory, and displays summary.

    コマンドライン引数を解析し、入力を検証し、C++ バイナリを実行し、
    output/ ディレクトリに結果を保存し、要約を表示する。
    """
    parser = argparse.ArgumentParser(
        description="Phase 4 + Phase 5: ZDD を用いた全域木の数え上げとフィルタリング"
    )
    parser.add_argument(
        "--grh",
        type=Path,
        required=True,
        help="polyhedron.grh ファイルへのパス"
    )
    parser.add_argument(
        "--edge-sets",
        type=Path,
        help="unfoldings_edge_sets.jsonl へのパス（Phase 5 フィルタリング用）"
    )
    args = parser.parse_args()

    # C++ バイナリの位置
    # Locate C++ binary
    script_dir = Path(__file__).parent
    binary_path = (script_dir.parent.parent /
                   "cpp" / "spanning_tree_zdd" / "build" / "spanning_tree_zdd")

    if not binary_path.exists():
        raise FileNotFoundError(
            f"Binary not found: {binary_path}\n"
            f"Please build the C++ binary first:\n"
            f"  cd cpp/spanning_tree_zdd/build\n"
            f"  cmake .. && make"
        )

    if not args.grh.exists():
        raise FileNotFoundError(f"Input file not found: {args.grh}")

    # edge_sets ファイルの検証（指定されている場合）
    # Validate edge_sets file if specified
    if args.edge_sets and not args.edge_sets.exists():
        raise FileNotFoundError(f"Edge sets file not found: {args.edge_sets}")

    # 多面体情報を取得
    # Extract polyhedron info from path
    poly_class, poly_name = get_polyhedron_info_from_grh(args.grh)
    
    # 出力ディレクトリを設定
    # Set up output directory
    # プロジェクトルート = python/ の親ディレクトリ
    # Project root = parent of python/ directory
    project_root = script_dir.parent.parent
    output_dir = project_root / "output" / "polyhedra" / poly_class / poly_name / "spanning_tree"
    output_file = output_dir / "result.json"

    print("=" * 60)
    if args.edge_sets:
        print(f"Phase 4 + Phase 5: Spanning Tree Enumeration and Filtering")
    else:
        print(f"Phase 4: Spanning Tree Enumeration")
    print(f"Polyhedron: {poly_class}/{poly_name}")
    print("=" * 60)
    print(f"Input (grh): {args.grh}")
    if args.edge_sets:
        print(f"Input (MOPEs): {args.edge_sets}")
    print(f"Output: {output_file}")
    print("=" * 60)

    # C++ バイナリを実行
    # Run C++ binary
    if args.edge_sets:
        print("Running Phase 4: ZDD construction...")
        print("Running Phase 5: Filtering overlapping unfoldings...")
    else:
        print("Running ZDD construction...")
    result = run_spanning_tree_count(args.grh, binary_path, args.edge_sets)

    # 結果を保存
    # Save result to file
    save_result_json(result, output_file)
    print(f"✓ Result saved to: {output_file}")
    print("=" * 60)

    # 結果を表示
    # Display results
    print("Graph Information:")
    print(f"  Vertices: {result['vertices']}")
    print(f"  Edges: {result['edges']}")
    print()

    print("Phase 4 Results:")
    print(f"  Build time: {result['phase4']['build_time_ms']:.2f} ms")
    print(f"  Count time: {result['phase4']['count_time_ms']:.2f} ms")
    print(f"  Spanning tree count: {result['phase4']['spanning_tree_count']}")

    # Phase 5 の結果表示（フィルタが適用された場合）
    # Display Phase 5 results if filtering was applied
    if result['phase5']['filter_applied']:
        print()
        print("Phase 5 Results:")
        print(f"  Number of MOPEs: {result['phase5']['num_mopes']}")
        print(f"  Subset time: {result['phase5']['subset_time_ms']:.2f} ms")
        print(f"  Non-overlapping count: {result['phase5']['non_overlapping_count']}")
        print()
        print("Summary:")
        print(f"  Total spanning trees: {result['phase4']['spanning_tree_count']}")
        print(f"  Non-overlapping unfoldings: {result['phase5']['non_overlapping_count']}")

        # 削減率を計算
        # Calculate reduction rate
        total = int(result['phase4']['spanning_tree_count'])
        non_overlapping = int(result['phase5']['non_overlapping_count'])
        reduction_rate = (1 - non_overlapping / total) * 100
        print(f"  Filtered out: {reduction_rate:.2f}%")

    print("=" * 60)


if __name__ == "__main__":
    main()
