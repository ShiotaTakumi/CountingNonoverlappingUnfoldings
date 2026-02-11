"""
Phase 1: Edge Relabeling - Integrated CLI

Handles:
- Unified execution of all Phase 1 steps
- Path resolution for polyhedron data
- Output directory management for data/ and output/
- Progress reporting

Phase 1 統合実行 CLI:
- Phase 1 の全ステップの統一実行
- 多面体データのパス解決
- data/ と output/ の出力ディレクトリ管理
- 進捗報告

Responsibility in Phase 1:
- User-facing CLI for Phase 1 complete execution
- Orchestrates graph_builder, grh_generator, decompose_runner, edge_mapper, and relabeler
- Outputs polyhedron_relabeled.json and edge_mapping.json for Phase 2

Phase 1 における責務:
- Phase 1 完全実行のためのユーザー向け CLI
- graph_builder, grh_generator, decompose_runner, edge_mapper, relabeler を統合実行
- Phase 2 のために polyhedron_relabeled.json と edge_mapping.json を出力

Usage:
    PYTHONPATH=python python -m edge_relabeling --poly <polyhedron_path>
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional

from .graph_builder import build_vertex_edge_graph
from .grh_generator import generate_grh
from .decompose_runner import run_decompose_with_stats
from .edge_mapper import create_edge_mapping, verify_mapping, save_edge_mapping
from .relabeler import load_polyhedron, relabel_polyhedron, verify_relabeling, save_polyhedron


def get_polyhedron_info(polyhedron_path: Path) -> tuple[str, str]:
    """
    Extract class and name from polyhedron.json.
    
    polyhedron.json から class と name を取得。
    
    Args:
        polyhedron_path (Path): Path to polyhedron.json
    
    Returns:
        tuple: (class, name) such as ('johnson', 'n20')
    """
    with open(polyhedron_path, 'r') as f:
        data = json.load(f)
    
    poly_class = data["polyhedron"]["class"]
    poly_name = data["polyhedron"]["name"]
    
    return poly_class, poly_name


def run_phase1(
    polyhedron_path: Path,
    output_base: Optional[Path] = None,
    data_base: Optional[Path] = None
) -> None:
    """
    Execute all Phase 1 steps in sequence.
    
    Phase 1 の全ステップを順次実行。
    
    Args:
        polyhedron_path (Path): Path to input polyhedron.json
        output_base (Path, optional): Base directory for output/ (default: current directory)
        data_base (Path, optional): Base directory for data/ (default: current directory)
    
    Outputs:
        - output/polyhedra/<class>/<name>/edge_relabeling/input.grh
        - output/polyhedra/<class>/<name>/edge_relabeling/output.grh
        - data/polyhedra/<class>/<name>/edge_mapping.json
        - data/polyhedra/<class>/<name>/polyhedron_relabeled.json
    
    Steps:
        1. Generate .grh file (graph_builder + grh_generator)
        2. Run decompose for pathwidth optimization
        3. Extract edge mapping (edge_mapper)
        4. Relabel polyhedron edges (relabeler)
    """
    # デフォルト設定
    if output_base is None:
        output_base = Path.cwd()
    if data_base is None:
        data_base = Path.cwd()
    
    # 多面体情報を取得
    poly_class, poly_name = get_polyhedron_info(polyhedron_path)
    
    print("=" * 60)
    print(f"Phase 1: Edge Relabeling")
    print(f"  Polyhedron: {poly_class}/{poly_name}")
    print(f"  Input:      {polyhedron_path}")
    print("=" * 60)
    print()
    
    # 出力ディレクトリの設定
    output_dir = output_base / "output" / "polyhedra" / poly_class / poly_name / "edge_relabeling"
    data_dir = data_base / "data" / "polyhedra" / poly_class / poly_name
    
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # ファイルパスの設定
    input_grh = output_dir / "input.grh"
    output_grh = output_dir / "output.grh"
    edge_mapping_json = data_dir / "edge_mapping.json"
    polyhedron_relabeled_json = data_dir / "polyhedron_relabeled.json"
    
    # Step 1: .grh ファイル生成
    print("[Step 1/4] Generating .grh file...")
    
    with open(polyhedron_path, 'r') as f:
        polyhedron = json.load(f)
    
    edge_to_vertices = build_vertex_edge_graph(polyhedron)
    generate_grh(edge_to_vertices, input_grh)
    
    num_vertices = max(max(v) for v in edge_to_vertices.values()) + 1
    num_edges = len(edge_to_vertices)
    
    print(f"  Generated: {input_grh}")
    print(f"    Edges:    {num_edges}")
    print(f"    Vertices: {num_vertices}")
    print()
    
    # Step 2: decompose 実行
    print("[Step 2/4] Running decompose (pathwidth optimization)...")
    
    input_edges, output_edges = run_decompose_with_stats(input_grh, output_grh)
    
    print(f"  Input:  {input_grh}")
    print(f"  Output: {output_grh}")
    print(f"    Input edges:  {input_edges}")
    print(f"    Output edges: {output_edges}")
    
    if input_edges != output_edges:
        print(f"  ERROR: Edge count mismatch!")
        sys.exit(1)
    
    print()
    
    # Step 3: 辺ラベル対応表の抽出
    print("[Step 3/4] Extracting edge mapping...")
    
    mapping = create_edge_mapping(input_grh, output_grh)
    verify_mapping(mapping)
    save_edge_mapping(mapping, edge_mapping_json)
    
    print(f"  Created: {edge_mapping_json}")
    print(f"    Total edges: {len(mapping)}")
    print(f"    Mapping (first 5):")
    for old_id in sorted(mapping.keys())[:5]:
        new_id = mapping[old_id]
        print(f"      {old_id} → {new_id}")
    print()
    
    # Step 4: 辺ラベル貼り替え
    print("[Step 4/4] Relabeling polyhedron edges...")
    
    relabeled = relabel_polyhedron(polyhedron, mapping)
    verify_relabeling(polyhedron, relabeled, mapping)
    save_polyhedron(relabeled, polyhedron_relabeled_json)
    
    print(f"  Created: {polyhedron_relabeled_json}")
    print(f"    Faces: {len(relabeled['faces'])}")
    print()
    
    # 完了メッセージ
    print("=" * 60)
    print("Phase 1 Complete!")
    print()
    print("Output files:")
    print(f"  - {input_grh}")
    print(f"  - {output_grh}")
    print(f"  - {edge_mapping_json}")
    print(f"  - {polyhedron_relabeled_json}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 1: Edge Relabeling - 多面体の辺ラベルをパス幅最適化された順序に貼り直す"
    )
    
    parser.add_argument(
        "--poly",
        type=str,
        required=True,
        help="入力 polyhedron.json のパス"
    )
    
    parser.add_argument(
        "--output-base",
        type=str,
        default=None,
        help="出力ベースディレクトリ（デフォルト: カレントディレクトリ）"
    )
    
    parser.add_argument(
        "--data-base",
        type=str,
        default=None,
        help="データベースディレクトリ（デフォルト: カレントディレクトリ）"
    )
    
    args = parser.parse_args()
    
    polyhedron_path = Path(args.poly)
    
    if not polyhedron_path.exists():
        print(f"Error: File not found: {polyhedron_path}")
        sys.exit(1)
    
    output_base = Path(args.output_base) if args.output_base else None
    data_base = Path(args.data_base) if args.data_base else None
    
    try:
        run_phase1(polyhedron_path, output_base, data_base)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
