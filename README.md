# AEGIS — Real-Time AI-Ready Supply Chain Intelligence

**Google Data Engineer (DAS / Platforms & Devices)-aligned portfolio demonstration**

[![Open Day 1 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Codewithadi21/aegis-real-time-supply-chain-ai/blob/main/notebooks/AEGIS_Day1_Colab.ipynb) **Day 1** · [Open Day 2 in Colab](https://colab.research.google.com/github/Codewithadi21/aegis-real-time-supply-chain-ai/blob/main/notebooks/AEGIS_Day2_Advanced.ipynb)


This project uses **fully synthetic** electronics sales, stock, supplier and demand data. It combines real cloud messaging, a BigQuery analytical warehouse, supply-chain decision replay, an optional BigQuery ML experiment and grounded supplier-policy retrieval.

> **Status transparency:** Source code, notebook, SQL, synthetic generator and unit tests are included and runnable. Live GCP resources, Dataflow deployment, BigQuery ML training and Gemini API requests are **not claimed to have been deployed/verified on your account** until you run them and capture results.

## Business problem
A multinational electronics supplier cannot see fast-moving sales and stock problems with yesterday's batch report. Supply disruptions cause stockout risk and potential missed revenue. Stakeholders need a trustworthy warehouse, testable metrics, and explainable risk scenarios.

## Why it's distinctive
**Supplier Delay Decision Replay:** compare 0/3/7/14-day arrival delays, the first stockout day, unfulfilled units and hypothetical revenue exposure; retrieve supplier policy evidence to explain escalation decisions. **No unsupported claim of unique IP or causal predictions.**

## Architecture

```text
Colab Python Sales Event Producer
            |
         Pub/Sub
            |
  BigQuery export subscription (streaming, no always-on Dataflow worker)
            |
   BigQuery Bronze/raw_sales_events (JSON stored as STRING)
            |
     BigQuery Silver SQL views (parse, validate, dedup event_id)
            |
     Gold v_fact_sales / v_stock_risk  <-- products, warehouses, 90-day demand
            |                     \
   Stockout Decision Replay       BigQuery ML (optional, temporal holdout)
            |
  Supplier policy retrieval (TF-IDF baseline / optional neural embeddings)
            |
        Gemini via Vertex AI (optional API call; gated for cost)
```

**Advanced alternative:** Pub/Sub → Apache Beam → managed Dataflow → separate validated/rejected BigQuery tables. This requires separate Pub/Sub pull subscription and billable streaming workers.

## Start here: fastest path

1. Click the **Open Day 1 in Colab** badge above to launch the notebook directly from GitHub.
2. Follow `docs/CLOUD_SETUP.md`, starting with the billing safety check.
3. Run the first code cell to clone this repository automatically; then authenticate to your GCP project.
4. Execute notebook cells sequentially. Set `PROJECT_ID` to your own project ID.
5. Run the `scripts.create_subscription` cell to create the BigQuery export subscription **before** publishing live events (dataset-scoped Pub/Sub service-agent permission may be required).
6. Run 20 events and a replay, verify `raw_sales_events`, `v_valid_sales` and `v_stock_risk` in BigQuery Studio.
7. Day 2: see `docs/DAY2_ADVANCED.md` for optional ML/RAG/Dataflow steps.

### Run the full local project now, no GCP needed

```bash
python -m pip install -r requirements.txt
python -m aegis.local_demo
python -m pytest -q
```

### Connect to GCP from Colab

```bash
python -m pip install -r requirements-gcp.txt
python -m scripts.setup_gcp --project-id YOUR_REAL_PROJECT_ID
python -m scripts.create_subscription --project-id YOUR_REAL_PROJECT_ID
# If permissions fail, use the manual setup described in docs/CLOUD_SETUP.md
python -m scripts.publish_events --project-id YOUR_REAL_PROJECT_ID --count 20 --replay-first
python -m scripts.run_queries --project-id YOUR_REAL_PROJECT_ID
```

## Tech stack and JD mapping

| Google JD skill | Implementation evidence |
|---|---|
| Python & SQL | Event generator, validation, analytics views |
| GCP BigQuery | Central warehouse, reference data, SQL marts |
| Pub/Sub | Actual streaming messages and export subscription |
| Dataflow | Optional Beam source and deployment (credit-funded) |
| ML data foundation | Synthetic 90-day historical features and BigQuery ML SQL |
| AI/LLMs/RAG | Supplier policy retrieval, grounded prompt, optional Vertex Gemini |
| Data modeling | Product, supplier, warehouse dimensions + fact events |
| Data quality/governance | Type/schema checks, rejection view, event ID dedup |
| Stakeholder focus | Warehouse KPIs and delay impact scenario report |

## Cost warning
The Google free trial is a **credit allowance**, not permission to run every service free of charge. BigQuery has a monthly free usage tier, but **BigQuery subscription delivery, BigQuery ML operations, Dataflow workers and Vertex AI may incur charges**, depending on account and workload. Check https://cloud.google.com/free and https://cloud.google.com/dataflow/pricing. Set billing alerts, inspect active jobs and stop/decommission billable resources after demonstration. Do not commit credentials.

## Dataset sizes (default)
6 products, 3 suppliers, 2 warehouses, 12 inventory positions, 12 purchase orders, 540 daily demand records; default live demo 20 events (+ one deliberate replay). Synthetic INR prices, no proprietary data. Example CSVs are included in `data/samples/` and can be regenerated with `python -m aegis.synthetic`.

## Evidence and truthfulness
- **Included:** implementation code, local tests, notebooks, SQL and architecture explanation.
- **Collect after real execution:** Console screenshots, successful job IDs, measured end-to-end delay, BigQuery ML model evaluation, RAG answer with source document refs.
- **Do not claim:** enterprise production traffic, real customer data, financial savings, true demand accuracy, or completed GCP deployment until validated.

## Measure observable streaming latency

After your BigQuery export subscription is working, run `python -m scripts.measure_latency --project-id YOUR_REAL_PROJECT_ID`. This publishes **one** test event and polls BigQuery (limited query count). The resulting seconds include query/polling delay and should not be described as a server-side delivery SLA.

## Publish on GitHub

See [GitHub upload instructions](docs/GITHUB_UPLOAD.md).

## Cleanup
Delete unneeded Pub/Sub subscriptions/topics and BigQuery datasets; **Drain/Cancel** any Dataflow job in the Console; delete optional GCS bucket when finished. Budget alerts do not cap spending.

## Docs
- [Day 1 cloud setup](docs/CLOUD_SETUP.md)
- [Architecture and assumptions](docs/ARCHITECTURE.md)
- [Day 2 and optional advanced tools](docs/DAY2_ADVANCED.md)
- [Interview preparation](docs/GOOGLE_INTERVIEW_NOTES.md)

## License
MIT — see LICENSE.
