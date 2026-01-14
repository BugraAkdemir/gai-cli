"""
Configuration management for gai-cli.
Handles loading/saving settings to ~/.gai/config.json and retrieving API keys.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

# Constants
CONFIG_DIR = Path.home() / ".gai"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_MODEL = "gemini-2.0-flash-exp"

def _ensure_config_dir():
    """Ensure the config directory exists."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

def _load_config() -> Dict[str, Any]:
    """Load configuration from disk."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

def _save_config(config: Dict[str, Any]):
    """Save configuration to disk."""
    _ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")

def get_api_key() -> Optional[str]:
    """
    Retrieve the API key from environment variables or config file.
    Priority:
    1. GAI_API_KEY (env)
    2. GEMINI_API_KEY (env)
    3. config.json
    """
    # Check environment variables
    env_key = os.getenv("GAI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if env_key:
        return env_key
        
    # Check config file
    config = _load_config()
    return config.get("api_key")

def save_api_key(api_key: str):
    """Save the API key to the config file."""
    config = _load_config()
    config["api_key"] = api_key
    _save_config(config)

def get_model() -> str:
    """Get the configured model name or default."""
    config = _load_config()
    return config.get("model", DEFAULT_MODEL)

def get_language() -> str:
    """Get the configured language code."""
    config = _load_config()
    return config.get("language", "en")

def save_language(lang: str):
    """Save the language preference."""
    config = _load_config()
    config["language"] = lang
    _save_config(config)

def get_theme() -> str:
    """Get the configured theme name."""
    config = _load_config()
    return config.get("theme", "default")

def save_theme(theme: str):
    """Save the theme preference."""
    config = _load_config()
    config["theme"] = theme
    _save_config(config)
