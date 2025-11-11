"""
ArtifactTextProvider: Specialized LLM provider for structured artifact extraction.

Extends TextProvider with generate_structured() method to support Pydantic
schema-forcing for reliable CodePatch and GeneratedTest extraction.
"""

import json
import logging
from typing import Type, TypeVar, Optional, Any, Dict

from pydantic import BaseModel, ValidationError

from .base import TextProvider
from ..core.models import ExtractedArtifacts

_logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ArtifactExtractionError(Exception):
    """Custom exception for structured LLM extraction failures."""

    pass


class ArtifactTextProvider(TextProvider):
    """
    Specialized LLM provider supporting forced structured output via Pydantic schemas.

    Extends TextProvider with generate_structured() method to extract CodePatches
    and GeneratedTests with guaranteed schema compliance.

    Features:
    - Pydantic schema validation for LLM output
    - Graceful fallback on validation errors
    - Type-safe extraction with TypeVar support
    - Comprehensive error handling and logging
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "mock-artifact-extractor", **kwargs):
        """
        Initialize the specialized artifact extraction provider.

        Args:
            api_key: Optional API key for LLM service
            model: Model identifier for artifact extraction
            **kwargs: Additional provider-specific arguments
        """
        self._api_key = api_key
        self._model = model
        self._kwargs = kwargs

    # =====================================
    # Required TextProvider methods
    # =====================================

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate text response (standard LLM call).

        Args:
            prompt: The input prompt
            model: Model to use (uses default if None)
            temperature: Sampling temperature
            max_tokens: Maximum output tokens
            system_prompt: Optional system message

        Returns:
            Dictionary with response and metadata
        """
        return {
            "response": f"Artifact extraction analysis based on: {prompt[:100]}...",
            "model": model or self._model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "timestamp": "2025-11-10T14:00:00Z",
            "provider": "artifact_provider",
        }

    def estimate_cost(self, prompt_tokens: int, max_tokens: int) -> float:
        """
        Estimate cost for extraction (Task 4.1: Token Transparency).

        Args:
            prompt_tokens: Number of input tokens
            max_tokens: Maximum output tokens

        Returns:
            Estimated cost in USD
        """
        # Mock pricing: $0.0001 base + $0.000005 per input token
        return 0.0001 + (prompt_tokens / 1000) * 0.000005

    def get_available_models(self) -> list[str]:
        """
        Get list of available models.

        Returns:
            List of model identifiers
        """
        return ["gemini-2.5-flash-structured", "artifact-extractor-v1", "mock-artifact-extractor"]

    def get_audit_analysis(self, context: str) -> str:
        """
        Get general audit analysis (not used for artifact extraction).

        Args:
            context: Analysis context

        Returns:
            Empty string (artifact provider focuses on structured extraction)
        """
        return ""

    # =====================================
    # Core Phase 5.3 Method
    # =====================================

    def generate_structured(
        self, user_prompt: str, target_schema: Type[T]
    ) -> Optional[T]:
        """
        Generate and extract structured data following a Pydantic schema.

        This is the core method for Phase 5.3 (Multi-Model Orchestration).
        It combines LLM generation with schema-forced output validation.

        Args:
            user_prompt: The extraction prompt (includes raw LLM analysis)
            target_schema: Pydantic model class to validate output against

        Returns:
            Instance of target_schema with validated data, or None on failure

        Raises:
            ArtifactExtractionError: If LLM call fails or validation errors
        """
        if not self._api_key:
            _logger.warning(
                "ArtifactTextProvider: API key not set. Cannot perform LLM-based extraction."
            )
            return None

        try:
            # Step 1: Call LLM with extraction instructions
            llm_response = self.generate(
                prompt=user_prompt,
                temperature=0.2,  # Low temperature for deterministic output
                max_tokens=2000,
            )

            response_text = llm_response.get("response", "")
            _logger.debug(f"LLM extraction response (first 200 chars): {response_text[:200]}...")

            # Step 2: Parse response as JSON (Phase 5.3 will improve this)
            # For MVP, we attempt to extract JSON from response
            extracted_data = self._extract_json_from_response(response_text)

            # Step 3: Validate against schema
            validated_artifact = target_schema.model_validate(extracted_data)
            _logger.debug(
                f"Successfully extracted and validated artifacts: "
                f"{type(validated_artifact).__name__}"
            )

            return validated_artifact

        except ValidationError as e:
            _logger.error(f"Pydantic validation failed for {target_schema.__name__}: {e}")
            raise ArtifactExtractionError(
                f"Schema validation failed: {e.error_count()} errors"
            ) from e
        except json.JSONDecodeError as e:
            _logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise ArtifactExtractionError(f"JSON parsing failed: {e}") from e
        except Exception as e:
            _logger.error(f"Unexpected error in structured extraction: {e}")
            raise ArtifactExtractionError(f"Unexpected error: {e}") from e

    # =====================================
    # Helper Methods
    # =====================================

    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response text.

        Attempts to find and parse JSON from the response, handling various formats
        (JSON blocks, inline JSON, etc.).

        Args:
            response_text: The raw LLM response

        Returns:
            Dictionary with extracted JSON data

        Raises:
            json.JSONDecodeError: If no valid JSON found
        """
        # Try to find JSON block markers
        if "```json" in response_text:
            # Extract content between json markers
            json_start = response_text.index("```json") + 7
            json_end = response_text.index("```", json_start)
            json_text = response_text[json_start:json_end].strip()
            return json.loads(json_text)

        # Try to find { ... } block
        if "{" in response_text:
            # Find the first { and last }
            start_idx = response_text.index("{")
            end_idx = response_text.rindex("}") + 1
            json_text = response_text[start_idx:end_idx]
            return json.loads(json_text)

        # No JSON found - return empty dict (will be caught by validation)
        raise json.JSONDecodeError("No JSON found in response", response_text, 0)


__all__ = ["ArtifactTextProvider", "ArtifactExtractionError"]
