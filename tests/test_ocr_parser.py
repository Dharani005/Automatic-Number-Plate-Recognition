import pytest
from src.ocr_engine import normalize_plate_text, parse_ocr_result

def test_normalize_plate_text():
    # Test whitespace and lowercase
    text, valid = normalize_plate_text(" ka 01 ab 1234 ")
    assert text == "KA01AB1234"
    assert valid is True

    # Test alphanumeric normalization
    text2, valid2 = normalize_plate_text("KA-01-AB-1234")
    assert text2 == "KA01AB1234"
    assert valid2 is True

    # Test short invalid string
    text3, valid3 = normalize_plate_text("A")
    assert valid3 is False

    # Test empty string
    text4, valid4 = normalize_plate_text("")
    assert text4 == ""
    assert valid4 is False

def test_parse_ocr_result_format_dict():
    raw_dict = [{
        "rec_texts": ["KA01AB1234", "TR"],
        "rec_scores": [0.95, 0.88],
        "rec_boxes": [[[10, 10], [100, 10], [100, 50], [10, 50]]]
    }]
    parsed = parse_ocr_result(raw_dict)
    assert len(parsed) == 2
    assert parsed[0]["text"] == "KA01AB1234"
    assert parsed[0]["confidence"] == 0.95

def test_parse_ocr_result_legacy_list():
    raw_list = [[ [ [10,10], [100,10], [100,50], [10,50] ], ("MH12DE1432", 0.91) ]]
    parsed = parse_ocr_result(raw_list)
    assert len(parsed) == 1
    assert parsed[0]["text"] == "MH12DE1432"
    assert parsed[0]["confidence"] == 0.91

def test_parse_ocr_result_empty():
    assert parse_ocr_result(None) == []
    assert parse_ocr_result([]) == []
