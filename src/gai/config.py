"""
Configuration management for gai-cli.
Handles loading/saving settings to ~/.gai/config.json and retrieving API keys.
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any, List

# Constants
GLOBAL_CONFIG_DIR = Path.home() / ".gai"
GLOBAL_CONFIG_FILE = GLOBAL_CONFIG_DIR / "config.json"
DEFAULT_MODEL = "gemini-2.0-flash-exp"

CONFIG_DIR = GLOBAL_CONFIG_DIR # For mocking in tests
CONFIG_FILE = GLOBAL_CONFIG_FILE # For mocking in tests

def get_project_dir(root: Optional[Path] = None) -> Path:
    """Get the local .gai directory. Creates it if missing."""
    base = root if root else Path.cwd()
    pdir = base / ".gai"
    if not pdir.exists():
        pdir.mkdir(parents=True, exist_ok=True)
    return pdir

def get_history_file(root: Optional[Path] = None) -> Path:
    """Get the path to the project-specific history file."""
    return get_project_dir(root) / "history.json"

def get_state_file(root: Optional[Path] = None) -> Path:
    """Get the path to the project-specific state file."""
    return get_project_dir(root) / "state.json"

def _load_config() -> Dict[str, Any]:
    """Load global configuration from disk."""
    config_file = globals().get('CONFIG_FILE', GLOBAL_CONFIG_FILE)
    if not config_file.exists():
        return {}
    try:
        return json.loads(config_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

def _save_config(config: Dict[str, Any]):
    """Save global configuration to disk."""
    config_dir = globals().get('CONFIG_DIR', GLOBAL_CONFIG_DIR)
    config_file = globals().get('CONFIG_FILE', GLOBAL_CONFIG_FILE)
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2), encoding="utf-8")

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

def save_model(model: str):
    """Save the model preference."""
    config = _load_config()
    config["model"] = model
    _save_config(config)

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

def get_mode() -> str:
    """Get the operation mode (agent or chat). Default: agent."""
    return _load_config().get("mode", "agent")

def save_mode(mode: str) -> None:
    """Save the operation mode."""
    config = _load_config()
    config["mode"] = mode
    _save_config(config)

def load_history(root: Optional[Path] = None) -> List[Dict[str, str]]:
    """Load session history from the local project .gai directory."""
    hfile = get_history_file(root)
    if not hfile.exists():
        return []
    try:
        return json.loads(hfile.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_history(history: List[Dict[str, str]], root: Optional[Path] = None):
    """Save session history to the local project .gai directory."""
    hfile = get_history_file(root)
    hfile.write_text(json.dumps(history, indent=2), encoding="utf-8")

def clear_history(root: Optional[Path] = None):
    """Clear session history for the current project."""
    hfile = get_history_file(root)
    if hfile.exists():
        hfile.unlink()

def load_state(root: Optional[Path] = None) -> Dict[str, Any]:
    """Load project state from the local .gai directory."""
    sfile = get_state_file(root)
    if not sfile.exists():
        return {}
    try:
        return json.loads(sfile.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_state(state: Dict[str, Any], root: Optional[Path] = None):
    """Save project state to the local .gai directory."""
    sfile = get_state_file(root)
    sfile.write_text(json.dumps(state, indent=2), encoding="utf-8")
