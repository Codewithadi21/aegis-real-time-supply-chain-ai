-- Replace YOUR_PROJECT_ID with your real Google Cloud project ID.
-- This is a read-only analysis of synthetic replay outputs.
SELECT
  COUNT(*) AS tested_customers,
  COUNTIF(predicted_churn_before != predicted_churn_after) AS changed_decisions,
  ROUND(100 * SAFE_DIVIDE(COUNTIF(predicted_churn_before != predicted_churn_after), COUNT(*)), 2) AS decision_flip_pct,
  COUNTIF(churned_next_30d = 1 AND predicted_churn_before = 0) AS missed_churners_before,
  COUNTIF(churned_next_30d = 1 AND predicted_churn_after = 0) AS missed_churners_after
FROM `YOUR_PROJECT_ID.datapulse_ai.paired_prediction_replay`;

-- Largest prediction changes: choose cases for diagnostic investigation.
SELECT customer_id, churned_next_30d,
       predicted_churn_probability_before,
       predicted_churn_probability_after,
       ABS(predicted_churn_probability_after - predicted_churn_probability_before) AS absolute_change
FROM `YOUR_PROJECT_ID.datapulse_ai.paired_prediction_replay`
ORDER BY absolute_change DESC
LIMIT 20;
