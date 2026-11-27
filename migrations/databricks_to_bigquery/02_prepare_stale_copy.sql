-- Use a dedicated aegis_migration dataset. inventory_landing and
-- inventory_source_snapshot are the two independent CSV loads.
CREATE OR REPLACE TABLE `YOUR_PROJECT_ID.aegis_migration.inventory_test` AS
SELECT * EXCEPT(stockout_flag)
FROM `YOUR_PROJECT_ID.aegis_migration.inventory_landing`;

UPDATE `YOUR_PROJECT_ID.aegis_migration.inventory_test`
SET stock_qty = 12, updated_at = TIMESTAMP '2025-01-01 00:00:00+00'
WHERE warehouse_id = 'WH_IND_01' AND product_id = 'LAPTOP_001';

ASSERT @@row_count = 1 AS 'The stale-record injection must affect exactly one row';
