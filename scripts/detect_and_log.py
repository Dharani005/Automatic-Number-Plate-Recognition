"""
ANPR End-to-End Pipeline Runner
Steps:
1. Input Loading & Verification
2. YOLO Plate Detection (with zero-detection diagnostics)
3. Multi-Variant Preprocessing
4. PaddleOCR Text Recognition & Normalization
5. Parameterized MySQL Logging
6. Comprehensive Step-by-Step Status Reporting

Usage:
    python scripts/detect_and_log.py path/to/image_or_video.jpg
"""

import sys
import os
import cv2
import logging
from pathlib import Path
from datetime import datetime

# Set Paddle environment variables before importing paddle components
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import PROJECT_ROOT, SAVE_DEBUG_IMAGES, OUTPUT_DIR
from src.utils import validate_input_source, load_image, load_video_capture
from src.detector import PlateDetector
from src.ocr_engine import ANPROCREngine
from src.database import ensure_schema_exists, insert_plate_log
from scripts.export_csv import export_plate_logs_to_csv

logger = logging.getLogger("ANPR.MainPipeline")

def process_single_frame(frame, detector: PlateDetector, ocr_engine: ANPROCREngine):
    """
    Processes a single frame/image through Detection, Preprocessing, and OCR.
    Returns list of processed plate results.
    """
    detections = detector.detect(frame)
    results = []

    for idx, det in enumerate(detections):
        crop = det["crop"]
        conf_yolo = det["confidence"]
        
        if SAVE_DEBUG_IMAGES:
            cv2.imwrite(str(OUTPUT_DIR / f"debug_crop_{idx}.jpg"), crop)

        plate_text, ocr_conf, variant_used = ocr_engine.read_plate(crop)

        results.append({
            "bbox": det["bbox"],
            "yolo_conf": conf_yolo,
            "plate_text": plate_text,
            "ocr_conf": ocr_conf,
            "variant_used": variant_used,
            "crop": crop
        })

    return results

def run_pipeline(source_path: str):
    print("=" * 60)
    print("         ANPR END-TO-END PIPELINE EXECUTION          ")
    print("=" * 60)

    pipeline_status = {
        "Input": "FAILED",
        "Detection": "SKIPPED",
        "OCR": "SKIPPED",
        "Database": "SKIPPED",
        "Overall": "FAILED"
    }

    # STEP 1: Input Loading & Verification
    try:
        validated_path, input_type = validate_input_source(source_path)
        pipeline_status["Input"] = "SUCCESS"
        print(f"[Input Verification] SUCCESS: Loaded {input_type.upper()} file at '{validated_path}'")
    except Exception as e:
        print(f"[Input Verification] FAILED: {e}")
        print_summary(pipeline_status)
        return False

    # STEP 2: YOLO Model Detector Initialization
    try:
        detector = PlateDetector()
        pipeline_status["Detection"] = "PENDING"
    except Exception as e:
        print(f"[YOLO Initialization] FAILED: {e}")
        pipeline_status["Detection"] = "FAILED"
        print_summary(pipeline_status)
        return False

    # STEP 3: OCR Engine Initialization
    try:
        ocr_engine = ANPROCREngine()
        pipeline_status["OCR"] = "PENDING"
    except Exception as e:
        print(f"[OCR Engine Initialization] FAILED: {e}")
        pipeline_status["OCR"] = "FAILED"
        print_summary(pipeline_status)
        return False

    # STEP 4: Database Connection Check
    db_available = ensure_schema_exists()

    # STEP 5: Execution Flow
    logged_records = 0

    if input_type == "image":
        frame = load_image(validated_path)
        frame_results = process_single_frame(frame, detector, ocr_engine)

        if len(frame_results) > 0:
            pipeline_status["Detection"] = "SUCCESS"
        else:
            pipeline_status["Detection"] = "FAILED (0 Boxes Detected)"
            print_summary(pipeline_status)
            return False

        ocr_found = False
        for res in frame_results:
            plate_text = res["plate_text"]
            ocr_conf = res["ocr_conf"]
            if plate_text:
                ocr_found = True
                print(f"[OCR Result] Plate: '{plate_text}' | OCR Conf: {ocr_conf:.2f} | Variant: {res['variant_used']}")
                
                if db_available:
                    success, row_id = insert_plate_log(plate_text, ocr_conf)
                    if success:
                        logged_records += 1

        if ocr_found:
            pipeline_status["OCR"] = "SUCCESS"
        else:
            pipeline_status["OCR"] = "FAILED (No text extracted)"

        if logged_records > 0:
            pipeline_status["Database"] = "SUCCESS"
            pipeline_status["Overall"] = "SUCCESS"
        else:
            if not db_available:
                pipeline_status["Database"] = "FAILED (Database Connection Unavailable)"
            else:
                pipeline_status["Database"] = "FAILED (No records inserted)"
            pipeline_status["Overall"] = "FAILED"

    elif input_type == "video":
        cap = load_video_capture(validated_path)
        frame_count = 0
        total_detections = 0

        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_count += 1
            if frame_count % 5 != 0:
                continue

            frame_results = process_single_frame(frame, detector, ocr_engine)
            if len(frame_results) > 0:
                total_detections += len(frame_results)
                pipeline_status["Detection"] = "SUCCESS"

            for res in frame_results:
                plate_text = res["plate_text"]
                ocr_conf = res["ocr_conf"]
                if plate_text:
                    pipeline_status["OCR"] = "SUCCESS"
                    if db_available:
                        success, row_id = insert_plate_log(plate_text, ocr_conf)
                        if success:
                            logged_records += 1

        cap.release()

        if logged_records > 0:
            pipeline_status["Database"] = "SUCCESS"
            pipeline_status["Overall"] = "SUCCESS"
        else:
            pipeline_status["Database"] = "FAILED"
            pipeline_status["Overall"] = "FAILED"

    if logged_records > 0:
        try:
            export_plate_logs_to_csv()
        except Exception as e:
            logger.warning(f"Could not auto-export CSV: {e}")

    print_summary(pipeline_status, logged_records)
    return pipeline_status["Overall"] == "SUCCESS"

def print_summary(status: dict, logged_count: int = 0):
    print("\n" + "=" * 60)
    print("                 PIPELINE STATUS SUMMARY             ")
    print("=" * 60)
    print(f"  Input Verification : {status['Input']}")
    print(f"  Plate Detection    : {status['Detection']}")
    print(f"  OCR Recognition    : {status['OCR']}")
    print(f"  Database Insertion : {status['Database']}")
    print(f"  Records Logged     : {logged_count}")
    print("-" * 60)
    print(f"  OVERALL RESULT     : {status['Overall']}")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/detect_and_log.py <path_to_image_or_video>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    success = run_pipeline(input_file)
    sys.exit(0 if success else 1)