-- ============================================================
-- Data Cleaning Script: SJSU Parking Data
-- ============================================================

-- Step 1: Inspect missing values
SELECT COUNT(*) AS null_percent_full_count
FROM SJSU_PARKING_DATA_RAW
WHERE percent_full IS NULL;

-- Step 2: Update missing values
-- The source data uses "Full" for 100% occupancy,
-- which was stored as NULL during ingestion.
-- These values are standardized to 100.

UPDATE SJSU_PARKING_DATA_RAW
SET percent_full = 100
WHERE percent_full IS NULL;

-- Step 3: Verify update
SELECT COUNT(*) AS remaining_nulls
FROM SJSU_PARKING_DATA_RAW
WHERE percent_full IS NULL;

-- Step 4: Sanity check values
SELECT MIN(percent_full) AS min_value,
       MAX(percent_full) AS max_value
FROM SJSU_PARKING_DATA_RAW;