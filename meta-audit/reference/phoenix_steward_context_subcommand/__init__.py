"""Context command modules for the Phoenix Steward system.

This package provides the implementation for the `phoenix steward context` command,
which generates a comprehensive context overview for AI agents.

Modules:
- command: Click command interface for the context command
- generators: Context generation logic
- formatters: Output formatting functions
- collectors: Data collection utilities
- displays: Display functions for terminal output

NOTE: Generator functions are NOT re-exported to avoid eager loading
of heavy dependencies like steward.db. Import directly from .generators
if needed for testing.
"""

from .command import context


__all__ = [
    "context",
]
