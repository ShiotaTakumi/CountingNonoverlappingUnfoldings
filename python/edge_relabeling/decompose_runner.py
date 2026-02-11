"""
Decompose Runner - C++ Binary Invocation

Handles:
- Subprocess invocation of cpp/edge_relabeling/build/edge_relabeling
- Pathwidth optimization via lib/decompose
- Standard input/output stream management
- Does NOT modify the decompose algorithm itself

decompose 実行モジュール:
- cpp/edge_relabeling/build/edge_relabeling のサブプロセス呼び出し
- lib/decompose によるパス幅最適化
- 標準入出力ストリームの管理
- decompose アルゴリズム自体は変更しない

Responsibility in Phase 1:
- Invokes the C++ binary that wraps lib/decompose
- Passes .grh file via stdin, receives optimized .grh via stdout
- Verifies edge count consistency before/after optimization

Phase 1 における責務:
- lib/decompose をラップする C++ バイナリを呼び出し
- .grh ファイルを stdin 経由で渡し、最適化された .grh を stdout から受け取り
- 最適化前後の辺数の一貫性を検証
"""

import subprocess
from pathlib import Path
from typing import Tuple


def run_decompose(input_grh_path: Path, output_grh_path: Path) -> None:
    """
    Run decompose to obtain pathwidth-optimized edge ordering.
    
    decompose を実行してパス幅最適化された辺順序を取得。
    
    Args:
        input_grh_path (Path): Input .grh file path (decompose input format)
        output_grh_path (Path): Output .grh file path (decompose output format)
    
    Raises:
        FileNotFoundError: If C++ binary not found
        RuntimeError: If decompose execution fails
    
    Note:
        The C++ binary must be built first:
        cd cpp/edge_relabeling && mkdir -p build && cd build && cmake .. && make
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
    Run decompose and return statistics.
    
    decompose を実行し、統計情報を返す。
    
    Args:
        input_grh_path (Path): Input .grh file path
        output_grh_path (Path): Output .grh file path
    
    Returns:
        tuple: (input_edge_count, output_edge_count)
    
    Note:
        Edge counts should match. If they don't, it indicates an error.
        辺数は一致すべき。不一致の場合はエラーを示す。
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
