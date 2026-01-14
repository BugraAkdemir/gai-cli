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

# Max total context size (chars) to avoid token limit
MAX_CONTEXT_SIZE = 100_000

def scan_project(root: str = ".") -> str:
    """
    Scan the project and return a formatted context string.
    Prioritizes src, tests, and config files.
    """
    root_path = Path(root).resolve()
    context_parts = []
    
    context_parts.append("## Project Context")
    context_parts.append(f"Root: {root_path.name}")
    context_parts.append("Structure:")
    
    file_contents = []
    total_size = 0
    
    # Priority directories
    PRIORITY_DIRS = {"src", "tests", "lib", "app"}
    
    # First pass: Get all files and categorize
    all_files = []
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root_path)
        
        prefix = "" if rel_dir == Path(".") else str(rel_dir) + "/"
        
        for f in filenames:
            if f.startswith(".") and f not in [".env.example", ".gitignore", "pyproject.toml", "package.json"]:
                continue
            
            file_path = current_dir / f
            rel_file = prefix + f
            
            is_priority = any(part in PRIORITY_DIRS for part in Path(rel_file).parts)
            all_files.append((rel_file, file_path, is_priority))

    # Add structure to context
    for rel_file, _, _ in all_files:
        context_parts.append(f"- {rel_file}")

    # Second pass: Collect content, prioritizing priority files
    # Sort files: priority first
    all_files.sort(key=lambda x: not x[2])
    
    for rel_file, file_path, _ in all_files:
        if file_path.suffix in ALLOWED_EXTENSIONS:
            try:
                stats = file_path.stat()
                if stats.st_size <= MAX_FILE_SIZE:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    
                    if total_size + len(content) > MAX_CONTEXT_SIZE:
                        # Stop adding content if we exceed limit, but continue listing structure
                        continue
                        
                    file_contents.append(f"\n### File: {rel_file}\n```{file_path.suffix[1:]}\n{content}\n```")
                    total_size += len(content)
            except Exception:
                pass

    context_parts.append("\n## File Contents")
    context_parts.extend(file_contents)
    
    return "\n".join(context_parts)
