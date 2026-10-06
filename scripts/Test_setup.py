"""
Step 1 sanity check.
Run this on any car photo (jpg/png) to confirm your environment works
before you start fine-tuning on a plate-detection dataset.

Usage:
    python scripts/test_setup.py path/to/your_car_image.jpg
"""
import sys
from ultralytics import YOLO

def main(image_path: str):
    # Pretrained COCO model — detects cars/buses/trucks/persons out of the box.
    # We're only using this to confirm the pipeline runs end-to-end.
    model = YOLO("yolov8n.pt")

    results = model.predict(source=image_path, conf=0.4, save=True, project="outputs", name="test_run")

    for r in results:
        print(f"Detected {len(r.boxes)} objects:")
        for box in r.boxes:
            cls_name = model.names[int(box.cls[0])]
            conf = float(box.conf[0])
            print(f"  - {cls_name} (confidence: {conf:.2f})")

    print("\nAnnotated image saved under outputs/test_run/")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/test_setup.py <image_path>")
        sys.exit(1)
    main(sys.argv[1])