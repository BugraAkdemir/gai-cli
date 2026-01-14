import pytest
from unittest.mock import MagicMock
from gai import gemini, config

def test_generate_response_mock(monkeypatch):
    # Mock the GenAI Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Mocked Response"
    mock_client.models.generate_content.return_value = mock_response
    
    monkeypatch.setattr("google.genai.Client", lambda api_key: mock_client)
    monkeypatch.setattr(config, "get_api_key", lambda: "fake-key")
    
    response = gemini.generate_response("Hello")
    assert response == "Mocked Response"
    mock_client.models.generate_content.assert_called_once()

def test_gemini_missing_key(monkeypatch):
    monkeypatch.setattr(config, "get_api_key", lambda: None)
    with pytest.raises(gemini.APIKeyMissingError):
        gemini.generate_response("Hello")
