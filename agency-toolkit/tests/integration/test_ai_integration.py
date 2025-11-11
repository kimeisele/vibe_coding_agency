"""Integration tests for the Mistral API provider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from agency_toolkit.providers.mistral_provider import MistralProvider


@pytest.fixture
def mock_mistral_client():
    """Mocks the Mistral API client to avoid real network calls."""
    with patch("mistralai.Mistral") as mock_mistral_constructor:
        mock_client = MagicMock()
        # Mock the response structure
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Mocked Mistral response"
        mock_client.chat.complete.return_value = mock_response
        mock_mistral_constructor.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def mock_api_key():
    """Automatically mocks the API key for all tests in this module."""
    with patch.dict(os.environ, {"MISTRAL_API_KEY": "test_key"}):
        yield


# --- MistralProvider Integration Tests ---


def test_provider_generate_with_valid_prompt_returns_response(mock_mistral_client):
    """Test that MistralProvider.generate returns properly formatted response."""
    provider = MistralProvider()
    response = provider.generate(prompt="Hello")

    assert response["response"] == "Mocked Mistral response"
    assert response["provider"] == "mistral"
    mock_mistral_client.chat.complete.assert_called_once()


def test_provider_generate_with_system_prompt(mock_mistral_client):
    """Test that system prompt is properly passed to API."""
    provider = MistralProvider()
    provider.generate(
        prompt="Test",
        system_prompt="You are helpful",
    )

    call_args = mock_mistral_client.chat.complete.call_args
    messages = call_args.kwargs["messages"]
    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == "You are helpful"
    assert messages[1]["role"] == "user"


def test_provider_generate_with_custom_parameters(mock_mistral_client):
    """Test that custom parameters are passed to API."""
    provider = MistralProvider()
    provider.generate(
        prompt="Test",
        temperature=0.3,
        max_tokens=500,
    )

    call_args = mock_mistral_client.chat.complete.call_args
    assert call_args.kwargs["temperature"] == 0.3
    assert call_args.kwargs["max_tokens"] == 500


def test_provider_handles_rate_limit_error(mock_mistral_client):
    """Test that rate limit errors are properly handled."""
    mock_mistral_client.chat.complete.side_effect = Exception("429 Rate limit")

    provider = MistralProvider()
    with pytest.raises(Exception, match="Rate limit exceeded"):
        provider.generate(prompt="test")


def test_provider_handles_timeout_error(mock_mistral_client):
    """Test that timeout errors are properly handled."""
    mock_mistral_client.chat.complete.side_effect = Exception("timeout")

    provider = MistralProvider()
    with pytest.raises(Exception, match="Mistral API timeout"):
        provider.generate(prompt="test")


def test_provider_handles_server_error(mock_mistral_client):
    """Test that server errors are properly handled."""
    mock_mistral_client.chat.complete.side_effect = Exception(
        "500 Internal server error"
    )

    provider = MistralProvider()
    with pytest.raises(Exception, match="Mistral API server error"):
        provider.generate(prompt="test")
