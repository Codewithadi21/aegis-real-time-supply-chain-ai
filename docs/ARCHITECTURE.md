# Architecture and Engineering Choices

## Business question
A consumer electronics enterprise needs rapid insights into sales, inventory and supplier delays. Day-old reports cannot support timely stockout decisions.

## Core streaming path
Colab Python producer → Pub/Sub topic → **BigQuery export subscription** → raw BigQuery table (`data` as STRING) → validation/deduplication SQL views → inventory-risk view. The export subscription provides actual server-side streaming ingestion. Data consumers poll or query BigQuery; this does **not** imply sub-second dashboards.

### Why not always Dataflow?
GCP recommends direct BigQuery subscriptions when no complex transformations are needed before storage. Dataflow is a managed streaming processing option for event-time windows, joins, side outputs and validation, but streaming workers incur charges. In phase 2, create **another** pull subscription for Dataflow; do not attempt to read the export subscription.

## Table design
- **Bronze:** `raw_sales_events`: one row per published message, `data STRING` (raw JSON body).
- **Silver:** `v_parsed_sales`, `v_valid_sales` (filter, `event_id` deduplication), `v_invalid_sales` (diagnostics).
- **Gold:** `v_fact_sales`, `v_stock_risk` (product and warehouse dimensional joins).
- **Reference:** `dim_products`, `dim_suppliers`, `dim_warehouses`, `opening_inventory`, `purchase_orders`, `historical_demand`.

### Important assumptions
- Events are synthetic; no actual inventory, sales or supplier data is used.
- Historical demand is synthetic and is **not** combined into online event counts; it informs expected velocity only.
- Online `SALE` messages reduce a fixed opening stock baseline in the demo. Inbound purchase orders do NOT increase on-hand stock until receipt is recorded. Production would use an inventory ledger with receiving, returns, adjustments and snapshots.
- Two warehouses share forecast historical demand evenly as a demonstrative simplification.
- Transactions are INR only; multi-currency conversion is deferred until an FX reference table exists.
- Deduplication occurs in a SQL view using stable application `event_id`, NOT by assuming Pub/Sub exactly-once message delivery.
- The Decision Replay's revenue exposure equals hypothetical unfulfilled units x sale price. It is *not realized lost sales*, causal inference, or guaranteed business outcome.

## AI/ML details
BigQuery ML trains an illustrative regression model from 90 days of synthetic demand. Hold out the last 14 days and compare MAE to a mean-demand baseline. A model may fail to outperform the baseline, which is a valid measured outcome.

The retrieval baseline ranks synthetic Markdown policies by TF-IDF cosine similarity. The optional neural retrieval script uses `sentence-transformers` embeddings. Gemini on Vertex AI is an **opt-in API call**, not needed for the offline demo; prompts include source references and ask the model to avoid unsourced claims. Retrieval output is not automatically verified as fact.

## Production enhancements (not claimed as implemented)
- IAM service identities and least-privilege dataset permissions
- Automated IaC, dead-letter queues, idempotent upsert/materialized deduplication
- Watermarks and event-time windowing in Beam, monitoring, PII protection
- Scheduled incremental ingestion, SCD2 dimensions, incident response workflows
- Replay and reconciliation against true inventory ledgers, traceable model governance
- CI deploy stages and reproducible load testing / concurrency and latency SLAs
