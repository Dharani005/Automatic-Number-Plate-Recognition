# 🚗 ANPR & Vehicle Traffic Analytics Dashboard Guide

This guide provides the complete blueprint, layout reference, SQL queries, DAX formulas, and visual configurations to build the **Automatic Number Plate Recognition (ANPR) & Vehicle Logging Power BI Dashboard**.

---

## 🎨 Dashboard Design Reference

![ANPR & Vehicle Analytics Power BI Dashboard](C:/Users/ELCOT/.gemini/antigravity-ide/brain/48333b05-7568-4cc0-9fac-45b027eb5c9a/anpr_powerbi_dashboard_1791117751324.jpg)

---

## 🛠️ Step 1: Connect Power BI to the ANPR Database

### Option A: Direct MySQL Connection (Select the Analytics View)
1. In **Power BI Desktop**, click **Get Data** → **MySQL database**.
2. Enter your connection settings:
   - **Server**: `localhost:3306` (or `127.0.0.1`)
   - **Database**: `anpr_db`
   - **Data Connectivity mode**: Select **Import** (or **DirectQuery** for real-time streaming updates).
3. Under **Database Credentials**, enter your MySQL user (`root`) and password.
4. In the **Navigator** window, you will see two objects:
   - ❌ `plate_logs` (Raw storage table: only contains the 4 physical columns `id`, `plate_number`, `confidence`, `timestamp`).
   - ✅ **`v_plate_analytics`** (Enriched Analytics View: **contains all 12 columns** including `gate_id`, `vehicle_status`, `confidence_bracket`, `log_hour`, `log_date`, `day_of_week`).
5. **Select `v_plate_analytics`** and click **Load**.

---

### Option B: If You Already Imported `plate_logs` (Add DAX Calculated Columns)
If you already imported the raw `plate_logs` table, you can add `gate_id`, `vehicle_status`, `log_hour`, and `confidence_bracket` as **Calculated Columns** in Power BI (click **Table Tools** → **New Column**):

1. **Gate ID**:
   ```dax
   gate_id = IF(MOD(plate_logs[id], 2) = 0, "Gate 01", "Gate 02")
   ```

2. **Vehicle Status**:
   ```dax
   vehicle_status = 
   SWITCH(
       TRUE(),
       plate_logs[plate_number] IN {"DL 3C AB 9012", "MH 04 AB 0001", "GENMERCANLAR"}, "Flagged",
       SEARCH("KA", plate_logs[plate_number], 1, 0) > 0 || 
       SEARCH("MH", plate_logs[plate_number], 1, 0) > 0 || 
       SEARCH("TN", plate_logs[plate_number], 1, 0) > 0, "Authorized",
       "Visitor"
   )
   ```

3. **Log Hour (0 to 23)**:
   ```dax
   log_hour = HOUR(plate_logs[timestamp])
   ```

4. **Log Date**:
   ```dax
   log_date = DATEVALUE(plate_logs[timestamp])
   ```

5. **Day of Week**:
   ```dax
   day_of_week = FORMAT(plate_logs[timestamp], "dddd")
   ```

6. **Confidence Percentage**:
   ```dax
   confidence_pct = plate_logs[confidence] * 100
   ```

7. **Confidence Bracket**:
   ```dax
   confidence_bracket = 
   SWITCH(
       TRUE(),
       plate_logs[confidence] >= 0.95, ">95% High",
       plate_logs[confidence] >= 0.85, "85-95% Medium",
       "<85% Low"
   )
   ```

---

### Option C: Import Enriched CSV (17 Pre-calculated Columns)
1. Run `python scripts/export_csv.py` (or `python scripts/seed_database.py --count 500`).
2. In Power BI, click **Get Data** → **Text/CSV** → choose `outputs/anpr_plate_logs.csv`.
3. Click **Load** to instantly access all 17 pre-computed analytical dimensions.

---

## 📐 Step 2: Data Model & DAX Measures

Create a new **Measures Table** in Power BI (`_Measures`) and add the following DAX calculations:

### 1. Total Detections
```dax
Total Detections = COUNTROWS(plate_logs)
```

### 2. Unique Number Plates
```dax
Unique Plates = DISTINCTCOUNT(plate_logs[plate_number])
```

### 3. Average OCR Accuracy
```dax
Avg OCR Accuracy = 
VAR AvgConf = AVERAGE(plate_logs[confidence])
RETURN
FORMAT(AvgConf, "0.0%")
```

### 4. Peak Traffic Hour
```dax
Peak Hour = 
VAR HourlySummary = 
    SUMMARIZE(
        plate_logs,
        plate_logs[log_hour],
        "VehicleCount", COUNT(plate_logs[id])
    )
VAR MaxCount = MAXX(HourlySummary, [VehicleCount])
VAR TopHour = 
    SELECTCOLUMNS(
        FILTER(HourlySummary, [VehicleCount] = MaxCount),
        "Hour", plate_logs[log_hour]
    )
VAR SingleHour = MINX(TopHour, [Hour])
RETURN
FORMAT(TIME(SingleHour, 0, 0), "hh:00 tt") & " - " & FORMAT(TIME(SingleHour + 1, 0, 0), "hh:00 tt")
```

