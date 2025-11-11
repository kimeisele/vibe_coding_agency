from typing import List

def get_research_queries(query: str) -> List[str]:
    """Generates a standard list of research queries for a given topic."""
    return [
        f"best practices {query} 2024",
        f"{query} common mistakes",
        f"{query} tools",
        f"{query} case studies",
        f"how to measure {query}"
    ]
