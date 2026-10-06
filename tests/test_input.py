import pytest
from pathlib import Path
from src.utils import validate_input_source, load_image

def test_missing_input_raises_filenotfound():
    with pytest.raises(FileNotFoundError):
        validate_input_source("non_existent_file_xyz_123.jpg")

def test_unsupported_file_extension():
    # Create a temporary txt file path for validation test
    temp_txt = Path(__file__).resolve().parent / "temp.txt"
    temp_txt.write_text("hello")
    try:
        with pytest.raises(ValueError):
            validate_input_source(temp_txt)
    finally:
        if temp_txt.exists():
            temp_txt.unlink()

def test_valid_image_input():
    test_car = Path(__file__).resolve().parent.parent / "test_car.jpg"
    if test_car.exists():
        path, input_type = validate_input_source(test_car)
        assert input_type == "image"
        img = load_image(test_car)
        assert img is not None
        assert img.size > 0
