from ultralytics import YOLO

MODEL_PATH = "runs/detect/models/plate_detector-3/weights/best.pt"

model = YOLO(MODEL_PATH)
results = model.predict("test_car.jpg", conf=0.05, verbose=True)

for r in results:
    print(f"Boxes found: {len(r.boxes)}")
    for box in r.boxes:
        print(f"  confidence: {float(box.conf[0]):.3f}, coords: {box.xyxy[0].tolist()}")