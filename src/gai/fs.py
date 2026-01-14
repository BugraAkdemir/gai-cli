"""
Safe filesystem operations for gai-cli.
Ensures all file actions are restricted to the current working directory.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Union, Optional

class FileSystemError(Exception):
    """Base class for filesystem errors."""
    pass

class UnsafePathError(FileSystemError):
    """Raised when a path is outside the allowed directory or is a system path."""
    pass

# Safety constants
IGNORED_DIRS = {
    'node_modules', '.git', '__pycache__', 'venv', '.venv', '.env', 
    'build', 'dist', '.pytest_cache', '.gai', '.vscode', 'coverage'
}

SYSTEM_PATHS = {
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "/etc", "/usr", "/bin", "/sbin", "/var", "/opt"
}

def validate_path(path: Union[str, Path], root: Optional[Path] = None, allow_new: bool = True) -> Path:
    """
    Validate that a path is safe to modify.
    
    Args:
        path: Relative or absolute path.
        root: The allowed base directory (default: CWD).
        allow_new: If True, path doesn't need to exist yet.
    """
    cwd = (root or Path.cwd()).resolve()
    target_path = Path(path).resolve()
    
    # Check if path is within root
    try:
        target_path.relative_to(cwd)
    except ValueError:
        raise UnsafePathError(f"Path restricted: {path} is outside the allowed directory ({cwd}).")
        
    # Check for specific system path prefixes (defensive depth)
    target_str = str(target_path)
    for sys_path in SYSTEM_PATHS:
        if target_str.startswith(sys_path):
            raise UnsafePathError(f"Path blocked: {path} is a system directory.")
            
    # Check for ignored directories traversal
    parts = target_path.parts
    for part in parts:
        if part in IGNORED_DIRS:
             # We allow reading from ignored dirs? maybe not. 
             # For writing/editing, definitely unsafe to touch internal cache/git files.
             raise UnsafePathError(f"Path restricted: Cannot modify files in {part}.")

    return target_path

def apply_actions(actions: List[Dict[str, str]], root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """
    Execute a list of file actions.
    
    Args:
        actions: List of dicts with 'action', 'path', 'content'.
        root: The base directory for operations.
        
    Returns:
         List of results dicts: {'path': str, 'status': 'success'|'error', 'message': str}
    """
    results = []
    
    for action in actions:
        act_type = action.get("action", "").lower()
        path_str = action.get("path", "")
        content = action.get("content", "")
        
        result = {"path": path_str, "status": "pending"}
        
        try:
            target = validate_path(path_str, root=root, allow_new=True)
            
            if act_type in ("create", "write", "replace"):
                # Ensure parent dirs exist
                target.parent.mkdir(parents=True, exist_ok=True)
                
                # Check create collision
                if act_type == "create" and target.exists():
                     raise FileSystemError("File already exists (action=create)")

                target.write_text(content, encoding="utf-8")
                result["status"] = "success"
                result["message"] = f"Written: {path_str}"
                
            elif act_type == "append":
                if not target.exists():
                    raise FileSystemError("File does not exist (action=append)")
                
                with open(target, "a", encoding="utf-8") as f:
                    f.write(content)
                result["status"] = "success" 
                result["message"] = f"Appended to: {path_str}"

            elif act_type == "delete":
                if not target.exists():
                    # Idempotent success or error? Let's say success but warn.
                    result["message"] = f"Skipped delete (not found): {path_str}"
                    result["status"] = "success"
                else:
                    if target.is_dir():
                        # We generally don't support deleting dirs recursively for safety yet
                        # Unless explicitly handled? Let's block for now for safety.
                         raise FileSystemError("Deleting directories is not supported yet for safety.")
                    
                    target.unlink()
                    result["status"] = "success"
                    result["message"] = f"Deleted: {path_str}"

            elif act_type in ("move", "rename"):
                # 'content' field in this case is actually the 'destination' path
                dest_str = content.strip()
                if not dest_str:
                     raise FileSystemError(f"Move action requires destination path in 'content' field.")
                
                dest_path = validate_path(dest_str, allow_new=True)
                
                if not target.exists():
                    raise FileSystemError(f"Source file not found: {path_str}")
                
                if dest_path.exists():
                    raise FileSystemError(f"Destination already exists: {dest_str}")

                # Ensure dest parent exists
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                target.rename(dest_path)
                result["status"] = "success"
                result["message"] = f"Moved: {path_str} -> {dest_str}"
                
            else:
                raise FileSystemError(f"Unknown action: {act_type}")
                
        except Exception as e:
            result["status"] = "error"
            result["message"] = str(e)
            
        results.append(result)
        
    return results

def read_file(path: str, root: Optional[Path] = None) -> str:
    """Read a file safely."""
    target = validate_path(path, root=root)
    if not target.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return target.read_text(encoding="utf-8")
