import sys
import cv2
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ocr_engine import ANPROCREngine

def test_ocr(image_path: str = "debug_crop.jpg"):
    print("=" * 60)
    print("             PADDLEOCR ENGINE DIAGNOSTIC             ")
    print("=" * 60)

    try:
        path = PROJECT_ROOT / image_path if not Path(image_path).is_absolute() else Path(image_path)
        print(f"Target Crop Image : {path}")

        if not path.exists():
            print(f"  [INFO] Crop file '{path.name}' does not exist. Creating synthetic license plate test image...")
            crop = np.zeros((120, 400, 3), dtype=np.uint8) + 240
            cv2.putText(crop, "KA 01 AB 1234", (20, 75), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3)
        else:
            crop = cv2.imread(str(path))

        ocr_engine = ANPROCREngine()
        plate_text, conf, variant = ocr_engine.read_plate(crop)

        print("-" * 60)
        print(f"Extracted Text    : '{plate_text}'")
        print(f"OCR Confidence    : {conf:.2f}")
        print(f"Best Variant Used : '{variant}'")
        print("=" * 60)

        if plate_text:
            print("PADDLEOCR DIAGNOSTIC: SUCCESS (Text extracted successfully)")
            print("=" * 60 + "\n")
            return True
        else:
            print("PADDLEOCR DIAGNOSTIC: FAILED (No text extracted)")
            print("=" * 60 + "\n")
            return False

    except Exception as e:
        print(f"PADDLEOCR DIAGNOSTIC: FAILED - {e}")
        print("=" * 60 + "\n")
        return False

if __name__ == "__main__":
    crop_img = sys.argv[1] if len(sys.argv) > 1 else "debug_crop.jpg"
    test_ocr(crop_img)
