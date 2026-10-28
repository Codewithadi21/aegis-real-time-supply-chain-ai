-- OPTIONAL: BigQuery ML model training consumes credits/billing depending on service.
-- Avoid temporal leakage: hold out the latest 14 days for evaluation.
CREATE OR REPLACE MODEL `{{PROJECT_ID}}.aegis_warehouse.demand_regressor`
OPTIONS(model_type='linear_reg', input_label_cols=['units_sold'], data_split_method='NO_SPLIT', max_iterations=20) AS
SELECT product_id, day_of_week, promo_flag, unit_price_inr, units_sold
FROM `{{PROJECT_ID}}.aegis_warehouse.historical_demand`
WHERE sales_date < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY);

SELECT * FROM ML.EVALUATE(
 MODEL `{{PROJECT_ID}}.aegis_warehouse.demand_regressor`,
 (SELECT product_id,day_of_week,promo_flag,unit_price_inr,units_sold
  FROM `{{PROJECT_ID}}.aegis_warehouse.historical_demand`
  WHERE sales_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY))
);

-- A basic mean-demand baseline is necessary to assess whether ML adds value.
WITH averages AS (
 SELECT product_id, AVG(units_sold) AS avg_units
 FROM `{{PROJECT_ID}}.aegis_warehouse.historical_demand`
 WHERE sales_date < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)
 GROUP BY product_id
)
SELECT ROUND(AVG(ABS(h.units_sold-a.avg_units)),3) AS baseline_mae
FROM `{{PROJECT_ID}}.aegis_warehouse.historical_demand` h
JOIN averages a USING(product_id)
WHERE h.sales_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY);
