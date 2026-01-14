"""
Autocomplete module for gai-cli.

This module provides a prompt_toolkit completer that triggers on '@' to suggest
files and directories for context injection.
"""

import os
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.document import Document
from pathlib import Path

# Reuse ignore lists from context if possible, or define them here to avoid circular deps
IGNORE_DIRS = {
    ".git", "__pycache__", "venv", ".venv", "node_modules", 
    "dist", "build", ".idea", ".vscode", ".gemini"
}

class FileContextCompleter(Completer):
    """
    A completer that suggests files and folders when the input starts with '@'.
    """
    
    def get_completions(self, document: Document, complete_event):
        text_before_cursor = document.text_before_cursor
        
        # Check if we are currently typing a token starting with @
        # We look for the last word
        word = document.get_word_before_cursor(WORD=True)
        
        # If the word before cursor starts with @, or if we just typed @
        # prompt_toolkit's get_word_before_cursor might not capture '@' if it's treated as a separator
        # So we manually check trigger
        
        # A clearer strategy: find the start of the current path argument
        # Simple heuristic: look back for '@'
        
        trigger_index = text_before_cursor.rfind("@")
        
        if trigger_index == -1:
            return
            
        # Ensure that the @ is part of the current word being typed
        # i.e., no spaces between @ and cursor, or only non-space chars
        current_input = text_before_cursor[trigger_index+1:]
        
        if " " in current_input:
            # We moved past the token
            return
            
        # The text to match against filesystem
        path_prefix = current_input
        
        try:
            # Determine directory and partial filename
            if os.path.sep in path_prefix or (os.path.altsep and os.path.altsep in path_prefix):
                dirname, basename = os.path.split(path_prefix)
                search_dir = Path(dirname) if dirname else Path(".")
            else:
                dirname = ""
                basename = path_prefix
                search_dir = Path(".")
            
            # Check if search_dir exists and is a directory
            if not search_dir.exists() or not search_dir.is_dir():
                return
                
            for child in search_dir.iterdir():
                name = child.name
                
                # Filter by basename match
                if not name.startswith(basename):
                    continue
                    
                # Skip ignored directories
                if child.is_dir() and name in IGNORE_DIRS:
                    continue
                
                # Prepare completion text
                # We need to replace the user's input from the last path separator
                completion_text = name
                
                # If directory, append separator
                if child.is_dir():
                    completion_text += os.path.sep
                
                # Yield completion
                # prompt_toolkit expects the full replacement for the matched part
                # But here we are completing the `basename` part
                
                yield Completion(
                    completion_text, 
                    start_position=-len(basename),
                    display=name,
                    display_meta="DIR" if child.is_dir() else "FILE"
                )
                
        except Exception:
            # Gracefully fail on path errors
            return
