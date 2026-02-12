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
        Path: Output directory (e.g., data/polyhedra/<class>/<name>/draw/exact_relabeled/)
        
    Output structure:
        <polyhedron_dir>/draw/<jsonl_stem>/
        
    Example:
        Input:  data/polyhedra/johnson/n20/exact_relabeled.jsonl
        Output: data/polyhedra/johnson/n20/draw/exact_relabeled/
    """
    # Get the parent directory (polyhedron directory)
    poly_dir = jsonl_path.parent
    
    # Get JSONL filename without extension
    jsonl_stem = jsonl_path.stem
    
    # Create output directory: <poly_dir>/draw/<jsonl_stem>/
    output_dir = poly_dir / "draw" / jsonl_stem
    
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
