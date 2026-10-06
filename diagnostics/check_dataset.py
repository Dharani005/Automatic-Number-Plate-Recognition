import sys
import yaml
import cv2
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def audit_dataset_split(split_name: str, split_dir: Path):
    images_dir = split_dir / "images"
    labels_dir = split_dir / "labels"

    print(f"\n--- Auditing '{split_name}' Split ({split_dir}) ---")

    if not images_dir.exists():
        print(f"  [FAIL] Missing images directory: {images_dir}")
        return False, 0, 0
    if not labels_dir.exists():
        print(f"  [FAIL] Missing labels directory: {labels_dir}")
        return False, 0, 0

    image_files = list(images_dir.glob("*.*"))
    label_files = list(labels_dir.glob("*.txt"))

    print(f"  Images Found : {len(image_files)}")
    print(f"  Labels Found : {len(label_files)}")

    corrupt_images = 0
    invalid_labels = 0
    out_of_bounds = 0
    empty_labels = 0

    for img_path in image_files:
        # Check image readability
        img = cv2.imread(str(img_path))
        if img is None or img.size == 0:
            corrupt_images += 1

        # Check matching label
        label_path = labels_dir / f"{img_path.stem}.txt"
        if label_path.exists():
            with open(label_path, "r") as f:
                lines = f.readlines()
            if len(lines) == 0:
                empty_labels += 1
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    invalid_labels += 1
                    continue
                try:
                    cls_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])
                    if not (0.0 <= x_center <= 1.0 and 0.0 <= y_center <= 1.0 and 0.0 <= width <= 1.0 and 0.0 <= height <= 1.0):
                        out_of_bounds += 1
                except ValueError:
                    invalid_labels += 1

    print(f"  Corrupt Images      : {corrupt_images}")
    print(f"  Empty Label Files   : {empty_labels}")
    print(f"  Invalid Label Lines : {invalid_labels}")
    print(f"  Out of Bounds Box   : {out_of_bounds}")

    is_valid = (corrupt_images == 0 and invalid_labels == 0 and out_of_bounds == 0 and len(image_files) > 0)
    return is_valid, len(image_files), len(label_files)

def check_dataset():
    print("=" * 60)
    print("            YOLO DATASET INTEGRITY DIAGNOSTIC         ")
    print("=" * 60)

    dataset_yaml = PROJECT_ROOT / "data" / "plates" / "data.yaml"
    if not dataset_yaml.exists():
        print(f"DATASET DIAGNOSTIC: FAILED - Missing data.yaml at {dataset_yaml}")
        return False

    with open(dataset_yaml, "r") as f:
        data_config = yaml.safe_load(f)

    print(f"Dataset YAML Config : {dataset_yaml}")
    print(f"Class Count (nc)    : {data_config.get('nc')}")
    print(f"Class Names         : {data_config.get('names')}")

    data_dir = dataset_yaml.parent
    train_valid, n_train_img, _ = audit_dataset_split("Train", data_dir / "train")
    val_valid, n_val_img, _ = audit_dataset_split("Validation", data_dir / "valid")
    test_valid, n_test_img, _ = audit_dataset_split("Test", data_dir / "test")

    total_images = n_train_img + n_val_img + n_test_img
    print("-" * 60)
    print(f"Total Dataset Images : {total_images} (Train: {n_train_img}, Val: {n_val_img}, Test: {n_test_img})")

    overall_valid = train_valid and val_valid
    print("=" * 60)
    if overall_valid:
        print("DATASET DIAGNOSTIC: SUCCESS (Dataset structure and labels valid)")
    else:
        print("DATASET DIAGNOSTIC: FAILED (Errors detected in dataset)")
    print("=" * 60 + "\n")
    return overall_valid

if __name__ == "__main__":
    sys.exit(0 if check_dataset() else 1)
