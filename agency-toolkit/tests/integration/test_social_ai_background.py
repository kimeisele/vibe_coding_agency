"""Integration tests for AI-generated social media backgrounds (WU-3.1b).

Tests the refactoring plan implementation for AI background generation
with proper fallback handling and error scenarios.
"""

from pathlib import Path
from unittest.mock import patch

from agency_toolkit.core.social.generator import generate as generate_social
from agency_toolkit.exceptions import AIProviderError, ImageProviderError


class TestAIBackgroundGeneration:
    """Test suite for AI background generation in social posts."""

    def test_generate_with_bg_concept_calls_enhance_prompt(self, tmp_path):
        """Test that bg_concept triggers prompt enhancement."""
        with (
            patch(
                "agency_toolkit.providers.mistral_provider.MistralProvider.enhance_image_prompt"
            ) as mock_enhance,
            patch("agency_toolkit.image_gen.generate_image") as mock_generate_image,
        ):
            mock_enhance.return_value = "enhanced: beautiful sunset"

            mock_generate_image.return_value = {
                "path": str(tmp_path / "generated_bg.png"),
                "cost": 0.01,
                "seed": 12345,
                "model": "flux",
                "provider": "replicate",
            }

            # Create a mock image file
            from PIL import Image

            mock_img = Image.new("RGB", (1080, 1080), color="blue")
            mock_img.save(tmp_path / "generated_bg.png")

            # Call generate_social with bg_concept
            result = generate_social(
                text="Test post",
                bg_concept="sunset over mountains",
                output_dir=tmp_path,
                dry_run=False,
            )

            # Assertions
            assert result["path"]
            mock_enhance.assert_called_once_with("sunset over mountains")

    def test_generate_with_bg_concept_generates_deterministic_seed(self, tmp_path):
        """Test that seed is deterministically generated from text and concept."""
        with (
            patch(
                "agency_toolkit.providers.mistral_provider.MistralProvider.enhance_image_prompt"
            ) as mock_enhance,
            patch("agency_toolkit.image_gen.generate_image") as mock_generate_image,
        ):
            mock_enhance.return_value = "enhanced prompt"

            # Create mock image
            from PIL import Image

            mock_img = Image.new("RGB", (1080, 1080))
            mock_img.save(tmp_path / "test_bg.png")

            mock_generate_image.return_value = {
                "path": str(tmp_path / "test_bg.png"),
                "cost": 0.01,
                "seed": 0,
                "model": "flux",
                "provider": "replicate",
            }

            text = "Test post"
            concept = "mountain landscape"

            generate_social(
                text=text,
                bg_concept=concept,
                output_dir=tmp_path,
                dry_run=False,
            )

            # Extract the seed that was passed to generate_image
            call_args = mock_generate_image.call_args
            passed_seed = call_args.kwargs["seed"]

            # Expected seed should be deterministic from text+concept
            expected_seed = hash(text + concept) % (2**32)
            assert passed_seed == expected_seed

    def test_generate_with_ai_failure_falls_back_to_gradient(self, tmp_path):
        """Test that AI generation failure gracefully falls back to gradient."""
        with (
            patch(
                "agency_toolkit.providers.mistral_provider.MistralProvider.enhance_image_prompt"
            ) as mock_enhance,
            patch("agency_toolkit.image_gen.generate_image") as mock_generate_image,
        ):
            mock_enhance.return_value = "enhanced"

            # Simulate failure
            mock_generate_image.side_effect = ImageProviderError("API error")

            result = generate_social(
                text="Test post",
                bg_concept="test concept",
                output_dir=tmp_path,
                dry_run=False,
            )

            # Should still generate an image (with fallback)
            assert result["path"]
            assert Path(result["path"]).name.startswith("social_")

    def test_generate_with_enhance_prompt_failure_falls_back(self, tmp_path):
        """Test that prompt enhancement failure falls back to gradient."""
        with patch(
            "agency_toolkit.providers.mistral_provider.MistralProvider.enhance_image_prompt"
        ) as mock_enhance:
            mock_enhance.side_effect = AIProviderError("API error")

            result = generate_social(
                text="Test post",
                bg_concept="test concept",
                output_dir=tmp_path,
                dry_run=False,
            )

            # Should still generate an image (with fallback)
            assert result["path"]
            assert Path(result["path"]).name.startswith("social_")

    def test_generate_respects_priority_explicit_background_over_concept(
        self, tmp_path
    ):
        """Test that explicit background_image_path takes priority over bg_concept."""
        # Create explicit background
        from PIL import Image

        explicit_bg = Image.new("RGB", (1080, 1080), color="red")
        bg_path = tmp_path / "explicit_bg.png"
        explicit_bg.save(bg_path)

        with patch(
            "agency_toolkit.providers.mistral_provider.MistralProvider.enhance_image_prompt"
        ) as mock_enhance:
            result = generate_social(
                text="Test post",
                background_image_path=bg_path,
                bg_concept="this should be ignored",
                output_dir=tmp_path,
                dry_run=False,
            )

            # enhance_image_prompt should NOT be called
            mock_enhance.assert_not_called()
            assert result["path"]

    def test_generate_without_bg_concept_uses_gradient(self, tmp_path):
        """Test that without bg_concept, gradient is used as fallback."""
        result = generate_social(
            text="Test post",
            style="modern",
            color="blue",
            output_dir=tmp_path,
            dry_run=False,
        )

        # Should create image successfully with gradient
        assert result["path"]
        assert Path(result["path"]).exists()

    def test_generate_with_invalid_background_path_falls_back_to_gradient(
        self, tmp_path
    ):
        """Test that invalid background path falls back to gradient."""
        invalid_path = tmp_path / "nonexistent.png"

        result = generate_social(
            text="Test post",
            background_image_path=invalid_path,
            output_dir=tmp_path,
            dry_run=False,
        )

        # Should still create image (with gradient fallback)
        assert result["path"]
        assert Path(result["path"]).exists()

    def test_enhance_image_prompt_creates_vivid_descriptions(self):
        """Test that enhance_image_prompt produces detailed prompts."""
        from agency_toolkit.providers.mistral_provider import MistralProvider

        with patch.object(MistralProvider, "generate") as mock_generate:
            mock_generate.return_value = {
                "response": "A breathtaking sunset painting with golden light rays",
                "model": "mistral-small-latest",
                "temperature": 0.7,
                "max_tokens": 200,
                "timestamp": "2024-11-07T20:00:00",
                "provider": "mistral",
            }

            provider = MistralProvider.__new__(MistralProvider)
            result = provider.enhance_image_prompt("sunset")

            assert "sunset" in result.lower()
            assert len(result) > 10  # Should be descriptive

            # Verify system prompt was used
            call_args = mock_generate.call_args
            assert "image generation" in call_args.kwargs["system_prompt"].lower()
