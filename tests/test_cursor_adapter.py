from pathlib import Path
import pytest

from automation.base_adapter import BaseIDEAdapter
from automation.cursor.cursor_adapter import CursorAdapter


def test_cursor_adapter_inheritance():
    adapter = CursorAdapter()
    assert isinstance(adapter, BaseIDEAdapter)
    assert adapter.ide_name == "cursor"


def test_prepare_workspace(tmp_path):
    adapter = CursorAdapter()
    test_ws = tmp_path / "test_workspace"
    test_ws.mkdir()

    # Tạo file mẫu và .gitkeep
    (test_ws / ".gitkeep").touch()
    (test_ws / "temp_file.txt").write_text("hello", encoding="utf-8")
    (test_ws / "sub_folder").mkdir()
    (test_ws / "sub_folder" / "nested.txt").write_text("world", encoding="utf-8")

    # Gọi prepare_workspace
    cleaned_ws = adapter.prepare_workspace(test_ws)
    assert cleaned_ws.exists()
    assert (cleaned_ws / ".gitkeep").exists()
    assert not (cleaned_ws / "temp_file.txt").exists()
    assert not (cleaned_ws / "sub_folder").exists()


def test_resolve_executable_path():
    adapter = CursorAdapter()
    try:
        path = adapter.resolve_executable_path()
        assert path.exists()
        assert path.suffix.lower() == ".exe"
    except FileNotFoundError:
        # Nếu máy test không cài Cursor thật, pass qua với cảnh báo
        pytest.skip("Cursor chưa được cài đặt trên máy hoặc đường dẫn không khả dụng.")

