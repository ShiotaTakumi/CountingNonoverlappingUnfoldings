"""
CLI interface for drawing utility (CountingNonoverlappingUnfoldings version).

Provides command-line interface for visualizing JSONL outputs from counting pipeline.
Counting パイプラインの JSONL 出力を可視化するコマンドラインインターフェース。

Usage:
    PYTHONPATH=python python -m drawing --jsonl <path_to_jsonl> [--no-labels]

Example:
    PYTHONPATH=python python -m drawing --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
    PYTHONPATH=python python -m drawing --jsonl data/polyhedra/archimedean/s12L/exact_relabeled.jsonl --no-labels
"""

import argparse
import sys
from pathlib import Path

from drawing.draw_raw import draw_raw_jsonl


def resolve_output_dir(jsonl_path: Path) -> Path:
    """
    Resolves output directory for SVG files based on input JSONL path.
    
    入力 JSONL のパスから SVG 出力ディレクトリを解決する。
    
    Args:
        jsonl_path: Path to input JSONL file
        
    Returns:
        Path: Output directory (e.g., output/polyhedra/<class>/<name>/draw/exact_relabeled/)
        
    Output structure:
        output/polyhedra/<class>/<name>/draw/<jsonl_stem>/
        
    Example:
        Input:  data/polyhedra/johnson/n20/exact_relabeled.jsonl
        Output: output/polyhedra/johnson/n20/draw/exact_relabeled/
        
    Note:
        SVG files are generated output, so they go to output/ not data/.
        SVG ファイルは生成された出力なので、data/ ではなく output/ に配置。
    """
    # Extract polyhedron class and name from input path
    # 入力パスから polyhedron の class と name を抽出
    # Expected: data/polyhedra/<class>/<name>/<file>.jsonl
    parts = jsonl_path.parts
    
    try:
        # Find 'polyhedra' in path
        polyhedra_idx = parts.index('polyhedra')
        poly_class = parts[polyhedra_idx + 1]
        poly_name = parts[polyhedra_idx + 2]
    except (ValueError, IndexError):
        raise ValueError(
            f"Cannot extract class/name from path: {jsonl_path}. "
            f"Expected structure: .../polyhedra/<class>/<name>/<file>.jsonl"
        )
    
    # Get repository root
    # リポジトリルートを取得
    repo_root = Path(__file__).resolve().parent.parent.parent
    
    # Get JSONL filename without extension
    # JSONL ファイル名（拡張子なし）を取得
    jsonl_stem = jsonl_path.stem
    
    # Create output directory: output/polyhedra/<class>/<name>/draw/<jsonl_stem>/
    # 出力ディレクトリを作成: output/polyhedra/<class>/<name>/draw/<jsonl_stem>/
    output_dir = repo_root / "output" / "polyhedra" / poly_class / poly_name / "draw" / jsonl_stem
    
    return output_dir


def create_parser() -> argparse.ArgumentParser:
    """
    Creates and returns the argument parser for the drawing CLI.
    
    描画 CLI 用の引数パーサを作成して返す。
    
    Returns:
        argparse.ArgumentParser: Configured argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="drawing",
        description="Drawing utility for visualizing counting pipeline outputs (JSONL → SVG)",
    )
    
    parser.add_argument(
        "--jsonl",
        type=Path,
        required=True,
        help="Path to JSONL file to visualize (e.g., data/polyhedra/johnson/n20/exact_relabeled.jsonl)"
    )
    
    parser.add_argument(
        "--no-labels",
        action="store_true",
        default=False,
        help="Hide face and edge labels (draw polygons only)"
    )
    
    return parser


def main():
    """
    Main entry point for the drawing CLI.
    
    描画 CLI のメイン入口。
    
    Example usage:
        PYTHONPATH=python python -m drawing --jsonl data/polyhedra/johnson/n20/exact_relabeled.jsonl
        PYTHONPATH=python python -m drawing --jsonl data/polyhedra/archimedean/s12L/exact_relabeled.jsonl --no-labels
    
    Execution model:
        - Reads JSONL records (must have faces with x, y, angle_deg, gon)
        - Outputs SVG files to <parent_dir>/draw/<jsonl_stem>/
        - Example: exact_relabeled.jsonl → draw/exact_relabeled/000000.svg, 000001.svg, ...
    """
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        # Validate input file
        # 入力ファイルを検証
        jsonl_path = args.jsonl.resolve()
        if not jsonl_path.is_file():
            raise FileNotFoundError(
                f"Input JSONL not found: {jsonl_path}\n"
                f"Make sure the file exists."
            )
        
        # Resolve output directory
        # 出力ディレクトリを解決
        output_dir = resolve_output_dir(jsonl_path)
        
        show_labels = not args.no_labels
        
        label_status = "no labels" if args.no_labels else "with labels"
        print(f"Drawing JSONL: {jsonl_path} ({label_status})")
        print(f"Output: {output_dir}/")
        print("")
        
        # Draw
        # 描画
        num_generated = draw_raw_jsonl(jsonl_path, output_dir, show_labels=show_labels)
        print(f"Done. Generated {num_generated} SVG files.")
        
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
