"""
Project scanner module.
Recursively analyzes the project structure to build context for the agent.
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any

from gai.fs import IGNORED_DIRS
from gai import config

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

def scan_project(root: str = ".", force_rescan: bool = False) -> str:
    """
    Scan the project and return a formatted context string.
    Caches the structure in .gai/structure.json to save tokens.
    """
    root_path = Path(root).resolve()
    project_dir = config.get_project_dir()
    cache_file = project_dir / "structure.json"
    
    # 1. Quick pass for all visible files
    all_files = []
    PRIORITY_DIRS = {"src", "tests", "lib", "app"}
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        current_dir = Path(dirpath)
        rel_dir = current_dir.relative_to(root_path)
        prefix = "" if rel_dir == Path(".") else str(rel_dir) + "/"
        
        for f in filenames:
            if f.startswith(".") and f not in [".env.example", ".gitignore", "pyproject.toml", "package.json"]:
                continue
            rel_file = prefix + f
            is_priority = any(part in PRIORITY_DIRS for part in Path(rel_file).parts)
            all_files.append({"rel_path": rel_file, "priority": is_priority})

    # 2. Update Cache
    cache_data = {"structure": all_files}
    cache_file.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")

    # 3. Load Project State (The Brain)
    project_state = config.load_state()

    # 4. Construct Context
    context_parts = []
    context_parts.append("## Project Context")
    context_parts.append(f"Root: {root_path.name}")
    
    if project_state:
        context_parts.append("\n## Project Brain (Internal State)")
        context_parts.append(f"Last Task: {project_state.get('last_task', 'N/A')}")
        context_parts.append(f"Status: {project_state.get('status', 'N/A')}")
        if project_state.get('errors'):
            context_parts.append(f"Remaining Errors: {', '.join(project_state.get('errors'))}")
        context_parts.append("")

    context_parts.append("Structure:")
    for f in all_files:
        context_parts.append(f"- {f['rel_path']}")
        
    context_parts.append("\n## File Contents")
    
    # Second pass: Collect content, prioritizing priority files
    # Only read priority files by default to save tokens, OR all if small enough
    total_size = 0
    file_contents = []
    
    # Group files by priority
    priority_files = [f for f in all_files if f['priority']]
    other_files = [f for f in all_files if not f['priority']]
    
    # Read files until MAX_CONTEXT_SIZE reached
    for f_info in priority_files + other_files:
        rel_path = f_info['rel_path']
        file_path = root_path / rel_path
        
        if file_path.suffix in ALLOWED_EXTENSIONS:
            try:
                stats = file_path.stat()
                if stats.st_size <= MAX_FILE_SIZE:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if total_size + len(content) > MAX_CONTEXT_SIZE:
                        continue
                    file_contents.append(f"\n### File: {rel_path}\n```{file_path.suffix[1:]}\n{content}\n```")
                    total_size += len(content)
            except Exception:
                pass

    context_parts.extend(file_contents)
    return "\n".join(context_parts)
