import cv2
import logging
from pathlib import Path
from typing import Union, Tuple, Optional

logger = logging.getLogger("ANPR.Utils")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

def validate_input_source(source_path: Union[str, Path]) -> Tuple[Path, str]:
    """
    Validates input file existence, resolves absolute path, and determines type ('image' or 'video').
    Raises FileNotFoundError or ValueError if invalid.
    """
    path = Path(source_path).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: '{path}' (Original string: '{source_path}')")
    
    if not path.is_file():
        raise ValueError(f"Input path is not a file: '{path}'")

    ext = path.suffix.lower()
    if ext in IMAGE_EXTENSIONS:
        return path, "image"
    elif ext in VIDEO_EXTENSIONS:
        return path, "video"
    else:
        raise ValueError(f"Unsupported file extension '{ext}' for input '{path}'. Allowed: {IMAGE_EXTENSIONS | VIDEO_EXTENSIONS}")

def load_image(image_path: Union[str, Path]):
    """
    Safely loads image using OpenCV.
    Raises ValueError if image loading fails or image is empty.
    """
    path, input_type = validate_input_source(image_path)
    if input_type != "image":
        raise ValueError(f"Expected image file, but got video file: '{path}'")

    img = cv2.imread(str(path))
    if img is None or img.size == 0:
        raise ValueError(f"cv2.imread() failed to read image at '{path}'. File may be corrupt or invalid image format.")

    logger.info(f"Successfully loaded image '{path.name}' ({img.shape[1]}x{img.shape[0]} px, {img.shape[2]} channels)")
    return img

def load_video_capture(video_path: Union[str, Path]) -> cv2.VideoCapture:
    """
    Safely opens OpenCV VideoCapture.
    Raises ValueError if VideoCapture cannot be opened.
    """
    path, input_type = validate_input_source(video_path)
    if input_type != "video":
        raise ValueError(f"Expected video file, but got image file: '{path}'")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"cv2.VideoCapture failed to open video file at '{path}'.")

    logger.info(f"Successfully opened video '{path.name}'")
    return cap
