"""Unit tests for Google Generative AI text provider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.providers.google_provider import VALID_MODELS, GoogleProvider


class TestGoogleProviderInitialization:
    """Test GoogleProvider initialization and API key handling."""

    @patch("google.generativeai.configure")
    def test_init_with_explicit_api_key(self, _mock_configure):
        """Test initialization with explicit API key."""
        provider = GoogleProvider(api_key="test-key-123")
        assert provider.api_key == "test-key-123"

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key-456"})
    @patch("google.generativeai.configure")
    def test_init_with_env_api_key(self, _mock_configure):
        """Test initialization with environment variable API key."""
        provider = GoogleProvider()
        assert provider.api_key == "env-key-456"

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key_raises_value_error(self):
        """Test that missing API key raises ValueError with helpful message."""
        with pytest.raises(ValueError) as exc_info:
            GoogleProvider()
        error_message = str(exc_info.value)
        assert "GOOGLE_API_KEY not found" in error_message
        assert "export GOOGLE_API_KEY" in error_message
        assert "makersuite.google.com" in error_message


class TestGoogleProviderGenerate:
    """Test GoogleProvider text generation."""

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_generate_with_default_model(self, _mock_configure, mock_model_class):
        """Test generate with default model (gemini-2.5-flash)."""
        # Setup
        mock_response = MagicMock()
        mock_response.text = "Generated response text"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")

        # Execute
        result = provider.generate("Test prompt")

        # Verify
        assert result["response"] == "Generated response text"
        assert result["model"] == "gemini-2.5-flash"
        assert result["provider"] == "google"
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 1000
        assert "timestamp" in result

        # Verify model was called correctly
        mock_model_class.assert_called_once()
        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs["model_name"] == "gemini-2.5-flash"
        assert call_kwargs["generation_config"]["temperature"] == 0.7
        assert call_kwargs["generation_config"]["max_output_tokens"] == 1000

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_generate_with_custom_model(self, _mock_configure, mock_model_class):
        """Test generate with custom model."""
        mock_response = MagicMock()
        mock_response.text = "Custom model response"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        result = provider.generate("Test prompt", model="gemini-1.5-pro")

        assert result["model"] == "gemini-1.5-pro"
        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs["model_name"] == "gemini-1.5-pro"

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_generate_with_system_prompt(self, _mock_configure, mock_model_class):
        """Test generate with system prompt prepended."""
        mock_response = MagicMock()
        mock_response.text = "Response with system context"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        result = provider.generate(
            "User prompt", system_prompt="You are a helpful assistant"
        )

        # Verify system prompt was prepended
        call_args = mock_model_instance.generate_content.call_args[0]
        full_prompt = call_args[0]
        assert "You are a helpful assistant" in full_prompt
        assert "User prompt" in full_prompt
        assert result["response"] == "Response with system context"

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_generate_with_custom_temperature_and_tokens(
        self, _mock_configure, mock_model_class
    ):
        """Test generate with custom temperature and max_tokens."""
        mock_response = MagicMock()
        mock_response.text = "Custom config response"
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        result = provider.generate("Test prompt", temperature=0.9, max_tokens=2000)

        assert result["temperature"] == 0.9
        assert result["max_tokens"] == 2000
        call_kwargs = mock_model_class.call_args[1]
        assert call_kwargs["generation_config"]["temperature"] == 0.9
        assert call_kwargs["generation_config"]["max_output_tokens"] == 2000

    @patch("google.generativeai.configure")
    def test_generate_with_invalid_model_raises_value_error(self, _mock_configure):
        """Test that invalid model raises ValueError."""
        provider = GoogleProvider(api_key="test-key")
        with pytest.raises(ValueError) as exc_info:
            provider.generate("Test prompt", model="invalid-model")
        error_message = str(exc_info.value)
        assert "Invalid model 'invalid-model'" in error_message
        assert "gemini-" in error_message  # Should list available models


class TestGoogleProviderErrorHandling:
    """Test GoogleProvider error handling."""

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_quota_error_handling(self, _mock_configure, mock_model_class):
        """Test handling of quota exceeded errors."""
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("Quota exceeded")
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        with pytest.raises(Exception) as exc_info:
            provider.generate("Test prompt")
        assert "quota exceeded" in str(exc_info.value).lower()

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_timeout_error_handling(self, _mock_configure, mock_model_class):
        """Test handling of timeout errors."""
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("Request timeout")
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        with pytest.raises(Exception) as exc_info:
            provider.generate("Test prompt")
        assert "timeout" in str(exc_info.value).lower()

    @patch("google.generativeai.GenerativeModel")
    @patch("google.generativeai.configure")
    def test_server_error_handling(self, _mock_configure, mock_model_class):
        """Test handling of server errors (5xx)."""
        mock_model_instance = MagicMock()
        mock_model_instance.generate_content.side_effect = Exception("500 Server Error")
        mock_model_class.return_value = mock_model_instance

        provider = GoogleProvider(api_key="test-key")
        with pytest.raises(Exception) as exc_info:
            provider.generate("Test prompt")
        assert "server error" in str(exc_info.value).lower()


class TestGoogleProviderUtilityMethods:
    """Test GoogleProvider utility methods."""

    @patch("google.generativeai.configure")
    def test_estimate_cost(self, _mock_configure):
        """Test cost estimation for Google GenAI."""
        provider = GoogleProvider(api_key="test-key")
        cost = provider.estimate_cost(prompt_tokens=1000, max_tokens=500)
        # Gemini 1.5 Flash: $0.00001875/1K input, $0.000075/1K output
        expected_cost = (1000 / 1000) * 0.00001875 + (500 / 1000) * 0.000075
        assert abs(cost - expected_cost) < 0.0001

    @patch("google.generativeai.configure")
    def test_get_available_models(self, _mock_configure):
        """Test getting list of available models."""
        provider = GoogleProvider(api_key="test-key")
        models = provider.get_available_models()
        assert isinstance(models, list)
        assert "gemini-2.5-flash" in models  # Current default model
        assert "gemini-1.5-flash" in models  # Legacy support
        assert "gemini-1.5-pro" in models
        assert len(models) == len(VALID_MODELS)
        assert len(models) > 0  # Ensure list is not empty

    @patch("google.generativeai.configure")
    def test_get_available_models_returns_copy(self, _mock_configure):
        """Test that get_available_models returns a copy, not reference."""
        provider = GoogleProvider(api_key="test-key")
        models1 = provider.get_available_models()
        models2 = provider.get_available_models()
        assert models1 is not models2
        assert models1 == models2
