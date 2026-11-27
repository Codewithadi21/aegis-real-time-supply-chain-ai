MERGE `YOUR_PROJECT_ID.aegis_migration.inventory_test` AS target
USING (
  SELECT warehouse_id, product_id, stock_qty, updated_at
  FROM `YOUR_PROJECT_ID.aegis_migration.inventory_source_snapshot`
  WHERE warehouse_id = 'WH_IND_01' AND product_id = 'LAPTOP_001'
) AS source
ON target.warehouse_id = source.warehouse_id
   AND target.product_id = source.product_id
WHEN MATCHED THEN UPDATE SET stock_qty = source.stock_qty, updated_at = source.updated_at;

ASSERT @@row_count = 1 AS 'The correction must reload exactly one row';
