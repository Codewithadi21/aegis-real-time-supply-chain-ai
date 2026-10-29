# GCP / Google Colab walkthrough

This project is fully executable on **free Colab CPU** without GCP charges.

## Quickstart (no Google Cloud costs)
1. Open the `notebooks/DataPulse_AI_Colab.ipynb` file in Google Colab (link on README).
2. Run cell 1 to clone public GitHub repository.
3. Run cell 2 to install requirements and imports.
4. Run deterministic data generation, contract checks, drift analysis, replay and incident report cells.
5. Inspect artifacts in `artifacts/`; save screenshots of before/after predictions.

## Optional BigQuery upload (may consume free-tier quota or credits)
1. Check Cloud Billing trial and set a budget alert; alerts do not hard-stop charges.
2. In Colab, `from google.colab import auth; auth.authenticate_user()`.
3. Enable BigQuery API and give your signed-in user appropriate dataset creation/job permissions.
4. Run `!python -m cloud.bigquery_load --project-id YOUR_ACTUAL_PROJECT_ID` from repository root.
5. Open BigQuery Studio and run `cloud/queries.sql` after replacing `YOUR_PROJECT_ID`.
6. Delete `datapulse_ai` dataset when no longer needed.

## Optional Pub/Sub incident event demonstration
Enable Pub/Sub API, then `!python -m cloud.pubsub_demo --project-id YOUR_ACTUAL_PROJECT_ID`.
A topic is created and a single synthetic incident is published. **No subscription/consumer is included**; this demonstration is not an end-to-end streaming production pipeline.
Delete the topic afterward.

## Optional Gemini text explanation
Requires a separate API key configured privately via `GOOGLE_API_KEY` and eligible billing. Model/API usage may be charged, independent of Google Cloud welcome credits. Never commit credentials or API responses containing private data.

## Privacy and security
Use synthetic data only. Never upload company files, client identifiers, raw logs, service account keys, or proprietary material.