### 5. Security Watchlist Alerts
```dax
Security Watchlist Hits = 
CALCULATE(
    COUNTROWS(plate_logs),
    plate_logs[vehicle_status] = "Flagged"
)
```

---

## 📊 Step 3: Visual-by-Visual Configuration

### 1. Header & Slicers (Top Bar)
- **Title Text Box**: `ANPR & Vehicle Traffic Analytics Dashboard` (Font: Segoe UI / Outfit, Bold, 20pt, White `#FFFFFF`).
- **Subtitle**: `Automatic Number Plate Recognition (ANPR) & Vehicle Logging System` (11pt, `#94A3B8`).
- **Slicers (Dropdown / Between format)**:
  - **Date Range Slicer**: Field `plate_logs[timestamp]` (Slider mode: *Between*).
  - **Gate Slicer**: Field `plate_logs[gate_id]` (Dropdown mode: *All / Gate 01 / Gate 02*).
  - **Plate Status Slicer**: Field `plate_logs[vehicle_status]` (Dropdown mode: *All / Authorized / Visitor / Flagged*).

---

### 2. KPI Summary Cards (Top Row)
Use the **Card (new)** or individual **Card** visuals:
| Metric Card | Field / Measure | Callout Value Font | Accent / Color |
|---|---|---|---|
| **Total Detections** | `[Total Detections]` | 28pt Bold | Cyan `#38BDF8` |
| **Unique Plates** | `[Unique Plates]` | 28pt Bold | Cyan `#38BDF8` |
| **Avg OCR Accuracy** | `[Avg OCR Accuracy]` | 28pt Bold | Cyan `#38BDF8` |
| **Peak Hour** | `[Peak Hour]` | 22pt Bold | White `#FFFFFF` |
| **Security Watchlist Hits** | `[Security Watchlist Hits]` | 28pt Bold | Amber `#F59E0B` |

---

### 3. Hourly Traffic Volume (Area / Line Chart)
- **Visual Type**: **Area Chart**
- **X-Axis**: `plate_logs[log_hour]` (Continuous, 0 to 24)
- **Y-Axis**: `[Total Detections]`
- **Formatting**:
  - Line Color: Cyan `#06B6D4`
  - Area Fill: Linear gradient opacity `40%`
  - Stroke Width: `3px`
  - Data Labels: Off (or on peak only)

---

### 4. Detection Confidence Distribution (Donut Chart)
- **Visual Type**: **Donut Chart**
- **Legend**: `plate_logs[confidence_bracket]`
- **Values**: `[Total Detections]`
- **Colors**:
  - `>95% High`: Electric Teal `#00E5BC`
  - `85-95% Medium`: Slate Cyan `#0E7490`
  - `<85% Low`: Amber Orange `#F59E0B`

---

### 5. Top 10 Most Frequent Plates (Bar Chart)
- **Visual Type**: **Clustered Column Chart**
- **X-Axis**: `plate_logs[plate_number]` (Top 10 Filter by `[Total Detections]`)
- **Y-Axis**: `[Total Detections]`
- **Colors**: Cyan `#00E5BC` for top ranks, Amber `#F59E0B` for threshold ranks.

---

### 6. Real-Time Vehicle Logs Table (Bottom Grid)
- **Visual Type**: **Table**
- **Columns**:
  1. `ID` (`plate_logs[id]`)
  2. `Plate Number` (`plate_logs[plate_number]`)
  3. `Timestamp` (`plate_logs[timestamp]`) formatted as `dd-MM-yyyy hh:mm tt`
  4. `OCR Confidence` (`plate_logs[confidence_pct]`) with `%` sign
  5. `Gate ID` (`plate_logs[gate_id]`)
  6. `Status Badge` (`plate_logs[vehicle_status]`)
- **Conditional Formatting (Status Badge Background)**:
  - `"Authorized"` → Background `#10B981` (Green), Text `#FFFFFF`
  - `"Visitor"` → Background `#0EA5E9` (Sky Blue), Text `#FFFFFF`
  - `"Flagged"` → Background `#EF4444` (Red/Amber), Text `#FFFFFF`

---

## 🎨 Theme Palette & Styling Specifications

| UI Element | Color Hex Code |
|---|---|
| **Canvas Background** | `#0B132B` or `#0F172A` |
| **Card / Container Background** | `#1C2541` or `#1E293B` (with 1px border `#334155`) |
| **Primary Accent (Cyan / Aqua)** | `#00F0FF` / `#06B6D4` |
| **Secondary Accent (Teal)** | `#10B981` |
| **Warning / Alert (Amber)** | `#F59E0B` |
| **Danger / Flagged (Crimson)** | `#EF4444` |
| **Primary Text** | `#F8FAFC` (100% White/Off-White) |
| **Secondary Text** | `#94A3B8` (Muted Slate) |
