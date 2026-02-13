"""
run_all — Full Pipeline Execution for Counting Non-overlapping Unfoldings

Executes all phases of the counting pipeline in a single command:
    Phase 1 (edge_relabeling)
    → Phase 2 (unfolding_expansion)
    → Phase 3 (graph_export)
    → Phase 4 & 5 (spanning_tree_zdd with filtering)

Usage:
    PYTHONPATH=python python -m run_all --poly data/polyhedra/<class>/<name>

Example:
    PYTHONPATH=python python -m run_all --poly data/polyhedra/johnson/n20
"""

__version__ = "1.0.0"
