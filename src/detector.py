import logging
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from ultralytics import YOLO
from config import resolve_model_path, CONFIDENCE_THRESHOLD, IOU_THRESHOLD

logger = logging.getLogger("ANPR.Detector")

class PlateDetector:
    def __init__(self, model_path: Path = None, conf: float = CONFIDENCE_THRESHOLD, iou: float = IOU_THRESHOLD):
        self.model_path = resolve_model_path(model_path)
        self.conf = conf
        self.iou = iou
        logger.info(f"Loading YOLO detector model from: {self.model_path}")
        self.model = YOLO(str(self.model_path))
        logger.info(f"YOLO model loaded successfully. Classes: {self.model.names}")

    def detect(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Runs YOLO inference on input BGR image.
        Returns list of detection dicts containing bounding box coordinates and confidence scores.
        Prints detailed diagnostic log if zero plate boxes are detected.
        """
        h, w = image.shape[:2]
        results = self.model.predict(
            source=image,
            conf=self.conf,
            iou=self.iou,
            verbose=False
        )

        detections = []
        raw_box_count = 0

        for r in results:
            raw_box_count += len(r.boxes)
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cls_id = int(box.cls[0])
                cls_name = self.model.names.get(cls_id, str(cls_id))
                conf_score = float(box.conf[0])

                # Ensure crop coordinates are strictly bound within image dimensions
                x1_clamped = max(0, min(x1, w - 1))
                y1_clamped = max(0, min(y1, h - 1))
                x2_clamped = max(0, min(x2, w))
                y2_clamped = max(0, min(y2, h))

                if x2_clamped > x1_clamped and y2_clamped > y1_clamped:
                    detections.append({
                        "bbox": (x1_clamped, y1_clamped, x2_clamped, y2_clamped),
                        "confidence": conf_score,
                        "class_id": cls_id,
                        "class_name": cls_name,
                        "crop": image[y1_clamped:y2_clamped, x1_clamped:x2_clamped]
                    })

        if len(detections) == 0:
            logger.warning(
                f"[YOLO Diagnostics] 0 plate boxes detected!\n"
                f"  - Model Path: {self.model_path}\n"
                f"  - Input Resolution: {w}x{h} px\n"
                f"  - Confidence Threshold: {self.conf}\n"
                f"  - IoU Threshold: {self.iou}\n"
                f"  - Raw Detections Found: {raw_box_count}\n"
                f"  - Model Classes: {self.model.names}\n"
                f"  Note: Undertrained models (e.g. 2 epochs) frequently miss plates. Full 50-epoch retraining recommended."
            )
        else:
            logger.info(f"YOLO detected {len(detections)} plate bounding box(es) (Conf thresh: {self.conf})")

        return detections
