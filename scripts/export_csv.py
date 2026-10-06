"""
ANPR MySQL to CSV Exporter for Power BI & Analytics
Fetches all records from anpr_db.plate_logs and exports an enriched CSV
ready for instant Power BI import.

Usage:
    python scripts/export_csv.py
"""

import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_db_connection
from config import OUTPUT_DIR

def export_plate_logs_to_csv(output_filepath: Path = None) -> Path:
    if output_filepath is None:
        output_filepath = OUTPUT_DIR / "anpr_plate_logs.csv"

    print("=" * 60)
    print("         ANPR DATABASE TO CSV EXPORT FOR POWER BI        ")
    print("=" * 60)

    try:
        conn = get_db_connection()
        query = "SELECT id, plate_number, confidence, timestamp FROM plate_logs ORDER BY timestamp DESC"
        
        # Load directly into pandas DataFrame
        df = pd.read_sql(query, conn)
        conn.close()

        if df.empty:
            print("[Warning] No records found in 'plate_logs' table.")
            # Create template with header
            df = pd.DataFrame(columns=["id", "plate_number", "confidence", "timestamp", "date", "time", "hour", "day_name"])
            df.to_csv(output_filepath, index=False)
            print(f"[Export] Saved empty schema template to: {output_filepath}")
            return output_filepath

        # Enrich with analytics columns for Power BI
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date
        df["time"] = df["timestamp"].dt.strftime("%H:%M:%S")
        df["hour"] = df["timestamp"].dt.hour
        df["day_name"] = df["timestamp"].dt.day_name()
        df["day_type"] = df["timestamp"].dt.dayofweek.apply(lambda x: "Weekend" if x >= 5 else "Weekday")
        df["confidence_percent"] = (df["confidence"] * 100).round(2)

        # Traffic Period Categorization
        def get_traffic_period(hour):
            if 6 <= hour < 11:
                return "Morning Rush (06:00 - 11:00)"
            elif 11 <= hour < 16:
                return "Afternoon (11:00 - 16:00)"
            elif 16 <= hour < 21:
                return "Evening Rush (16:00 - 21:00)"
            else:
                return "Night (21:00 - 06:00)"

        df["traffic_period"] = df["hour"].apply(get_traffic_period)

        # Confidence Quality Tier
        def get_confidence_tier(conf):
            if conf >= 0.90:
                return "High (>=90%)"
            elif conf >= 0.75:
                return "Moderate (75-89%)"
            else:
                return "Low (<75%)"

        df["confidence_tier"] = df["confidence"].apply(get_confidence_tier)

        # State/Region Extraction (e.g. TN, MH, DL, KA)
        known_states = {"TN": "Tamil Nadu", "MH": "Maharashtra", "DL": "Delhi", "KA": "Karnataka", "HR": "Haryana", "KL": "Kerala", "AP": "Andhra Pradesh", "TS": "Telangana", "UP": "Uttar Pradesh"}
        df["state_code"] = df["plate_number"].str[:2].str.upper()
        df["state_name"] = df["state_code"].apply(lambda code: known_states.get(code, "Other / International"))


        # Ensure output directory exists
        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_filepath, index=False)

        print(f"[Success] Successfully exported {len(df)} records to:")
        print(f"          -> {output_filepath}")
        print("\nPreview of Exported Data:")
        print(df.head())
        print("=" * 60)
        return output_filepath

    except Exception as e:
        print(f"[Error] Failed to export database records to CSV: {e}")
        raise

if __name__ == "__main__":
    export_plate_logs_to_csv()
