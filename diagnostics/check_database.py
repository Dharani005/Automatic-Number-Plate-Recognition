import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import DB_HOST, DB_PORT, DB_USER, DB_NAME
from src.database import get_db_connection, ensure_schema_exists

def check_database():
    print("=" * 60)
    print("           MYSQL DATABASE CONNECTION DIAGNOSTIC       ")
    print("=" * 60)
    print(f"Target Host     : {DB_HOST}:{DB_PORT}")
    print(f"Database User   : {DB_USER}")
    print(f"Target Database : {DB_NAME}")
    print("-" * 60)

    # Step 1: Ensure Schema
    schema_ok = ensure_schema_exists()
    if not schema_ok:
        print("  [FAIL] Failed to initialize or connect to MySQL database.")
        print("=" * 60)
        print("Database Connection: FAILED")
        print("  Explanation: Check if MySQL service is running on localhost:3306 and credentials in .env are correct.")
        print("=" * 60 + "\n")
        return False

    # Step 2: Query Existing Logs Table
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM plate_logs")
        row_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        print(f"  [OK] MySQL Schema Verified: `anpr_db`.`plate_logs` table exists.")
        print(f"  [OK] Current `plate_logs` record count: {row_count}")
        print("=" * 60)
        print("Database connection: SUCCESS")
        print("=" * 60 + "\n")
        return True
    except Exception as e:
        print(f"  [FAIL] Query execution error: {e}")
        print("=" * 60)
        print("Database Connection: FAILED")
        print(f"  Explanation: {e}")
        print("=" * 60 + "\n")
        return False

if __name__ == "__main__":
    sys.exit(0 if check_database() else 1)
