"""
Entry point for python -m spanning_tree_zdd

Allows running the module as a script:
    PYTHONPATH=python python -m spanning_tree_zdd --grh <path>

python -m spanning_tree_zdd のエントリーポイント。

モジュールをスクリプトとして実行可能にする:
    PYTHONPATH=python python -m spanning_tree_zdd --grh <パス>
"""

from .cli import main

if __name__ == "__main__":
    main()
