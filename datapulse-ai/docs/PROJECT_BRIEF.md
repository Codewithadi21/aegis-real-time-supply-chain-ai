# Project brief — DataPulse AI

## Business problem
Traditional ETL checks can confirm that data is complete and parseable yet miss **semantic source changes** that silently alter model predictions and operational decisions.

## Primary user
Data Engineers, MLOps engineers, data scientists, and analytic platform teams.

## Concrete example
The field `engagement_events_30d` originally counts purchase activity. The upstream producer changes it to login activity without renaming the field. Values remain numeric and non-null; data-quality validation still passes. A previously trained churn model scores the altered data. DataPulse compares the same model on the same customer cohort using original vs changed feature snapshots.

## Five independently testable requirements
1. **Data contract:** numeric, required, unique customer identifiers; meaningful business definition documented.
2. **Drift:** detect distribution changes, report distribution summary and a KS test (exploratory; do not treat p-values as proof of harm).
3. **Model impact:** compare paired probabilities, class decisions, AUC, recall, false negatives and affected customers.
4. **Trace:** follow manually declared field-to-feature-to-model-to-decision lineage.
5. **Investigation:** publish a deterministic evidence-based explanation and human-review recommendation. Optional Gemini is a text layer, never the metrics engine.

## Why it's not just a drift dashboard
It shows an *end-to-end impact chain* from semantically broken upstream values to model output changes, and quantifies the difference on a fixed model and paired cohort.

## What it does NOT claim
- No evidence of realized revenue losses or causal effect on actual customers.
- No benchmark on a live enterprise environment.
- No automated production repair or safe auto-retraining.
- No true inference-serving monitoring or production-scale streaming without separate deployment.

## Minimum credible demo
`python -m datapulse` creates artifacts containing evidence of the schema pass, semantic failure, drift statistics, prediction flips, baseline and changed model metrics, and a structured incident report.
