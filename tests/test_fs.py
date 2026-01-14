import os
import pytest
from pathlib import Path
from gai import fs

def test_validate_path_safe():
    cwd = Path.cwd().resolve()
    # Test a file in the project
    safe_path = cwd / "src" / "gai" / "cli.py"
    assert fs.validate_path(safe_path) == safe_path

def test_validate_path_unsafe():
    # Test a path outside project (e.g., home directory or root)
    if os.name == 'nt':
        unsafe_path = "C:\\Windows\\System32"
    else:
        unsafe_path = "/etc/passwd"
        
    with pytest.raises(fs.UnsafePathError):
        fs.validate_path(unsafe_path)

def test_apply_actions_create_delete(tmp_path, monkeypatch):
    # Mock CWD to tmp_path for safety during test
    monkeypatch.chdir(tmp_path)
    
    test_file = "test_io.txt"
    actions = [
        {"action": "create", "path": test_file, "content": "hello world"}
    ]
    
    results = fs.apply_actions(actions)
    assert results[0]["status"] == "success"
    assert (tmp_path / test_file).read_text() == "hello world"
    
    # Test delete
    delete_actions = [{"action": "delete", "path": test_file}]
    fs.apply_actions(delete_actions)
    assert not (tmp_path / test_file).exists()
