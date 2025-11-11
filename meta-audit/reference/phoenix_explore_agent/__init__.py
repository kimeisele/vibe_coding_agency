"""ExploreAgent - autonomous codebase exploration.

This module provides the ExploreAgent for iterative codebase exploration
using a plan-execute-synthesize loop with temporary RAG.
"""

from .agent import MAX_FINDING_SIZE, MAX_GOAL_LENGTH, ExploreAgent
from .embeddings import Vector, _TempRAGStore


__all__ = [
    "ExploreAgent",
    "Vector",
    "_TempRAGStore",
    "MAX_GOAL_LENGTH",
    "MAX_FINDING_SIZE",
]
