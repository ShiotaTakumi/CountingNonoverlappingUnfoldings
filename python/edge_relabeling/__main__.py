"""
Phase 1: Edge Relabeling - Module Entry Point

Entry point for executing Phase 1 as a Python module.

Phase 1 モジュールのエントリーポイント。

Usage:
    PYTHONPATH=python python -m edge_relabeling --poly <polyhedron_path>

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from .cli import main

if __name__ == "__main__":
    main()
