"""
decompose_runner.py

Python から C++ バイナリ（edge_relabeling）を subprocess で実行し、
パス幅最適化された辺順序を取得する。
"""

import subprocess
from pathlib import Path
from typing import Tuple


def run_decompose(input_grh_path: Path, output_grh_path: Path) -> None:
    """
    decompose を実行してパス幅最適化された辺順序を取得する
    
    Args:
        input_grh_path: 入力 .grh ファイルパス（decompose 入力形式）
        output_grh_path: 出力 .grh ファイルパス（tdzdd 互換形式）
    
    Raises:
        FileNotFoundError: C++ バイナリが見つからない場合
        RuntimeError: decompose の実行に失敗した場合
    """
    # C++ バイナリのパスを解決
    binary_path = Path(__file__).parent.parent.parent / "cpp" / "edge_relabeling" / "build" / "edge_relabeling"
    
    if not binary_path.exists():
        raise FileNotFoundError(
            f"C++ バイナリが見つかりません: {binary_path}\n"
            f"以下のコマンドでビルドしてください:\n"
            f"cd cpp/edge_relabeling && mkdir -p build && cd build && cmake .. && make"
        )
    
    # 入力ファイルの存在確認
    if not input_grh_path.exists():
        raise FileNotFoundError(f"入力ファイルが見つかりません: {input_grh_path}")
    
    # 出力ディレクトリの作成
    output_grh_path.parent.mkdir(parents=True, exist_ok=True)
    
    # decompose を実行
    try:
        with open(input_grh_path, 'r') as infile, \
             open(output_grh_path, 'w') as outfile:
            
            result = subprocess.run(
                [str(binary_path)],
                stdin=infile,
                stdout=outfile,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"decompose の実行に失敗しました (exit code: {e.returncode})\n"
            f"stderr: {e.stderr}"
        )
    except Exception as e:
        raise RuntimeError(f"decompose の実行中に予期しないエラーが発生しました: {e}")


def run_decompose_with_stats(input_grh_path: Path, output_grh_path: Path) -> Tuple[int, int]:
    """
    decompose を実行し、統計情報を返す
    
    Args:
        input_grh_path: 入力 .grh ファイルパス
        output_grh_path: 出力 .grh ファイルパス
    
    Returns:
        (入力辺数, 出力辺数) のタプル
    """
    # decompose を実行
    run_decompose(input_grh_path, output_grh_path)
    
    # 入力辺数をカウント
    with open(input_grh_path, 'r') as f:
        input_lines = [line.strip() for line in f if line.strip() and not line.startswith('p')]
        input_edge_count = len([line for line in input_lines if line.startswith('e')])
    
    # 出力辺数をカウント（ヘッダー行を除く）
    with open(output_grh_path, 'r') as f:
        output_lines = [line.strip() for line in f if line.strip()]
        output_edge_count = len([line for line in output_lines if line.startswith('e')])
    
    return input_edge_count, output_edge_count


if __name__ == "__main__":
    # テスト実行
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python -m edge_relabeling.decompose_runner <input.grh> <output.grh>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    
    print(f"Running decompose...")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}")
    
    try:
        input_edges, output_edges = run_decompose_with_stats(input_path, output_path)
        print(f"\n✓ Success!")
        print(f"  Input edges:  {input_edges}")
        print(f"  Output edges: {output_edges}")
        
        if input_edges != output_edges:
            print(f"\n⚠ Warning: 辺数が一致しません")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
