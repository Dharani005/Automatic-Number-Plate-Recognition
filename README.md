# Automatic Number Plate Recognition (ANPR) & Vehicle Logging System

A production-ready End-to-End Automatic Number Plate Recognition (ANPR) system featuring **YOLOv8 Detection**, **PaddleOCR Multi-Variant Recognition**, parameterized **MySQL Logging**, and rich **Power BI Business Intelligence & Surveillance Analytics**.

---

## 🚀 Key Features
- **Accurate Detection**: YOLOv8 model for detecting vehicle license plates with automatic confidence thresholds.
- **Robust OCR Recognition**: PaddleOCR integration with multi-variant image preprocessing (grayscale, contrast normalization, bilateral filtering, upscaling, sharpening).
- **Relational Storage**: MySQL parameterized logging with automatic timestamping and schema validation.
- **Power BI Integration**: Automatic 14-dimension CSV exporter and realistic synthetic dataset generator for building traffic surveillance and frequency dashboards.

---

## 📁 Project Structure
```
anpr_project/
├── config.py                 # Centralized configuration & environment loader
├── requirements.txt          # Python package dependencies
├── anpr_db.sql               # Database schema definition
├── models/
│   └── best.pt               # Trained YOLO license plate model weights
├── scripts/
│   ├── detect_and_log.py     # Main end-to-end pipeline runner
│   ├── export_csv.py         # 14-column enriched CSV exporter for Power BI
│   ├── seed_database.py      # Realistic mock traffic data generator
│   └── train.py              # YOLOv8 fine-tuning script
├── src/
│   ├── database.py           # MySQL connection and insert routines
│   ├── detector.py           # YOLO model inference wrapper
│   ├── ocr_engine.py         # PaddleOCR multi-variant recognition
│   ├── preprocessor.py       # Computer Vision image enhancement pipeline
│   └── utils.py              # Image/video loaders and geometry helpers
├── outputs/                  # Exported CSVs and diagnostic detection crops
└── tests/                    # Unit and integration test suite
```

---

## ⚙️ Quick Start

### 1. Environment Setup
```powershell
pip install -r requirements.txt
```

### 2. Configure Database
Copy `.env.example` to `.env` and configure your MySQL credentials:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=anpr_db
```

### 3. Run ANPR Pipeline on an Image or Video
```powershell
python scripts/detect_and_log.py test_car.jpg
```

### 4. Generate Data & Build Power BI Dashboard
To generate 500+ realistic traffic logs and export an enriched CSV for Power BI:
```powershell
python scripts/seed_database.py --count 500
```

