"""
Phase 6: Nonisomorphic Counting - Integrated CLI

Handles:
- Unified execution of automorphism computation + C++ Phase 4+6
- Path resolution for polyhedron data
- Output directory management
- Progress reporting

Phase 6 統合実行 CLI:
- 自己同型計算 + C++ Phase 4+6 の統一実行
- 多面体データのパス解決
- 出力ディレクトリ管理
- 進捗報告

Responsibility in Phase 6:
- User-facing CLI for Phase 6 complete execution
- Orchestrates compute_automorphisms.py and C++ spanning_tree_zdd
- Outputs result.json with phase4 and phase6 results

Phase 6 における責務:
- Phase 6 完全実行のためのユーザー向け CLI
- compute_automorphisms.py と C++ spanning_tree_zdd を統合実行
- phase4 と phase6 の結果を含む result.json を出力

Usage:
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir>
"""

import argparse
import sys
import json
import subprocess
from pathlib import Path
from typing import Optional

from .compute_automorphisms import (
    load_grh,
    build_graph,
    compute_all_automorphisms,
    vertex_perm_to_edge_perm
)


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


def run_phase6(
    polyhedron_dir: Path,
    output_base: Optional[Path] = None
) -> None:
    """
    Execute Phase 6: automorphism computation + C++ Phase 4+6.
    
    Phase 6 を実行: 自己同型計算 + C++ Phase 4+6。
    
    Args:
        polyhedron_dir (Path): Path to polyhedron directory (e.g. data/polyhedra/johnson/n20)
        output_base (Path, optional): Base directory for output/ (default: current directory)
    
    Outputs:
        - <polyhedron_dir>/automorphisms.json
        - output/polyhedra/<class>/<name>/spanning_tree/result.json
    
    Steps:
        1. Compute automorphisms from polyhedron.grh
        2. Run C++ spanning_tree_zdd with --automorphisms
        3. Parse JSON output and save to result.json
    """
    # デフォルト設定
    if output_base is None:
        output_base = Path.cwd()
    
    # 多面体情報を取得
    poly_class, poly_name = get_polyhedron_info(polyhedron_dir)
    
    print("=" * 60)
    print(f"Phase 6: Nonisomorphic Counting (via Burnside's Lemma)")
    print(f"  Polyhedron: {poly_class}/{poly_name}")
    print(f"  Input:      {polyhedron_dir}")
    print("=" * 60)
    print()
    
    # ファイルパスの設定
    grh_file = polyhedron_dir / "polyhedron.grh"
    automorphisms_file = polyhedron_dir / "automorphisms.json"
    output_dir = output_base / "output" / "polyhedra" / poly_class / poly_name / "spanning_tree"
    result_file = output_dir / "result.json"
    
    if not grh_file.exists():
        print(f"Error: File not found: {grh_file}")
        sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: 自己同型計算
    print("[Step 1/2] Computing automorphisms...")
    
    edges = load_grh(grh_file)
    G = build_graph(edges)
    
    num_vertices = G.number_of_nodes()
    num_edges = G.number_of_edges()
    
    print(f"  Graph: {num_vertices} vertices, {num_edges} edges")
    
    vertex_automorphisms = compute_all_automorphisms(G)
    group_order = len(vertex_automorphisms)
    
    print(f"  Automorphism group order: {group_order}")
    
    # 辺置換に変換
    edge_permutations = []
    for vperm in vertex_automorphisms:
        eperm = vertex_perm_to_edge_perm(vperm, edges)
        edge_permutations.append(eperm)
    
    # 恒等置換の検証
    identity_found = False
    for eperm in edge_permutations:
        if eperm == list(range(len(edges))):
            identity_found = True
            break
    if not identity_found:
        print("  Warning: Identity permutation not found in automorphisms")
    
    # JSON 出力
    automorphisms_data = {
        "num_vertices": num_vertices,
        "num_edges": num_edges,
        "group_order": group_order,
        "edge_permutations": edge_permutations
    }
    
    with open(automorphisms_file, 'w') as f:
        json.dump(automorphisms_data, f)
    
    print(f"  Saved: {automorphisms_file}")
    print()
    
    # Step 2: C++ spanning_tree_zdd 実行
    print("[Step 2/2] Running C++ spanning_tree_zdd (Phase 4+6)...")
    
    # C++ バイナリのパスを解決
    cpp_binary = Path(__file__).parent.parent.parent / "cpp" / "spanning_tree_zdd" / "build" / "spanning_tree_zdd"
    
    if not cpp_binary.exists():
        print(f"Error: C++ binary not found: {cpp_binary}")
        print("Please build it first:")
        print("  cd cpp/spanning_tree_zdd && mkdir -p build && cd build && cmake .. && make")
        sys.exit(1)
    
    # C++ 実行
    try:
        result = subprocess.run(
            [
                str(cpp_binary),
                str(grh_file),
                "--automorphisms",
                str(automorphisms_file)
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # stderr は進捗情報なので表示
        if result.stderr:
            print(result.stderr, end='')
        
        # stdout は JSON
        json_output = result.stdout
        
    except subprocess.CalledProcessError as e:
        print(f"Error: C++ binary failed (exit code {e.returncode})")
        print("stderr:", e.stderr)
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
    
    # 結果サマリー
    print("=" * 60)
    print("Phase 6 Complete!")
    print()
    print("Results:")
    print(f"  Labeled spanning trees:      {result_data['phase4']['spanning_tree_count']}")
    if 'phase6' in result_data and 'nonisomorphic_count' in result_data['phase6']:
        print(f"  Nonisomorphic spanning trees: {result_data['phase6']['nonisomorphic_count']}")
        print(f"  Group order |Aut(Γ)|:        {result_data['phase6']['group_order']}")
    print()
    print(f"Output: {result_file}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 6: Nonisomorphic Counting - Burnside の補題による非同型展開図の数え上げ"
    )
    
    parser.add_argument(
        "--poly",
        type=str,
        required=True,
        help="多面体ディレクトリへのパス（例: data/polyhedra/johnson/n20）"
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
    
    output_base = Path(args.output_base) if args.output_base else None
    
    try:
        run_phase6(polyhedron_dir, output_base)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
