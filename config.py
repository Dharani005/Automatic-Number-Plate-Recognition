import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Base Project Root
PROJECT_ROOT = Path(__file__).resolve().parent

# Load .env file
env_path = PROJECT_ROOT / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Logging Configuration
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_STR, logging.INFO)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("ANPR.Config")

# Database Credentials
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "anpr_db")

# Model Thresholds
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.25"))
IOU_THRESHOLD = float(os.getenv("IOU_THRESHOLD", "0.45"))
SAVE_DEBUG_IMAGES = os.getenv("SAVE_DEBUG_IMAGES", "true").lower() == "true"

# Output Directory
OUTPUT_DIR = PROJECT_ROOT / os.getenv("OUTPUT_DIR", "outputs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def resolve_model_path(env_model_path: str = None) -> Path:
    """
    Robust pathlib resolution for YOLO best.pt weights.
    Prioritizes:
    1. Explicit env_model_path if provided and exists.
    2. MODEL_PATH from .env if exists.
    3. Fine-tuned runs directory (runs/detect/models/*/weights/best.pt).
    4. Root models/best.pt.
    """
    candidates = []

    if env_model_path:
        candidates.append(Path(env_model_path))

    configured_path = os.getenv("MODEL_PATH")
    if configured_path:
        p = Path(configured_path)
        candidates.append(p if p.is_absolute() else PROJECT_ROOT / p)

    # Search runs folder for recent best.pt
    runs_dir = PROJECT_ROOT / "runs" / "detect" / "models"
    if runs_dir.exists():
        for run_best in sorted(runs_dir.glob("**/weights/best.pt"), reverse=True):
            candidates.append(run_best)

    # Base models directory candidate
    candidates.append(PROJECT_ROOT / "models" / "best.pt")

    for cand in candidates:
        if cand.exists() and cand.is_file():
            # Ensure it's not a tiny base/truncated file if a larger trained weight exists
            size_mb = cand.stat().st_size / (1024 * 1024)
            logger.info(f"Resolved YOLO model path: {cand} (Size: {size_mb:.2f} MB)")
            return cand

    raise FileNotFoundError(
        f"No valid YOLO model weights found! Tested candidates: {[str(c) for c in candidates]}"
    )
