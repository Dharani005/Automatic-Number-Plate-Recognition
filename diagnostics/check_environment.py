import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

def check_environment():
    print("=" * 60)
    print("           ANPR ENVIRONMENT DIAGNOSTIC               ")
    print("=" * 60)
    print(f"Python Version: {sys.version.split()[0]} ({sys.platform})")
    print("-" * 60)

    modules = [
        ("ultralytics", "YOLOv8 Object Detection"),
        ("paddleocr", "PaddleOCR Engine"),
        ("paddle", "PaddlePaddle Deep Learning Framework"),
        ("cv2", "OpenCV Image Processing"),
        ("mysql.connector", "MySQL Database Connector"),
        ("dotenv", "Python Environment Configuration"),
        ("pytest", "Automated Testing Framework"),
        ("PIL", "Pillow Image Library")
    ]

    all_passed = True
    for mod, desc in modules:
        try:
            m = __import__(mod)
            version = getattr(m, "__version__", "Available")
            print(f"  [OK]   {mod:<18} (v{version:<10}) - {desc}")
        except ImportError as e:
            print(f"  [FAIL] {mod:<18} - NOT INSTALLED ({e})")
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("ENVIRONMENT DIAGNOSTIC: SUCCESS (All required packages installed)")
    else:
        print("ENVIRONMENT DIAGNOSTIC: FAILED (Missing packages)")
    print("=" * 60 + "\n")
    return all_passed

if __name__ == "__main__":
    sys.exit(0 if check_environment() else 1)
