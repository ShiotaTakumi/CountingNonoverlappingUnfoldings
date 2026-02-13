"""
Phase 2: Unfolding Expansion - Module Entry Point

Entry point for executing Phase 2 as a Python module.

Phase 2 モジュールのエントリーポイント。

Usage:
    PYTHONPATH=python python -m unfolding_expansion --exact <exact_jsonl_path>

Responsibility:
    Delegates to cli.main() for argument parsing and execution.
    引数解析と実行のために cli.main() に委譲。
"""

from .cli import main

if __name__ == "__main__":
    main()
