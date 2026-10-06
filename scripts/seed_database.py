"""
ANPR Database Seeder & Mock Data Generator for Power BI Dashboarding
Generates realistic license plate detection logs with realistic time distributions,
confidence scores, and plate formats to facilitate rich Power BI analytics.

Usage:
    python scripts/seed_database.py [--count 500] [--clear]
"""

import sys
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database import get_db_connection
from scripts.export_csv import export_plate_logs_to_csv

# Pool of realistic plates (mix of Indian & International formats)
SAMPLE_PLATES = [
    "TN07CD4512", "TN09BE8891", "TN01AX1234", "TN14AZ9087", "TN22DF5566",
    "MH12AB1001", "MH02CB4432", "MH01DE8765", "MH14GH9900", "MH04KL3210",
    "DL01CA1234", "DL08CJ9876", "DL03TC4567", "DL05AQ2211", "DL10XZ8822",
    "KA01MJ4321", "KA03NE7654", "KA05PB9988", "KA51QE1122", "KA04RS5544",
    "HR26DK8392", "HR51AE6543", "UP32BN7890", "KL07CR1100", "AP09CK4455",
    "SD63GXW", "GENMERCANLAR", "B777CAR", "ABC1234", "XYZ9876"
]

def generate_realistic_timestamp(days_back: int = 14) -> datetime:
    """Generates timestamps weighted towards realistic traffic hours (morning/evening rush)."""
    now = datetime.now()
    random_days = random.randint(0, days_back)
    
    # Peak traffic hours weighted higher
    hour_weights = [
        1, 1, 1, 1, 2, 4,       # 00:00 - 05:00 (Night/Early morning)
        8, 15, 25, 20, 12, 10,   # 06:00 - 11:00 (Morning Rush)
        10, 12, 11, 14, 18, 25,  # 12:00 - 17:00 (Afternoon to Evening Rush)
        22, 16, 10, 6, 4, 2      # 18:00 - 23:00 (Evening / Night)
    ]
    
    hour = random.choices(range(24), weights=hour_weights, k=1)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    
    date_val = now.date() - timedelta(days=random_days)
    return datetime.combine(date_val, datetime.min.time()) + timedelta(hours=hour, minutes=minute, seconds=second)

def seed_database(count: int = 500, clear_existing: bool = False):
    print("=" * 60)
    print(f"       ANPR DATABASE SEEDER (Generating {count} Records)       ")
    print("=" * 60)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if clear_existing:
        cursor.execute("TRUNCATE TABLE plate_logs")
        conn.commit()
        print("[Info] Truncated existing 'plate_logs' table.")
        
    insert_sql = "INSERT INTO plate_logs (plate_number, confidence, timestamp) VALUES (%s, %s, %s)"
    
    records = []
    for _ in range(count):
        # 70% chance of repeat vehicle, 30% brand new random
        if random.random() < 0.75:
            plate = random.choice(SAMPLE_PLATES)
        else:
            state = random.choice(["TN", "MH", "DL", "KA", "HR", "KL", "TS"])
            rto = f"{random.randint(1, 99):02d}"
            series = random.choice(["AB", "CD", "EF", "GH", "JK", "MN", "PQ", "RS", "XY"])
            num = f"{random.randint(1000, 9999)}"
            plate = f"{state}{rto}{series}{num}"
            
        # Confidence score distribution (mostly 85%-99.9%, few outliers)
        if random.random() < 0.85:
            confidence = round(random.uniform(0.88, 0.999), 4)
        else:
            confidence = round(random.uniform(0.60, 0.87), 4)
            
        timestamp = generate_realistic_timestamp(days_back=14)
        records.append((plate, confidence, timestamp))
        
    cursor.executemany(insert_sql, records)
    conn.commit()
    cursor.close()
    conn.close()
    
    print(f"[Success] Inserted {count} realistic ANPR detection logs into MySQL!")
    print("[Info] Updating enriched CSV for Power BI...")
    
    # Trigger CSV export immediately
    export_plate_logs_to_csv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed realistic ANPR logs for Power BI")
    parser.add_argument("--count", type=int, default=500, help="Number of records to generate (default: 500)")
    parser.add_argument("--clear", action="store_true", help="Clear existing records before seeding")
    args = parser.parse_args()
    
    seed_database(count=args.count, clear_existing=args.clear)
