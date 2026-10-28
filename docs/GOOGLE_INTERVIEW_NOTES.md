# Google DAS — Project explanation checklist

## 90-second pitch
I built AEGIS, a synthetic consumer-electronics supply-chain intelligence platform. Python-generated sales events travel through Pub/Sub to BigQuery, where SQL validation and event-ID deduplication create analytics-ready facts. I linked sales with product and warehouse dimensions to estimate days of stock cover. A scenario simulator compares supplier delays of 0, 3, 7 and 14 days and calculates hypothetical revenue exposure. I also designed a small demand forecasting experiment with a temporal holdout, plus policy retrieval for grounded AI explanations. I can explain why I chose direct Pub/Sub export first, then used Dataflow as an optional advanced transformation layer.

Only say a feature is **built/deployed** after you have personally executed and verified it. Until then say **designed/planned**.

## Deep dive questions
- Why Pub/Sub? Decouples producer and consumer and buffers events; delivery can repeat.
- Why BigQuery? Managed analytical warehouse, effective for joins/aggregations and ML integration.
- What is idempotency? One logical sale has a stable event ID; deduplication avoids double-counting.
- What if schema changes? Validate and quarantine unexpected data, use versioned contracts.
- What if events are late? The simple MVP orders by event timestamp; production should use event-time windows, watermarks and appropriate late-data policy.
- How do you calculate inventory? Opening stock minus sold units in a short demo; real enterprise needs an event-sourced stock ledger with receipts/returns.
- How to optimize query cost? Partition large fact tables by event date, cluster by frequent join/filter keys, prune partitions, materialize repeated heavy transforms, benchmark bytes read.
- How can ML fail? Synthetic data can be unrepresentative; compare temporal holdout MAE to baseline and report limitations.
- Why RAG? Retrieve explicit supplier-policy evidence before generating natural-language explanations; citations and numerical validation still required.
- Dataflow vs BigQuery subscription? Dataflow supports complex streaming processing; direct export is cheaper/simpler when transformation can occur in warehouse SQL.
- Production monitoring? Publish-to-query latency, rejected-event volume, duplicate rate, query bytes, service errors, pipeline uptime, model drift.
