import pytest
from pathlib import Path
from config import PROJECT_ROOT, resolve_model_path, CONFIDENCE_THRESHOLD

def test_project_root_exists():
    assert PROJECT_ROOT.exists()
    assert PROJECT_ROOT.is_dir()

def test_model_path_resolution():
    model_path = resolve_model_path()
    assert model_path.exists()
    assert model_path.is_file()
    assert model_path.suffix == ".pt"

def test_confidence_threshold_type():
    assert isinstance(CONFIDENCE_THRESHOLD, float)
    assert 0.0 <= CONFIDENCE_THRESHOLD <= 1.0
