-- Gold: enrich valid events with product and warehouse dimensions.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.aegis_warehouse.v_fact_sales` AS
SELECT s.event_id,s.event_timestamp,s.product_id,s.warehouse_id,s.quantity,
       s.unit_price_inr, s.quantity*s.unit_price_inr AS revenue_inr,
       p.unit_cost_inr, s.quantity*(s.unit_price_inr-p.unit_cost_inr) AS gross_margin_inr,
       p.category,p.product_name
FROM `{{PROJECT_ID}}.aegis_warehouse.v_valid_sales` s
JOIN `{{PROJECT_ID}}.aegis_warehouse.dim_products` p USING(product_id)
JOIN `{{PROJECT_ID}}.aegis_warehouse.dim_warehouses` w USING(warehouse_id);

-- Inventory opening snapshot is an experiment baseline; orders reduce the projection.
-- Inbound purchase orders are deliberately NOT added until an actual receipt event exists.
-- Historical daily demand is divided evenly across two warehouses: explicit demo assumption.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.aegis_warehouse.v_stock_risk` AS
WITH sold AS (
  SELECT product_id,warehouse_id,SUM(quantity) AS sold_units
  FROM `{{PROJECT_ID}}.aegis_warehouse.v_fact_sales`
  GROUP BY 1,2
), velocity AS (
  SELECT product_id, AVG(units_sold)/2.0 AS estimated_daily_demand_per_warehouse
  FROM `{{PROJECT_ID}}.aegis_warehouse.historical_demand`
  GROUP BY 1
)
SELECT i.product_id,i.warehouse_id,i.opening_stock,
       COALESCE(s.sold_units,0) AS sold_units,
       GREATEST(i.opening_stock-COALESCE(s.sold_units,0),0) AS remaining_stock,
       ROUND(v.estimated_daily_demand_per_warehouse,2) AS estimated_daily_demand,
       ROUND(SAFE_DIVIDE(GREATEST(i.opening_stock-COALESCE(s.sold_units,0),0),
                         NULLIF(v.estimated_daily_demand_per_warehouse,0)),2) AS estimated_days_cover,
       CASE WHEN SAFE_DIVIDE(GREATEST(i.opening_stock-COALESCE(s.sold_units,0),0),
                             NULLIF(v.estimated_daily_demand_per_warehouse,0)) < 7
            THEN 'HIGH' ELSE 'NORMAL' END AS stock_risk
FROM `{{PROJECT_ID}}.aegis_warehouse.opening_inventory` i
LEFT JOIN sold s USING(product_id,warehouse_id)
LEFT JOIN velocity v USING(product_id);
