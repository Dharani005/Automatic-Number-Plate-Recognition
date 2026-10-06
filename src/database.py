import mysql.connector
from mysql.connector import Error
import logging
from datetime import datetime
from typing import Tuple, Optional
from config import DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

logger = logging.getLogger("ANPR.Database")

def get_db_connection():
    """
    Creates and returns a MySQL database connection using configured environment credentials.
    Never prints or logs the database password.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            connect_timeout=5
        )
        return conn
    except Error as e:
        logger.error(f"MySQL Connection Failed: Host='{DB_HOST}', User='{DB_USER}', Database='{DB_NAME}' | Error: {e}")
        raise

def ensure_schema_exists() -> bool:
    """
    Ensures that the anpr_db database and plate_logs table exist.
    Creates them if missing.
    """
    try:
        # Initial connection without database to create DB if needed
        conn = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`")
        cursor.execute(f"USE `{DB_NAME}`")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS plate_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plate_number VARCHAR(20) NOT NULL,
                confidence FLOAT NOT NULL,
                timestamp DATETIME NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Database schema check completed successfully for '{DB_NAME}.plate_logs'.")
        return True
    except Error as e:
        logger.error(f"Failed to ensure database schema existence: {e}")
        return False

def insert_plate_log(plate_number: str, confidence: float, timestamp: Optional[datetime] = None) -> Tuple[bool, Optional[int]]:
    """
    Inserts a detected license plate log into MySQL plate_logs using parameterized query.
    Returns (success_boolean, inserted_row_id)
    """
    if not plate_number:
        logger.warning("Attempted to insert empty plate_number into database. Skipped.")
        return False, None

    if timestamp is None:
        timestamp = datetime.now()

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO plate_logs (plate_number, confidence, timestamp) VALUES (%s, %s, %s)"
        params = (plate_number, float(confidence), timestamp)
        cursor.execute(query, params)
        conn.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        conn.close()
        logger.info(f"Successfully inserted plate log into MySQL: ID={inserted_id}, Plate='{plate_number}', Conf={confidence:.2f}, Time={timestamp}")
        return True, inserted_id
    except Error as e:
        logger.error(f"MySQL Insert Failed for plate '{plate_number}': {e}")
        if conn and conn.is_connected():
            conn.close()
        return False, None
