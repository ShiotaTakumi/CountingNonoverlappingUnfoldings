"""
__main__.py

Phase 1: Edge Relabeling モジュールのエントリーポイント

Usage:
    PYTHONPATH=python python -m edge_relabeling --poly <polyhedron_path>
"""

from .cli import main

if __name__ == "__main__":
    main()
