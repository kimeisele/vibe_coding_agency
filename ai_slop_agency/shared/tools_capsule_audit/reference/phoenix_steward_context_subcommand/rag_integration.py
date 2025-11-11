"""RAG integration for steward context - keyword extraction and knowledge lookup.

This module bridges Steward (context/status) with RAG (knowledge base) to provide
intelligent, context-aware knowledge snippets.
"""

import logging
import os
from typing import Any, Dict, List, Optional


logger = logging.getLogger(__name__)

_ENABLE_RAG = os.environ.get("PHOENIX_ENABLE_KNOWLEDGE", "").lower() in {
    "1",
    "true",
    "yes",
}


def extract_keywords_from_context(
    git_reality: Optional[Dict[str, Any]] = None,
    active_wu: Optional[Dict[str, Any]] = None,
    system_health: Optional[Dict[str, Any]] = None,
    priority_blockers: Optional[Dict[str, List[str]]] = None,
) -> List[str]:
    """
    Extract relevant keywords from current context for RAG search.

    Analyzes:
    - Active work unit title/id
    - Modified files (to detect area of focus)
    - Detected system health issues
    - Priority blockers/issues

    Args:
        git_reality: Git status information
        active_wu: Currently active work unit
        system_health: System health metrics
        priority_blockers: Detected blockers and issues

    Returns:
        List of keywords sorted by relevance
    """
    keyword_scores = {}  # Track relevance score for deduplication

    # === WU-based keywords (highest priority) ===
    if active_wu:
        # WU title contains primary context
        if title := active_wu.get("title"):
            # Extract meaningful words from title
            words = _extract_meaningful_words(title)
            for word in words:
                keyword_scores[word] = keyword_scores.get(word, 0) + 3

        # WU ID itself is relevant
        if wu_id := active_wu.get("id"):
            keyword_scores[wu_id] = keyword_scores.get(wu_id, 0) + 2

        # WU type/category
        if wu_type := active_wu.get("type"):
            keyword_scores[wu_type] = keyword_scores.get(wu_type, 0) + 2

    # === Git-based keywords (medium priority) ===
    if git_reality:
        # Changed files indicate area of work
        if changed_files := git_reality.get("changed_files"):
            for file_path in changed_files[:5]:  # Top 5 files
                # Extract module/feature from file path
                parts = file_path.split("/")
                for part in parts:
                    if part and not part.startswith("."):
                        word = _normalize_word(part.split(".")[0])
                        if len(word) > 2:  # Skip single letters
                            keyword_scores[word] = keyword_scores.get(word, 0) + 1.5

        # Branch name is often descriptive
        if branch := git_reality.get("current_branch"):
            words = _extract_meaningful_words(branch)
            for word in words:
                keyword_scores[word] = keyword_scores.get(word, 0) + 1

    # === Health/blocker-based keywords (medium priority) ===
    if system_health:
        # Known issues
        if issues := system_health.get("known_issues"):
            for issue in issues[:3]:
                words = _extract_meaningful_words(issue)
                for word in words:
                    keyword_scores[word] = keyword_scores.get(word, 0) + 1.5

    if priority_blockers:
        # Blocker messages contain important context
        for blocker_list in priority_blockers.values():
            for blocker in blocker_list[:3]:  # Top 3 blockers per category
                words = _extract_meaningful_words(blocker)
                for word in words:
                    keyword_scores[word] = keyword_scores.get(word, 0) + 1

    # === Sort by relevance and return ===
    # Remove short words and duplicates, sort by score
    relevant_keywords = [
        word
        for word, score in sorted(
            keyword_scores.items(), key=lambda x: x[1], reverse=True
        )
        if len(word) > 2  # Exclude very short words
    ]

    # Return top 8 keywords for RAG search
    return relevant_keywords[:8]


def _extract_meaningful_words(text: str) -> List[str]:
    """Extract meaningful words from text.

    Removes common words, punctuation, etc.
    """
    import re

    # Common words to skip
    stop_words = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "is",
        "was",
        "are",
        "been",
        "be",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "must",
        "can",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "up",
        "about",
        "out",
        "if",
        "as",
        "it",
        "this",
        "that",
    }

    # Split by common delimiters
    text = text.lower()
    # Replace common delimiters with spaces
    text = re.sub(r"[-_/.]", " ", text)
    # Remove non-alphanumeric
    text = re.sub(r"[^a-z0-9\s]", "", text)

    words = [w for w in text.split() if w and w not in stop_words and len(w) > 2]
    return list(dict.fromkeys(words))  # Deduplicate while preserving order


