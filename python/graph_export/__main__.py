"""
Phase 3: Graph Data Conversion - Module Entry Point

Entry point for executing Phase 3 as a Python module.

Phase 3 モジュールのエントリーポイント。

Usage:
    PYTHONPATH=python python -m graph_export --poly <polyhedron_relabeled_path>

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from .cli import main

if __name__ == "__main__":
    main()
