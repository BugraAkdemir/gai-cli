"""
Theme definitions for gai-cli.
"""

from typing import Dict

THEMES: Dict[str, Dict[str, str]] = {
    "default": {
        "user": "bold #f8fafc",       # White/Slate 50
        "ai": "bold #f8fafc",         # White
        "accent": "#ef4444",          # Red 500 (Claude Border Red)
        "info": "#94a3b8",            # Slate 400
        "error": "bold #ef4444",      # Red 500
        "success": "bold #22c55e",    # Green 500
        "header": "bold #ef4444",     # Red Accent
        "border": "#7f1d1d"           # Deep Red / Maroon (Slate 700 fallback: #334155)
    },
    "dark": {
        "user": "bold #fcfcfc",
        "ai": "bold #fcfcfc",
        "accent": "#f87171",          # Soft Red
        "info": "#6b7280",
        "error": "bold #f87171",
        "success": "bold #4ade80",
        "header": "bold #f87171",
        "border": "#450a0a"           # Very Dark Red
    },
    "light": {
        "user": "bold #0f172a",
        "ai": "bold #0f172a",
        "accent": "#dc2626",          # Bright Red
        "info": "#64748b",
        "error": "bold #dc2626",
        "success": "bold #16a34a",
        "header": "bold #dc2626",
        "border": "#fee2e2"           # Light Red wash
    }
}

def get_theme(name: str) -> Dict[str, str]:
    """Get a theme by name."""
    return THEMES.get(name, THEMES["default"])
