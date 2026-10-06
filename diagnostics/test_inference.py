import sys
import cv2
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils import load_image
from src.detector import PlateDetector

def test_inference(image_path: str = "test_car.jpg"):
    print("=" * 60)
    print("             YOLO INFERENCE DIAGNOSTIC               ")
    print("=" * 60)

    try:
        img_path = PROJECT_ROOT / image_path if not Path(image_path).is_absolute() else Path(image_path)
        print(f"Target Image Path : {img_path}")

        image = load_image(img_path)
        detector = PlateDetector()

        detections = detector.detect(image)
        print("-" * 60)
        print(f"Detections Found  : {len(detections)}")

        for idx, det in enumerate(detections):
            bbox = det["bbox"]
            conf = det["confidence"]
            cls_name = det["class_name"]
            print(f"  Box [{idx+1}]: {cls_name} @ {bbox} | Confidence: {conf:.3f}")

        print("=" * 60)
        if len(detections) > 0:
            print("YOLO INFERENCE DIAGNOSTIC: SUCCESS (Bounding boxes detected)")
        else:
            print("YOLO INFERENCE DIAGNOSTIC: WARNING (0 plate boxes detected with current weights)")
            print("  Note: Retraining model for 50 epochs on GPU will resolve weak detection accuracy.")
        print("=" * 60 + "\n")
        return len(detections) > 0
    except Exception as e:
        print(f"YOLO INFERENCE DIAGNOSTIC: FAILED - {e}")
        print("=" * 60 + "\n")
        return False

if __name__ == "__main__":
    test_img = sys.argv[1] if len(sys.argv) > 1 else "test_car.jpg"
    test_inference(test_img)
