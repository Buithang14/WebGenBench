import pytest
from experiment.task_loader import load_task, list_available_tasks

def test_load_task_t01_success():
    task = load_task("T01")
    assert task.meta.task_id == "T01"
    assert task.meta.name == "Login Form"
    assert "index.html" in task.meta.expected_files
    assert "style.css" in task.meta.expected_files
    assert "script.js" in task.meta.expected_files
    
    # Kiểm tra prompt
    assert len(task.prompt_text) > 0
    assert "index.html" in task.prompt_text
    assert "style.css" in task.prompt_text
    
    # Kiểm tra ảnh thiết kế
    assert task.reference_image_path.exists()
    assert task.image_dimensions == (1440, 900)

def test_load_nonexistent_task():
    with pytest.raises(FileNotFoundError):
        load_task("T99_INVALID")

def test_list_available_tasks():
    tasks = list_available_tasks()
    assert "T01" in tasks

