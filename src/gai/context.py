"""
Context handling module for gai-cli.

This module handles `load_context` which processes arguments starting with `@`.
It supports reading single files like `@file.py` and directories like `@src/`.
"""

import os
from pathlib import Path

# Common directories to ignore
IGNORE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules", 
    "dist", "build", ".idea", ".vscode", ".gemini"
}

# Common binary or non-text extensions to ignore
IGNORE_EXTS = {
    ".pyc", ".pyo", ".pyd", ".so", ".dll", ".exe", ".bin", 
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", 
    ".tar", ".gz", ".7z", ".db", ".sqlite", ".sqlite3"
}

def load_context(path_str: str) -> str:
    """
    Load context from a file or directory path.

    Args:
        path_str: The path string (without the leading '@').

    Returns:
        str: A formatted string containing the context for the LLM.

    Raises:
        FileNotFoundError: If the path does not exist.
        PermissionError: If the path cannot be read.
    """
    path = Path(path_str).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path_str}")

    if path.is_file():
        return _read_file_context(path)
    elif path.is_dir():
        return _read_dir_context(path)
    else:
        # Should rarely happen unless it's a socket or device
        raise FileNotFoundError(f"Path is not a valid file or directory: {path_str}")


def _read_file_context(path: Path) -> str:
    """Read a single file and wrap it in context blocks."""
    try:
        content = path.read_text(encoding="utf-8", errors="ignore")
        return (
            f"Analyze the following file:\n\n"
            f"--- {path.name} ---\n"
            f"{content}\n"
            f"--- End of {path.name} ---\n"
        )
    except Exception as e:
        raise PermissionError(f"Could not read file {path.name}: {e}")


def _read_dir_context(path: Path) -> str:
    """Recursively read text files from a directory."""
    context_parts = [f"Analyze the following files from directory '{path.name}':\n"]
    
    file_count = 0
    
    for current_path, dirs, files in os.walk(path):
        # Modify dirs in-place to skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for filename in files:
            file_path = Path(current_path) / filename
            
            # Skip skipped extensions
            if file_path.suffix.lower() in IGNORE_EXTS:
                continue
                
            try:
                # Attempt to read as text
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                
                # Simple check for binary content that might have slipped through (e.g. null bytes)
                if "\0" in content:
                    continue
                
                rel_path = file_path.relative_to(path.parent)
                context_parts.append(
                    f"\n--- {rel_path} ---\n"
                    f"{content}\n"
                )
                file_count += 1
                
            except Exception:
                # Silently skip files we can't read
                continue

    if file_count == 0:
        return f"Directory '{path.name}' contains no readable text files."
        
    context_parts.append(f"\n--- End of directory context ---\n")
    return "".join(context_parts)


def process_prompt(prompt: str) -> str:
    """
    Process a prompt, finding words starting with '@' and expanding them.
    
    Args:
        prompt: The raw user input.
        
    Returns:
        str: The prompt with context injected.
    """
    import re
    
    # We want to match tokens starting with @ but not if they are email addresses (simplistic check)
    # A simple approach: split by whitespace, check tokens.
    # To handle quotes, we might need a more robust parser, but for now, simple whitespace split is verified behavior.
    
    # Actually, let's use a regex to find @path tokens
    # We'll valid path characters (this is simplifying, assuming no spaces in path for this regex version)
    # If users want spaces, they might need to use quotes, but simpler is better for now.
    
    parts = []
    
    # Using split to preserve basic structure. 
    # Note: This means "My file is @foo.txt" works.
    # "My file is '@foo.txt'" might keep the quotes.
    
    tokens = prompt.split()
    
    for token in tokens:
        if token.startswith("@") and len(token) > 1:
            path_str = token[1:]
            try:
                # remove trailing punctuation if any (like . or ,)
                # gentle heuristic: simple strip of common punctuation from end
                # but careful with file extensions.
                # Let's try raw path first.
                
                context_content = load_context(path_str)
                parts.append(context_content)
                
            except (FileNotFoundError, PermissionError):
                # If fail, treat as text
                parts.append(token)
        else:
            parts.append(token)
            
    return " ".join(parts)