def _normalize_word(word: str) -> str:
    """Normalize a word for comparison."""
    return word.lower().strip()


def query_rag_for_context(
    keywords: List[str],
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Query RAG knowledge base for context-relevant snippets.

    Args:
        keywords: List of keywords to search for
        limit: Maximum number of results to return

    Returns:
        List of RAG results with structure:
        [
            {
                "section": str (e.g., "2.3 Architecture"),
                "text": str (the actual content),
                "score": float (0-1, relevance),
                "file_path": str (source file),
                "doc_id": str (document id)
            },
            ...
        ]

    Returns empty list if RAG unavailable (graceful degradation).
    """
    if not _ENABLE_RAG:
        logger.debug(
            "RAG integration disabled (set PHOENIX_ENABLE_KNOWLEDGE=1 to enable)"
        )
        return []

    if not keywords:
        logger.debug("No keywords provided for RAG query")
        return []

    try:
        from phoenix_system.knowledge.query import KnowledgeQuery

        kb = KnowledgeQuery()

        # Build search query from keywords
        # Prioritize first few keywords, limit query length
        search_query = " ".join(keywords[:5])

        # Search RAG
        results = kb.search(query=search_query, limit=limit * 2, threshold=0.0)

        # Filter and format results (top N by score)
        formatted_results = []
        for result in results[:limit]:
            formatted_results.append(
                {
                    "section": result.get("section", ""),
                    "text": result.get("text", ""),
                    "score": result.get("score", 0.0),
                    "file_path": result.get("file_path", ""),
                    "doc_id": result.get("doc_id", ""),
                }
            )

        if formatted_results:
            logger.debug(
                f"RAG search found {len(formatted_results)} relevant snippets for keywords: {keywords[:3]}"
            )

        return formatted_results

    except Exception as e:
        logger.warning(
            f"RAG knowledge base unavailable: {e}. "
            f"Continuing without knowledge context. "
            f"(Run 'phoenix knowledge index' to enable)"
        )
        return []


def query_rag_for_action_recommendations(
    keywords: List[str],
    context_type: str = "general",
    limit: int = 3,
) -> List[Dict[str, Any]]:
    """
    Query RAG knowledge base specifically for action recommendations.

    Searches for documents that contain step-by-step procedures, protocols,
    or guides that suggest next actions based on context.

    Args:
        keywords: Keywords extracted from current context
        context_type: Type of context ("general", "error", "blockers", "status")
        limit: Maximum recommendations to return

    Returns:
        List of action recommendations with structure:
        [
            {
                "action": str (what to do),
                "command": str (optional CLI command),
                "reason": str (why this is recommended),
                "section": str (source section),
                "confidence": float (0-1)
            },
            ...
        ]

    Returns empty list if RAG unavailable (graceful degradation).
    """
    if not _ENABLE_RAG:
        logger.debug(
            "RAG action recommendations disabled "
            "(set PHOENIX_ENABLE_KNOWLEDGE=1 to enable)"
        )
        return []

    if not keywords:
        logger.debug("No keywords provided for action recommendation query")
        return []

    try:
        from phoenix_system.knowledge.query import KnowledgeQuery

        kb = KnowledgeQuery()

        # Build action-specific search queries
        # Look for PROCEDURE, GUIDE, PROTOCOL, WORKFLOW documents
        action_keywords = keywords + [
            "procedure",
            "guide",
            "protocol",
            "workflow",
            "next step",
            "recommendation",
        ]

        # Search with action-focused keywords
        search_query = " ".join(action_keywords[:6])

        # Search RAG - get more results and filter for actions
        raw_results = kb.search(query=search_query, limit=limit * 3, threshold=0.0)

        # Convert to action recommendations
        recommendations = []
        for result in raw_results[:limit]:
            section = result.get("section", "")
            text = result.get("text", "")
            score = result.get("score", 0.0)
            file_path = result.get("file_path", "")

            # Extract action from text (first sentence usually)
            action_text = text.split(".")[0] if "." in text else text[:100]

            # Try to infer CLI command if applicable
            command = _extract_cli_command_from_recommendation(text, file_path)

            recommendations.append(
                {
                    "action": action_text,
                    "command": command,
                    "reason": _generate_reason_for_recommendation(
                        section, context_type, keywords
                    ),
                    "section": section,
                    "confidence": score,
                    "source": file_path,
                }
            )

        if recommendations:
            logger.debug(
                f"Found {len(recommendations)} action recommendations for keywords: {keywords[:3]}"
            )

        return recommendations

    except Exception as e:
        logger.warning(
            f"Action recommendation query failed: {e}. "
            f"Continuing without recommendations."
        )
        return []


def _extract_cli_command_from_recommendation(
    text: str, file_path: str
) -> Optional[str]:
    """
    Try to extract a CLI command from recommendation text or file path.

    Examples:
    - "Run: phoenix knowledge index" → "phoenix knowledge index"
    - "Execute: make test" → "make test"
    """
    import re

    # Look for patterns like "phoenix ...", "make ...", etc.
    patterns = [
        r"(?:run|execute|command|use):\s+([^\n.]+)",  # "Run: phoenix command"
        r"(?:phoenix|make)\s+[a-z\-]+(?:\s+[a-z\-]+)?",  # Direct commands
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            cmd = match.group(0).strip() if match.groups() else match.group(0).strip()
            if any(cmd.startswith(prefix) for prefix in ["phoenix", "make", "git"]):
                return cmd

    return None


def _generate_reason_for_recommendation(
    section: str, context_type: str, keywords: List[str]
) -> str:
    """
    Generate a natural language reason for why this recommendation is being made.
    """
    if not keywords:
        return f"Recommended action from {section}"

    keyword_str = ", ".join(keywords[:2])
    return f"Relevant to {keyword_str} (source: {section})"


def get_context_aware_knowledge(
    git_reality: Optional[Dict[str, Any]] = None,
    active_wu: Optional[Dict[str, Any]] = None,
    system_health: Optional[Dict[str, Any]] = None,
    priority_blockers: Optional[Dict[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Main entry point: extract keywords and query RAG for relevant knowledge.

    This is the orchestrator function that combines keyword extraction with
    RAG querying to provide context-aware knowledge snippets.

    Args:
        git_reality: Git status
        active_wu: Active work unit
        system_health: System health
        priority_blockers: Detected blockers

    Returns:
        List of relevant knowledge snippets (max 3)
    """
    # Step 1: Extract keywords from context
    keywords = extract_keywords_from_context(
        git_reality=git_reality,
        active_wu=active_wu,
        system_health=system_health,
        priority_blockers=priority_blockers,
    )

    if not keywords:
        logger.debug("No keywords extracted from context")
        return []

    logger.debug(f"Extracted keywords for RAG: {keywords}")

    # Step 2: Query RAG with keywords
    results = query_rag_for_context(keywords, limit=3)

    return results


def get_action_recommendations(
    git_reality: Optional[Dict[str, Any]] = None,
    active_wu: Optional[Dict[str, Any]] = None,
    system_health: Optional[Dict[str, Any]] = None,
    priority_blockers: Optional[Dict[str, List[str]]] = None,
) -> List[Dict[str, Any]]:
    """
    Main entry point for action recommendations (WU-INT-002A).

    Extracts keywords from context and queries RAG specifically for
    actionable recommendations (procedures, guides, next steps).

    Args:
        git_reality: Git status
        active_wu: Active work unit
        system_health: System health
        priority_blockers: Detected blockers

    Returns:
        List of action recommendations (max 3) with CLI commands where applicable
    """
    # Step 1: Extract keywords from context
    keywords = extract_keywords_from_context(
        git_reality=git_reality,
        active_wu=active_wu,
        system_health=system_health,
        priority_blockers=priority_blockers,
    )

    if not keywords:
        logger.debug("No keywords extracted from context")
        return []

    # Determine context type based on system state
    context_type = "general"
    if system_health and system_health.get("known_issues"):
        context_type = "error"
    elif priority_blockers and any(priority_blockers.values()):
        context_type = "blockers"

    logger.debug(
        f"Extracted keywords for action recommendations: {keywords}, context: {context_type}"
    )

    # Step 2: Query RAG specifically for actions
    recommendations = query_rag_for_action_recommendations(
        keywords, context_type=context_type, limit=3
    )

    return recommendations
