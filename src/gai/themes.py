"""
Theme definitions for gai-cli.
"""

from typing import Dict

THEMES: Dict[str, Dict[str, str]] = {
    "default": {
        "user": "bold #4f81fb",       # Professional Blue
        "ai": "bold #d97757",         # Warm terracotta (Claude-ish) / or Gemini #8e44ad? Let's go specific Gemini: "bold #cba6f7" (Soft Purple)
                                      # Actually user said "Claude CLI benzet" -> Claude uses distinct headers.
                                      # Let's use: User=Blue/Indigo, AI=Orange/TerraCotta is common, OR User=Green, AI=ClaudeColor.
                                      # Let's stick to a clean Gemini palette but minimal.
                                      # User: Bold Cyan. AI: Soft White/Purple.
        "user": "bold #38bdf8",     # Sky Blue
        "ai": "bold #fb923c",       # Soft Orange (Claude-like friendliness)
        "accent": "dim #94a3b8",      # Slate 400
        "info": "dim #64748b",        # Slate 500
        "error": "bold #ef4444",      # Red 500
        "success": "bold #22c55e",    # Green 500
        "header": "bold #f1f5f9",     # Slate 100
        "border": "dim #334155"       # Slate 700
    },
    "dark": {
        "user": "bold #818cf8",       # Indigo 400
        "ai": "bold #e879f9",         # Fuchsia 400
        "accent": "dim #6b7280",
        "info": "dim #4b5563",
        "error": "bold #f87171",
        "success": "bold #4ade80",
        "header": "bold white",
        "border": "dim #374151"
    },
    "light": {
        "user": "bold #0284c7",       # Sky 600
        "ai": "bold #ea580c",         # Orange 600
        "accent": "dim #64748b",
        "info": "dim #94a3b8",
        "error": "bold #dc2626",
        "success": "bold #16a34a",
        "header": "bold #0f172a",
        "border": "dim #cbd5e1"
    }
}

def get_theme(name: str) -> Dict[str, str]:
    """Get a theme by name."""
    return THEMES.get(name, THEMES["default"])
