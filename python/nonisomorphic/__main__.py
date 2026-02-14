"""
Spanning Tree Pipeline - Module Entry Point

Entry point for executing the pipeline as a Python module.

全域木パイプラインのモジュールエントリーポイント。

Usage:
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir>
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir> --filter
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir> --noniso
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir> --filter --noniso

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from .cli import main

if __name__ == "__main__":
    main()
