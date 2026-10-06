import os
# Disable oneDNN PIR flags to prevent Windows CPU execution crash in Paddle paddle
os.environ["FLAGS_use_mkldnn"] = "0"
os.environ["FLAGS_enable_pir_api"] = "0"

import re
import torch  # Prevents shm.dll load error on Windows Python builds
import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Optional, Tuple
from paddleocr import PaddleOCR
from src.preprocessor import generate_preprocessing_variants

logger = logging.getLogger("ANPR.OCREngine")

def normalize_plate_text(raw_text: str) -> Tuple[str, bool]:
    """
    Normalizes license plate text:
    1. Converts to uppercase.
    2. Strips spaces and non-alphanumeric characters.
    3. Validates length and character composition.
    Returns (normalized_text, is_valid)
    """
    if not raw_text:
        return "", False

    # Standard upper-case conversion
    text = raw_text.strip().upper()

    # Remove non-alphanumeric noise (symbols, hyphens, periods)
    text = re.sub(r'[^A-Z0-9]', '', text)

    if len(text) < 3 or len(text) > 13:
        return text, False

    # Check if final text has valid alphanumeric structure
    is_valid = bool(re.match(r'^[A-Z0-9]{3,13}$', text))
    return text, is_valid


def parse_ocr_result(raw_result: Any) -> List[Dict[str, Any]]:
    """
    Safely parses PaddleOCR outputs across different API versions.
    Handles:
    - New Paddlex .predict() / .ocr() dict structure with 'rec_texts' and 'rec_scores'
    - Legacy nested list format [[[box], (text, conf)], ...]
    - Empty / None OCR outputs
    Returns list of dicts: [{"text": str, "confidence": float, "box": ...}]
    """
    parsed = []
    if raw_result is None:
        return parsed

    try:
        if isinstance(raw_result, list):
            for item in raw_result:
                if isinstance(item, dict):
                    texts = item.get("rec_texts", [])
                    scores = item.get("rec_scores", [])
                    boxes = item.get("rec_boxes", item.get("rec_polys", []))
                    for idx, (t, s) in enumerate(zip(texts, scores)):
                        b = boxes[idx] if idx < len(boxes) else None
                        parsed.append({
                            "text": str(t),
                            "confidence": float(s),
                            "box": b
                        })
                elif isinstance(item, list):
                    # Legacy PaddleOCR format: item = [box_points, (text_str, conf_float)]
                    # Check if item has 2 elements and item[1] is a tuple/list (text, conf)
                    if len(item) == 2 and isinstance(item[1], (tuple, list)) and len(item[1]) == 2:
                        box = item[0]
                        text, conf = item[1]
                        parsed.append({
                            "text": str(text),
                            "confidence": float(conf),
                            "box": box
                        })
                    else:
                        for entry in item:
                            if isinstance(entry, dict):
                                texts = entry.get("rec_texts", [])
                                scores = entry.get("rec_scores", [])
                                for t, s in zip(texts, scores):
                                    parsed.append({"text": str(t), "confidence": float(s), "box": None})
                            elif isinstance(entry, list) and len(entry) == 2 and isinstance(entry[1], (tuple, list)):
                                parsed.append({"text": str(entry[1][0]), "confidence": float(entry[1][1]), "box": entry[0]})
        elif isinstance(raw_result, dict):
            texts = raw_result.get("rec_texts", [])
            scores = raw_result.get("rec_scores", [])
            boxes = raw_result.get("rec_boxes", [])
            for idx, (t, s) in enumerate(zip(texts, scores)):
                b = boxes[idx] if idx < len(boxes) else None
                parsed.append({
                    "text": str(t),
                    "confidence": float(s),
                    "box": b
                })
    except Exception as e:
        logger.warning(f"Error parsing raw OCR result: {e}")

    return parsed


class ANPROCREngine:
    def __init__(self, lang: str = "en", enable_mkldnn: bool = False):
        logger.info(f"Initializing PaddleOCR Engine (lang='{lang}', enable_mkldnn={enable_mkldnn})...")
        self.reader = PaddleOCR(lang=lang, enable_mkldnn=enable_mkldnn)
        logger.info("PaddleOCR Engine initialized successfully.")

    def read_plate(self, crop: np.ndarray) -> Tuple[Optional[str], float, str]:
        """
        Runs multi-variant OCR preprocessing evaluation on cropped plate image.
        Evaluates 4 variant crops (Upscaled, CLAHE, Otsu, Sharpened) and picks best
        result based on combined confidence and plate text validity score.

        Returns (best_plate_text, best_confidence, selected_variant_name)
        """
        variants = generate_preprocessing_variants(crop)
        if not variants:
            return None, 0.0, "none"

        best_text = None
        best_conf = 0.0
        best_variant = "none"

        for var in variants:
            var_name = var["name"]
            var_img = var["image"]

            raw_ocr = self.reader.ocr(var_img)
            parsed_entries = parse_ocr_result(raw_ocr)

            for entry in parsed_entries:
                raw_text = entry["text"]
                conf = entry["confidence"]
                norm_text, is_valid = normalize_plate_text(raw_text)

                if norm_text and is_valid:
                    score = conf * 1.2 if is_valid else conf
                    if score > best_conf:
                        best_conf = float(conf)
                        best_text = norm_text
                        best_variant = var_name
                elif norm_text and not best_text:
                    if conf > best_conf:
                        best_conf = float(conf)
                        best_text = norm_text
                        best_variant = var_name

        logger.info(f"OCR Multi-Variant Best Result: '{best_text}' (Conf: {best_conf:.2f}, Variant: '{best_variant}')")
        return best_text, best_conf, best_variant
