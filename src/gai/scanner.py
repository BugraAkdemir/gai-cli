"""
Project scanner module.
Recursively analyzes the project structure to build context for the agent.
"""

import os
from pathlib import Path
from typing import List

from gai.fs import IGNORED_DIRS

# Skip files larger than this (bytes)
MAX_FILE_SIZE = 50_000 

# Extensions to include in context
ALLOWED_EXTENSIONS = {
    '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', '.json', 
    '.yaml', '.yml', '.toml', '.md', '.txt', '.sh', '.bat', 
    '.dart', '.go', '.rs', '.java', '.c', '.cpp', '.h'
}

def is_ignored(path: Path) -> bool:
    """Check if path contains any ignored directories."""
    for part in path.parts:
        if part in IGNORED_DIRS:
            return True
    return False

def scan_project(root: str = ".") -> str:
    """
    Scan the project and return a formatted context string.
    """
    root_path = Path(root).resolve()
    context_parts = []
    
    context_parts.append("## Project Context")
    context_parts.append(f"Root: {root_path.name}")
    context_parts.append("Structure:")
    
    file_contents = []
    
    # First pass: structure
    for dirpath, dirnames, filenames in os.walk(root_path):
        # Modify dirnames in-place to skip ignored
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root_path)
        
        if rel_dir == Path("."):
            prefix = ""
        else:
            prefix = str(rel_dir) + "/"
            
        for f in filenames:
            file_path = current_dir / f
            rel_file = prefix + f
            
            # Skip hidden files unless important
            if f.startswith(".") and f not in [".env.example", ".gitignore"]:
                continue
                
            context_parts.append(f"- {rel_file}")
            
            # Content Collection Logic
            if file_path.suffix in ALLOWED_EXTENSIONS:
                try:
                    stats = file_path.stat()
                    if stats.st_size <= MAX_FILE_SIZE:
                        try:
                            content = file_path.read_text(encoding="utf-8", errors="ignore")
                            file_contents.append(f"\n### File: {rel_file}\n```{file_path.suffix[1:]}\n{content}\n```")
                        except Exception:
                            pass # Skip read errors
                except Exception:
                    pass

    context_parts.append("\n## File Contents")
    context_parts.extend(file_contents)
    
    return "\n".join(context_parts)
