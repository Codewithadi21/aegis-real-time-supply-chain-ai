# Technical interview walkthrough

## 90-second narrative
"I noticed a gap between classical ETL quality checks and downstream model reliability. A source can silently change the meaning of an existing column without breaking schemas, leaving a healthy-looking pipeline that changes ML decisions. I built a reproducible synthetic experiment in Python: it trains a fixed churn model, scores the same customer cohort on trusted and semantically changed snapshots, checks distribution and semantic contracts, quantifies decision flips and errors, and generates an evidence-grounded incident report. The approach is extensible to BigQuery and event-driven observability. I intentionally distinguished prediction sensitivity from proven business loss, because this is crucial for trustworthy ML engineering."

## Questions to prepare for
- Why can schema, null, and duplicate checks pass while semantics fail?
- How would you know whether drift actually reduced model accuracy without labels?
- Why score identical holdout IDs with a fixed model?
- Why are KS/PSI insufficient as stand-alone incident triggers?
- How would you prevent feature leakage across time?
- How would you maintain lineage automatically in a large warehouse?
- Where would Pub/Sub, Dataflow, BigQuery, Vertex AI and monitoring fit in a cloud implementation?
- What would a safe quarantine and rollback strategy look like?
- How would you stop a Gemini agent from executing destructive SQL or inventing facts?

## Proof expectations
Keep screenshots of tests, paired prediction changes, evaluation metrics, incident report and (only if deployed) actual BigQuery tables. Do not label the cloud demonstration "productionized" until you have evidence.
