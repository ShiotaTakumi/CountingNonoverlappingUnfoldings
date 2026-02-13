"""
Phase 6: Nonisomorphic Counting - Module Entry Point

Entry point for executing Phase 6 as a Python module.

Phase 6 モジュールのエントリーポイント。

Usage:
    PYTHONPATH=python python -m nonisomorphic --poly <polyhedron_dir>

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from .cli import main

if __name__ == "__main__":
    main()
