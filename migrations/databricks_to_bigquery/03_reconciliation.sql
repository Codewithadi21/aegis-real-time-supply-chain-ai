CREATE OR REPLACE VIEW `YOUR_PROJECT_ID.aegis_migration.inventory_reconciliation` AS
WITH
source AS (
  SELECT warehouse_id, product_id, stock_qty, updated_at, stockout_flag
  FROM `YOUR_PROJECT_ID.aegis_migration.inventory_source_snapshot`
),
target AS (
  SELECT warehouse_id, product_id, stock_qty, updated_at, stock_qty < 5 AS stockout_flag
  FROM `YOUR_PROJECT_ID.aegis_migration.inventory_test`
),
source_keys AS (
  SELECT warehouse_id, product_id, COUNT(*) AS row_count,
    MAX(stock_qty) AS stock_qty, MAX(updated_at) AS updated_at,
    LOGICAL_OR(stockout_flag) AS stockout_flag
  FROM source GROUP BY warehouse_id, product_id
),
target_keys AS (
  SELECT warehouse_id, product_id, COUNT(*) AS row_count,
    MAX(stock_qty) AS stock_qty, MAX(updated_at) AS updated_at,
    LOGICAL_OR(stockout_flag) AS stockout_flag
  FROM target GROUP BY warehouse_id, product_id
),
key_checks AS (
  SELECT warehouse_id, product_id,
    s.row_count IS NULL OR t.row_count IS NULL AS key_missing,
    COALESCE(s.row_count, 0) > 1 OR COALESCE(t.row_count, 0) > 1 AS duplicate_key,
    warehouse_id IS NULL OR product_id IS NULL
      OR TRIM(warehouse_id) = '' OR TRIM(product_id) = '' AS invalid_key,
    s.stock_qty IS DISTINCT FROM t.stock_qty AS quantity_diff,
    s.updated_at IS DISTINCT FROM t.updated_at AS timestamp_diff,
    s.stockout_flag IS DISTINCT FROM t.stockout_flag AS stockout_diff,
    s.stock_qty AS source_qty, t.stock_qty AS target_qty,
    s.updated_at AS source_updated_at, t.updated_at AS target_updated_at,
    s.stockout_flag AS source_stockout, t.stockout_flag AS target_stockout
  FROM source_keys AS s
  FULL OUTER JOIN target_keys AS t USING (warehouse_id, product_id)
),
source_totals AS (
  SELECT warehouse_id, SUM(stock_qty) AS total FROM source GROUP BY warehouse_id
),
target_totals AS (
  SELECT warehouse_id, SUM(stock_qty) AS total FROM target GROUP BY warehouse_id
),
warehouse_checks AS (
  SELECT warehouse_id, s.total AS source_total, t.total AS target_total,
    s.total IS DISTINCT FROM t.total AS total_diff
  FROM source_totals AS s FULL OUTER JOIN target_totals AS t USING (warehouse_id)
),
summary AS (
  SELECT
    (SELECT COUNT(*) FROM source) AS source_rows,
    (SELECT COUNT(*) FROM target) AS target_rows,
    (SELECT COUNTIF(key_missing) FROM key_checks) AS missing_keys,
    (SELECT COUNTIF(duplicate_key OR invalid_key) FROM key_checks) AS invalid_or_duplicate_keys,
    (SELECT COUNTIF(quantity_diff) FROM key_checks) AS quantity_mismatches,
    (SELECT COUNTIF(timestamp_diff) FROM key_checks) AS timestamp_mismatches,
    (SELECT COUNTIF(stockout_diff) FROM key_checks) AS stockout_mismatches,
    (SELECT COUNTIF(total_diff) FROM warehouse_checks) AS warehouse_mismatches
),
differences AS (
  SELECT * FROM key_checks
  WHERE key_missing OR duplicate_key OR invalid_key OR quantity_diff OR timestamp_diff OR stockout_diff
)
SELECT
  IF(source_rows > 0 AND source_rows = target_rows
    AND missing_keys = 0 AND invalid_or_duplicate_keys = 0
    AND quantity_mismatches = 0 AND timestamp_mismatches = 0
    AND stockout_mismatches = 0 AND warehouse_mismatches = 0, 'PASS', 'HOLD') AS decision,
  summary.*, d.warehouse_id, d.product_id, d.source_qty, d.target_qty,
  d.source_updated_at, d.target_updated_at, d.source_stockout, d.target_stockout,
  w.source_total AS source_warehouse_qty, w.target_total AS target_warehouse_qty
FROM summary
LEFT JOIN differences AS d ON TRUE
LEFT JOIN warehouse_checks AS w ON w.warehouse_id = d.warehouse_id;
