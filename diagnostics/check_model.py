import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import resolve_model_path
from ultralytics import YOLO

def check_model():
    print("=" * 60)
    print("             YOLO MODEL DIAGNOSTIC                  ")
    print("=" * 60)

    try:
        model_path = resolve_model_path()
        print(f"Resolved Model Path : {model_path}")
        file_size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"Model File Size     : {file_size_mb:.2f} MB")
        
        if file_size_mb < 10.0:
            print("  [WARNING] File size < 10MB indicates a base/un-trained model or lightweight placeholder.")

        # Load YOLO model
        model = YOLO(str(model_path))
        print(f"YOLO Architecture   : {model.task}")
        print(f"Model Class Names   : {model.names}")
        print("-" * 60)

        # Check training history if results.csv exists nearby
        results_csv = model_path.parent.parent / "results.csv"
        if results_csv.exists():
            with open(results_csv, "r") as f:
                lines = f.readlines()
            epoch_count = max(0, len(lines) - 1)
            print(f"Training History    : {epoch_count} epoch(s) logged in {results_csv.name}")
            if epoch_count < 10:
                print("  ⚠️ MODEL STATUS: CODE FIXED — MODEL RETRAINING REQUIRED")
                print("     (Model was only trained for 2 epochs; 50 epochs recommended for reliable detection)")
        else:
            print("Training History    : No results.csv log found in model directory.")

        print("=" * 60)
        print("YOLO MODEL DIAGNOSTIC: SUCCESS (Model weights verified & loadable)")
        print("=" * 60 + "\n")
        return True
    except Exception as e:
        print(f"YOLO MODEL DIAGNOSTIC: FAILED - {e}")
        print("=" * 60 + "\n")
        return False

if __name__ == "__main__":
    sys.exit(0 if check_model() else 1)
