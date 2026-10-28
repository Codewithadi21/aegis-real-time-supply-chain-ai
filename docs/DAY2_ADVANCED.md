# Day 2 — AI/ML and optional Dataflow

## 1. Stockout Decision Replay
Run `python -m aegis.local_demo`. Compare 0/3/7/14-day shipment arrival delays. Explain that forecasts and revenue exposure are **synthetic scenario calculations**.

## 2. BigQuery ML
Open `sql/03_bigquery_ml_optional.sql` in BigQuery Studio, replace `{{PROJECT_ID}}` with your real ID and run each SQL statement in order. BigQuery ML training may consume credits. Evaluate MAE on the last 14 days and benchmark mean-demand MAE. Add actual results to GitHub README only after running.

## 3. RAG
`aegis.retrieval` implements free TF-IDF vector retrieval for policy documents. For **neural embeddings** install `requirements-rag-optional.txt`, run `aegis.semantic_retrieval.semantic_search` in Colab. Downloading transformer weights uses network and additional time. `python -m scripts.optional_gemini --project-id ID` is cost-safe prompt preview; use `--confirm-billing` only after checking Vertex AI model permissions and pricing.

## 4. Dataflow (optional, credit-consuming)
Dataflow is a separate advanced path. Enable Dataflow/Compute Engine/Cloud Storage APIs, create a GCS bucket in a compatible US region, configure Dataflow worker identity with least privilege. Create a new Pub/Sub **pull subscription** `aegis-dataflow-pull` on `aegis-sales-events`; do not use `aegis-to-bigquery` (an export subscription) as Beam input.

Install Beam in a suitable Python environment: `pip install -r requirements-beam.txt`. Verify local transforms with `python -m scripts.beam_local_smoke`. If workers can import the packaged code and you have staging bucket permissions, deploy a short-lived managed job:

```bash
python -m scripts.beam_pipeline \
  --project-id YOUR_PROJECT_ID \
  --subscription projects/YOUR_PROJECT_ID/subscriptions/aegis-dataflow-pull \
  --bucket YOUR_BUCKET \
  --region us-central1
```

This job is a **continuous streaming job**; it does not automatically stop when publishing ends. Find it in https://console.cloud.google.com/dataflow/jobs and **Drain** (or Cancel) it after the test. Check cloud billing afterward. Dataflow will write to separate `dataflow_valid_sales` and `dataflow_rejected_sales` tables.

## 5. Future Databricks version
Build a second, explicit implementation with Delta Bronze/Silver/Gold layers in Databricks using PySpark. Compare schema evolution, merge/upsert behavior, transaction history, incremental processing, and costs against BigQuery views. Keep this in a separate repository/branch to avoid confusing the core Google-focused design.
