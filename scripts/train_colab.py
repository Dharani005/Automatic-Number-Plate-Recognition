"""
Google Colab GPU Retraining Script for YOLOv8 License Plate Detector
=====================================================================

Instructions:
1. Open Google Colab (https://colab.research.google.com).
2. Set Runtime -> Change runtime type -> T4 GPU.
3. Zip your `data/plates` folder locally and upload `plates.zip` to Colab.
4. Execute the cells below to run full 50-epoch training on GPU (~5-10 minutes).
5. Download the output `best.pt` model file and place it in your local
   `runs/detect/models/plate_detector-3/weights/best.pt`.
"""

# Cell 1: Environment Setup
"""
!pip install ultralytics opencv-python pyyaml
"""

# Cell 2: Extract Dataset
"""
import zipfile
import os

with zipfile.ZipFile("plates.zip", "r") as zip_ref:
    zip_ref.extractall("data")

print("Dataset extracted successfully to data/plates/")
"""

# Cell 3: Create YAML File on Colab
"""
data_yaml_content = '''
train: /content/data/plates/train/images
val: /content/data/plates/valid/images
test: /content/data/plates/test/images

nc: 1
names: ['license_plate']
'''

with open("/content/data/plates/data.yaml", "w") as f:
    f.write(data_yaml_content)

print("data.yaml updated with absolute Colab paths.")
"""

# Cell 4: Train YOLOv8 Model on GPU (50 Epochs)
"""
from ultralytics import YOLO

# Load base YOLOv8 nano model
model = YOLO("yolov8n.pt")

# Run 50 epochs training on GPU (device=0)
results = model.train(
    data="/content/data/plates/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    patience=10,
    project="runs/detect",
    name="colab_plate_detector",
    device=0,
    val=True
)

print("Training Complete!")
print("Best weights saved at: /content/runs/detect/colab_plate_detector/weights/best.pt")
"""

# Cell 5: Download Trained Weights to Local Machine
"""
from google.colab import files
files.download("/content/runs/detect/colab_plate_detector/weights/best.pt")
"""
