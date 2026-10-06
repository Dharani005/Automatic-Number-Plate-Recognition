import cv2
import numpy as np
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger("ANPR.Preprocessor")

def upscale_crop(crop: np.ndarray, target_size: int = 400) -> np.ndarray:
    """Upscales small cropped plate images so OCR has sufficient pixel resolution."""
    h, w = crop.shape[:2]
    if max(h, w) < target_size:
        scale = target_size / float(max(h, w))
        resized = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        return resized
    return crop.copy()

def apply_clahe(gray: np.ndarray) -> np.ndarray:
    """Applies CLAHE (Contrast Limited Adaptive Histogram Equalization) to enhance contrast."""
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    return clahe.apply(gray)

def apply_sharpening(img: np.ndarray) -> np.ndarray:
    """Applies high-pass sharpening filter matrix."""
    kernel = np.array([[0, -1, 0],
                       [-1, 5, -1],
                       [0, -1, 0]], dtype=np.float32)
    return cv2.filter2D(img, -1, kernel)

def generate_preprocessing_variants(crop: np.ndarray) -> List[Dict[str, np.ndarray]]:
    """
    Generates multiple preprocessed variants for OCR evaluation:
    1. Upscaled Original BGR
    2. Grayscale + CLAHE
    3. Grayscale + Otsu Binarization
    4. Sharpened BGR
    """
    if crop is None or crop.size == 0:
        return []

    # Variant 1: Upscaled BGR
    upscaled = upscale_crop(crop, target_size=450)

    # Convert upscaled to Grayscale
    gray = cv2.cvtColor(upscaled, cv2.COLOR_BGR2GRAY)
    filtered = cv2.bilateralFilter(gray, 11, 17, 17)

    # Variant 2: CLAHE Enhanced Grayscale (converted to 3-channel for OCR engine)
    clahe_gray = apply_clahe(filtered)
    clahe_bgr = cv2.cvtColor(clahe_gray, cv2.COLOR_GRAY2BGR)

    # Variant 3: Otsu Thresholding
    _, otsu_thresh = cv2.threshold(filtered, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_bgr = cv2.cvtColor(otsu_thresh, cv2.COLOR_GRAY2BGR)

    # Variant 4: Sharpened
    sharpened = apply_sharpening(upscaled)

    variants = [
        {"name": "upscaled_bgr", "image": upscaled},
        {"name": "clahe_enhanced", "image": clahe_bgr},
        {"name": "otsu_threshold", "image": otsu_bgr},
        {"name": "sharpened_bgr", "image": sharpened},
    ]

    logger.debug(f"Generated {len(variants)} preprocessing variants for OCR candidate evaluation.")
    return variants
