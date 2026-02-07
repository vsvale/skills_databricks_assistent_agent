-- Manual SQL Pattern for SCD Type 2 Merge
-- 1. Source Construction: Union the new data (for insertion) with the keys from target that need to be closed.
-- 2. Merge: Update the old record to close it, and insert the new record.

MERGE INTO target t
USING (
   -- 1. New records to be inserted (marked as current)
   SELECT key, value, effective_date as start_date, NULL as end_date, true as is_current 
   FROM source_updates
   
   UNION ALL
   
   -- 2. Existing target records that need to be closed (update end_date)
   SELECT t.key, t.value, t.start_date, s.effective_date as end_date, false as is_current
   FROM target t
   JOIN source_updates s ON t.key = s.key
   WHERE t.is_current = true AND t.value <> s.value
) s
ON t.key = s.key AND t.start_date = s.start_date

-- Close the old record
WHEN MATCHED AND s.is_current = false THEN
  UPDATE SET t.end_date = s.end_date, t.is_current = false

-- Insert the new record
WHEN NOT MATCHED THEN
  INSERT (key, value, start_date, end_date, is_current)
  VALUES (s.key, s.value, s.start_date, s.end_date, s.is_current)
