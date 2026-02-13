"""
Drawing Utility - Module Entry Point

Entry point for executing the drawing utility as a Python module.

描画ユーティリティモジュールのエントリーポイント。

Usage:
    PYTHONPATH=python python -m drawing --jsonl <jsonl_path> [--no-labels]

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from drawing.cli import main

if __name__ == "__main__":
    main()
