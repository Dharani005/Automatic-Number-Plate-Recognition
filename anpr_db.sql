CREATE DATABASE IF NOT EXISTS anpr_db;
USE anpr_db;

CREATE TABLE IF NOT EXISTS plate_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plate_number VARCHAR(20) NOT NULL,
    confidence FLOAT NOT NULL,
    timestamp DATETIME NOT NULL
);

SELECT 
    id,
    plate_number,
    confidence,
    ROUND(confidence * 100, 1) AS confidence_pct,
    timestamp,
    DATE(timestamp) AS log_date,
    TIME(timestamp) AS log_time,
    HOUR(timestamp) AS log_hour,
    DAYNAME(timestamp) AS day_of_week,
    CASE 
        WHEN plate_number IN ('DL 3C AB 9012', 'MH 04 AB 0001') THEN 'Flagged'
        WHEN plate_number LIKE '%KA%' OR plate_number LIKE '%MH%' THEN 'Authorized'
        ELSE 'Visitor'
    END AS vehicle_status,
    CASE 
        WHEN id % 2 = 0 THEN 'Gate 01'
        ELSE 'Gate 02'
    END AS gate_id,
    CASE 
        WHEN confidence >= 0.95 THEN '>95% High'
        WHEN confidence >= 0.85 THEN '85-95% Medium'
        ELSE '<85% Low'
    END AS confidence_bracket
FROM anpr_db.plate_logs;
