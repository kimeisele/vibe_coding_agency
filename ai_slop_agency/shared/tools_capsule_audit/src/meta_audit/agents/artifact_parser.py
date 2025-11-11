"""
Artifact Parser: Extracts structured artifacts from LLM analysis responses.

Converts free-form LLM text into structured CodePatch and GeneratedTest objects
using Pydantic validation and optional LLM-based schema forcing via ArtifactTextProvider.
"""

import logging
from pathlib import Path
from typing import List, Optional, Type

from pydantic import BaseModel

from ..core.models import ExtractedArtifacts, CodePatch, GeneratedTest
from ..providers.artifact_provider import ArtifactTextProvider, ArtifactExtractionError

_logger = logging.getLogger(__name__)


class ArtifactParsingError(Exception):
    """Custom exception for artifact parsing failures."""
    pass


class ArtifactParser:
    """
    Transforms free-text LLM responses into structured artifacts
    (CodePatches, GeneratedTests) using a separate LLM provider and Pydantic schemas.

    This parser bridges the gap between unstructured LLM output and the strongly-typed
    ExtractedArtifacts schema, enabling reliable artifact handling downstream.
    """

    def __init__(self, llm_provider: Optional[ArtifactTextProvider] = None):
        """
        Initialize the parser with an optional LLM provider for extraction.

        Args:
            llm_provider: Optional ArtifactTextProvider for structured artifact extraction.
                         If None, fallback parsing logic is used.
        """
        self._llm_provider = llm_provider

    def parse(self, raw_llm_analysis: str) -> ExtractedArtifacts:
        """
        Extract artifacts from raw LLM analysis text.

        The parsing process attempts to:
        1. Use LLM-based schema forcing (if provider available) to extract structured data (Phase 5.3)
        2. Fall back to heuristic parsing if LLM fails or no provider available
        3. Return empty artifacts if no artifacts found

        Args:
            raw_llm_analysis: The free-text analysis from AuditAgent

        Returns:
            ExtractedArtifacts with patches and tests lists (never raises)
        """
        try:
            # Try LLM-based extraction if provider available (Phase 5.3)
            if self._llm_provider:
                try:
                    return self._parse_with_llm(raw_llm_analysis)
                except ArtifactParsingError as e:
                    # LLM extraction failed, fall back to heuristic
                    _logger.debug(
                        f"LLM-based extraction failed ({type(e).__name__}), "
                        f"falling back to heuristic parsing: {e}"
                    )
                    return self._parse_heuristic(raw_llm_analysis)

            # No LLM provider, use heuristic parsing
            return self._parse_heuristic(raw_llm_analysis)

        except Exception as e:
            # Unexpected error - log and return empty artifacts rather than crash
            _logger.warning(
                f"Unexpected error during artifact parsing: {e}, returning empty artifacts"
            )
            return ExtractedArtifacts()

    def _parse_with_llm(self, raw_llm_analysis: str) -> ExtractedArtifacts:
        """
        Attempt to extract artifacts using LLM with schema forcing (Phase 5.3).

        This method uses ArtifactTextProvider.generate_structured() to extract
        and validate structured CodePatches and GeneratedTests following
        the Pydantic ExtractedArtifacts schema.

        Args:
            raw_llm_analysis: The LLM analysis text to parse

        Returns:
            ExtractedArtifacts from LLM extraction

        Raises:
            ArtifactParsingError: If LLM extraction fails
        """
        if not self._llm_provider:
            raise ArtifactParsingError("ArtifactTextProvider is not set for LLM-based extraction")

        try:
            # Create extraction prompt with instructions for structured output
            extraction_prompt = self._create_extraction_prompt(raw_llm_analysis)

            # Call LLM with schema forcing to get validated ExtractedArtifacts
            extracted_artifacts = self._llm_provider.generate_structured(
                user_prompt=extraction_prompt,
                target_schema=ExtractedArtifacts
            )

            # Validate that we got a result
            if extracted_artifacts is None:
                raise ArtifactParsingError(
                    "ArtifactTextProvider returned None (likely due to missing API key or validation failure)"
                )

            _logger.debug(
                f"Successfully extracted artifacts via LLM: "
                f"{len(extracted_artifacts.patches)} patches, {len(extracted_artifacts.tests)} tests"
            )
            return extracted_artifacts

        except ArtifactExtractionError as e:
            # Provider-level errors (JSON parsing, validation, etc.)
            _logger.warning(f"LLM-based extraction failed ({type(e).__name__}): {e}")
            raise ArtifactParsingError(f"Structured artifact extraction failed: {e}") from e
        except Exception as e:
            # Unexpected errors
            _logger.warning(f"Unexpected error in LLM-based extraction: {e}")
            raise ArtifactParsingError(f"Unexpected error during extraction: {e}") from e

    def _parse_heuristic(self, text: str) -> ExtractedArtifacts:
        """
        Heuristic parsing of artifact text using pattern matching.

        This is a placeholder implementation that demonstrates how artifacts
        could be detected. Phase 5.2+ will improve with better parsing logic.

        Args:
            text: The text to parse

        Returns:
            ExtractedArtifacts with extracted patches and tests
        """
        patches = []
        tests = []

        # Simple heuristic: Look for code blocks and test patterns
        # This is a placeholder - real implementation would be more sophisticated

        # Example: If text mentions "patch" or "fix", try to extract code
        if "patch" in text.lower() or "fix" in text.lower():
            # Look for code blocks or line number references
            if "line" in text.lower() and ("replace" in text.lower() or "insert" in text.lower()):
                # Simplified extraction - in reality this would be much more robust
                _logger.debug("Detected potential patch in LLM response")

        # Example: If text mentions "test" or "test case", try to extract test
        if "test" in text.lower() and ("def test_" in text or "assert" in text):
            _logger.debug("Detected potential test in LLM response")

        return ExtractedArtifacts(patches=patches, tests=tests)

    def _create_extraction_prompt(self, raw_analysis: str) -> str:
        """
        Create a prompt that guides the LLM to extract structured artifacts.

        Args:
            raw_analysis: The original analysis text

        Returns:
            A prompt for artifact extraction
        """
        prompt = f"""Extract structured artifacts from the following analysis.

Return ONLY the following JSON structure with NO other text:
{{
    "patches": [
        {{
            "file_path": "path/to/file.py",
            "patch_type": "REPLACE_LINES",
            "start_line": 10,
            "end_line": 15,
            "content": "new code here",
            "explanation": "why this patch"
        }}
    ],
    "tests": [
        {{
            "file_path": "tests/test_module.py",
            "test_name": "test_function_name",
            "content": "def test_function_name():\\n    assert True",
            "explanation": "what this test covers"
        }}
    ]
}}

Analysis to extract from:
{raw_analysis}

Return ONLY valid JSON, no other text."""
        return prompt


__all__ = ["ArtifactParser", "ArtifactParsingError"]
