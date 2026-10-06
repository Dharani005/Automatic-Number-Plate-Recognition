# ANPR & Vehicle Logging System — Starter Scaffold

## Folder structure
```
anpr_project/
├── data/
│   ├── images/       # put your dataset images here
│   └── labels/        # YOLO-format .txt labels here
├── models/             # trained/fine-tuned weights go here
├── scripts/
│   └── test_setup.py   # Step 1: sanity check
├── outputs/            # detection results, logs
└── requirements.txt
```

## Step 1 (today): confirm environment works
```bash
pip install -r requirements.txt
python scripts/test_setup.py path/to/any_car_photo.jpg
```
This uses the pretrained YOLOv8n (COCO classes) — just to prove detection,
cropping, and saving works before you touch the plate dataset.

## Step 2 (this week): get a plate dataset
Go to Roboflow Universe: https://universe.roboflow.com and search
"license plate detection". Pick a project with a few hundred+ images,
export in **YOLOv8 format**, and drop the images/labels into
`data/images/` and `data/labels/`.

## Step 3 (next): fine-tune YOLOv8 on plates
Once the dataset is in place, we'll write `scripts/train.py` to fine-tune
`yolov8n.pt` on just the "license_plate" class.

## Step 4: OCR + MySQL logging
Crop detected plates → preprocess → EasyOCR → insert (plate, timestamp)
into MySQL.

## Step 5: Power BI dashboard
Connect Power BI to the MySQL table for entry/exit frequency and alerts.