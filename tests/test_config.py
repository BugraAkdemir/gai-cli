import os
import json
import pytest
from pathlib import Path
from gai import config

def test_load_config_empty(tmp_path, monkeypatch):
    # Mock CONFIG_FILE to a temporary path
    mock_config = tmp_path / "config.json"
    monkeypatch.setattr(config, "CONFIG_FILE", mock_config)
    
    # Should return empty dict if file doesn't exist
    assert config._load_config() == {}

def test_save_load_api_key(tmp_path, monkeypatch):
    mock_dir = tmp_path / ".gai"
    mock_config = mock_dir / "config.json"
    monkeypatch.setattr(config, "CONFIG_DIR", mock_dir)
    monkeypatch.setattr(config, "CONFIG_FILE", mock_config)
    
    test_key = "test-api-key"
    config.save_api_key(test_key)
    
    assert config.get_api_key() == test_key
    assert json.loads(mock_config.read_text())["api_key"] == test_key

def test_get_api_key_env_priority(tmp_path, monkeypatch):
    monkeypatch.setenv("GAI_API_KEY", "env-key")
    # Even if config has a key, env should take priority
    monkeypatch.setattr(config, "_load_config", lambda: {"api_key": "config-key"})
    
    assert config.get_api_key() == "env-key"

def test_get_model_default():
    # Test should check against the DEFAULT_MODEL constant
    # User may have a different model configured
    default = config.DEFAULT_MODEL
    assert default == "gemini-2.0-flash-exp"
