"""Unit tests for the Mistral provider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.exceptions import AIProviderError
from agency_toolkit.providers.mistral_provider import MistralProvider


class TestMistralProviderInitialization:
    """Test MistralProvider initialization."""

    def test_provider_initializes_with_api_key_from_env(self):
        """Test that provider reads API key from MISTRAL_API_KEY environment variable."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key_123"}):
            with patch("mistralai.Mistral"):
                provider = MistralProvider()
                assert provider.api_key == "test_key_123"

    def test_provider_raises_error_when_api_key_missing(self):
        """Test that provider raises ValueError when API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="MISTRAL_API_KEY not found"):
                MistralProvider()


class TestMistralProviderGenerate:
    """Test the generate method of MistralProvider."""

    def test_generate_calls_mistral_api_with_correct_params(self):
        """Test that generate properly calls Mistral API."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
            with patch("mistralai.Mistral") as mock_mistral_class:
                mock_client = MagicMock()
                mock_mistral_class.return_value = mock_client

                # Mock the API response
                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Test response"
                mock_client.chat.complete.return_value = mock_response

                provider = MistralProvider()
                result = provider.generate(prompt="Test prompt")

                assert result["response"] == "Test response"
                assert result["provider"] == "mistral"
                assert result["model"] == "mistral-small-latest"

    def test_generate_accepts_custom_model(self):
        """Test that generate accepts custom model parameter."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
            with patch("mistralai.Mistral") as mock_mistral_class:
                mock_client = MagicMock()
                mock_mistral_class.return_value = mock_client

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Response"
                mock_client.chat.complete.return_value = mock_response

                provider = MistralProvider()
                result = provider.generate(prompt="Test", model="mistral-large-latest")

                assert result["model"] == "mistral-large-latest"

    def test_generate_rejects_invalid_model(self):
        """Test that generate rejects invalid model names."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
            with patch("mistralai.Mistral"):
                provider = MistralProvider()

                with pytest.raises(ValueError, match="Invalid model"):
                    provider.generate(prompt="Test", model="invalid-model-xyz")


class TestEnhanceImagePrompt:
    """Test the enhance_image_prompt method."""

    def test_enhance_image_prompt_calls_generate(self):
        """Test that enhance_image_prompt calls generate with system prompt."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
            with patch("mistralai.Mistral") as mock_mistral_class:
                mock_client = MagicMock()
                mock_mistral_class.return_value = mock_client

                mock_response = MagicMock()
                mock_response.choices = [MagicMock()]
                mock_response.choices[0].message.content = "Enhanced prompt"
                mock_client.chat.complete.return_value = mock_response

                provider = MistralProvider()
                result = provider.enhance_image_prompt("sunset")

                assert result == "Enhanced prompt"
                # Verify system prompt was used
                call_args = mock_client.chat.complete.call_args
                messages = call_args.kwargs["messages"]
                assert len(messages) == 2  # system + user
                assert messages[0]["role"] == "system"
                assert "image generation" in messages[0]["content"].lower()

    def test_enhance_image_prompt_raises_on_error(self):
        """Test that enhance_image_prompt raises AIProviderError on failure."""
        with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
            with patch("mistralai.Mistral") as mock_mistral_class:
                mock_client = MagicMock()
                mock_mistral_class.return_value = mock_client
                mock_client.chat.complete.side_effect = Exception("API error")

                provider = MistralProvider()

                with pytest.raises(
                    AIProviderError, match="Image prompt enhancement failed"
                ):
                    provider.enhance_image_prompt("sunset")
