"""
Base components for analyzers and collectors.
"""

from typing import Protocol, Dict, Any

class Collector(Protocol):
    """
    A protocol for data collectors.
    """
    def collect(self, path: str) -> Dict[str, Any]:
        """
        Collects data from the given path.
        """
        ...
