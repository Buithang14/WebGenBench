from pathlib import Path
import pytest

from automation.clipboard_helper import (
    copy_text_to_clipboard,
    get_text_from_clipboard,
    copy_image_to_clipboard,
    is_image_in_clipboard,
)

BASE_DIR = Path(__file__).resolve().parent.parent


def test_copy_text_to_clipboard_vietnamese():
    test_text = "WebGenBench: Đăng nhập tài khoản với giao diện tiếng Việt UTF-8 chuẩn xác 100%!"
    success = copy_text_to_clipboard(test_text)
    assert success is True

    read_back = get_text_from_clipboard()
    assert read_back == test_text


def test_copy_image_to_clipboard():
    image_path = BASE_DIR / "designs" / "T01_reference.png"
    assert image_path.exists(), "File designs/T01_reference.png phải tồn tại để kiểm thử."

    success = copy_image_to_clipboard(image_path)
    assert success is True

    has_image = is_image_in_clipboard()
    assert has_image is True


def test_copy_nonexistent_image():
    fake_path = BASE_DIR / "designs" / "nonexistent_image.png"
    success = copy_image_to_clipboard(fake_path)
    assert success is False

