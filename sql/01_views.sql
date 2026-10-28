-- Bronze: raw_sales_events stores untouched Pub/Sub message bodies as STRING.
-- Silver: parse, validate and deduplicate by event_id for correct analytical counts.
-- The view is eventually consistent with streamed messages and not a physical deduplication mechanism.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.aegis_warehouse.v_parsed_sales` AS
SELECT
  data,
  SAFE.PARSE_JSON(data) AS payload,
  JSON_VALUE(SAFE.PARSE_JSON(data), '$.event_id') AS event_id,
  JSON_VALUE(SAFE.PARSE_JSON(data), '$.event_type') AS event_type,
  JSON_VALUE(SAFE.PARSE_JSON(data), '$.product_id') AS product_id,
  JSON_VALUE(SAFE.PARSE_JSON(data), '$.warehouse_id') AS warehouse_id,
  SAFE_CAST(JSON_VALUE(SAFE.PARSE_JSON(data), '$.quantity') AS INT64) AS quantity,
  SAFE_CAST(JSON_VALUE(SAFE.PARSE_JSON(data), '$.unit_price_inr') AS FLOAT64) AS unit_price_inr,
  JSON_VALUE(SAFE.PARSE_JSON(data), '$.currency') AS currency,
  SAFE_CAST(JSON_VALUE(SAFE.PARSE_JSON(data), '$.event_timestamp') AS TIMESTAMP) AS event_timestamp
FROM `{{PROJECT_ID}}.aegis_warehouse.raw_sales_events`;

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.aegis_warehouse.v_invalid_sales` AS
SELECT * FROM `{{PROJECT_ID}}.aegis_warehouse.v_parsed_sales` AS v_parsed_sales
WHERE payload IS NULL OR event_id IS NULL OR event_id = ''
   OR event_type != 'SALE' OR event_type IS NULL
   OR product_id IS NULL OR warehouse_id IS NULL
   OR quantity IS NULL OR quantity <= 0
   OR unit_price_inr IS NULL OR unit_price_inr <= 0
   OR currency != 'INR' OR currency IS NULL
   OR event_timestamp IS NULL
   OR NOT EXISTS (SELECT 1 FROM `{{PROJECT_ID}}.aegis_warehouse.dim_products` p WHERE p.product_id = v_parsed_sales.product_id)
   OR NOT EXISTS (SELECT 1 FROM `{{PROJECT_ID}}.aegis_warehouse.dim_warehouses` w WHERE w.warehouse_id = v_parsed_sales.warehouse_id);

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.aegis_warehouse.v_valid_sales` AS
SELECT event_id,event_type,product_id,warehouse_id,quantity,unit_price_inr,currency,event_timestamp
FROM `{{PROJECT_ID}}.aegis_warehouse.v_parsed_sales` AS v_parsed_sales
WHERE payload IS NOT NULL AND event_id IS NOT NULL AND event_id != ''
  AND event_type = 'SALE' AND product_id IS NOT NULL AND warehouse_id IS NOT NULL
  AND quantity > 0 AND unit_price_inr > 0 AND currency = 'INR' AND event_timestamp IS NOT NULL
  AND EXISTS (SELECT 1 FROM `{{PROJECT_ID}}.aegis_warehouse.dim_products` p WHERE p.product_id = v_parsed_sales.product_id)
  AND EXISTS (SELECT 1 FROM `{{PROJECT_ID}}.aegis_warehouse.dim_warehouses` w WHERE w.warehouse_id = v_parsed_sales.warehouse_id)
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY event_timestamp DESC) = 1;
