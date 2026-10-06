"""
Step 3: Fine-tune YOLOv8n on the license plate dataset.

Before running:
  - Make sure data/plates/data.yaml exists and its train/val paths
    point to plates/train/images and plates/valid/images correctly.

Usage:
    python scripts/train.py
"""
from ultralytics import YOLO

def main():
    # Start from the pretrained COCO weights, then fine-tune only on
    # the "license_plate" class(es) defined in data.yaml.
    model = YOLO("yolov8n.pt")

    results = model.train(
        data="data/plates/data.yaml",
        epochs=50,
        imgsz=640,
        batch=16,
        patience=10,          # stop early if no improvement for 10 epochs
        project="models",
        name="plate_detector",
        val=True,
    )

    print("\nTraining complete.")
    print("Best weights saved at: models/plate_detector/weights/best.pt")

if __name__ == "__main__":
    main()