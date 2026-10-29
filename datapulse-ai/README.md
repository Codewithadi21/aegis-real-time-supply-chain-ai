# DataPulse AI — Data-to-Decision Impact Replay

> **What if every basic pipeline check passes, but an upstream field quietly changes meaning and causes your ML model to change business decisions?**

A reproducible Python / ML engineering project that traces a **semantic data failure** from an apparently healthy source dataset to model predictions and a decision-level incident report. Built as a standalone project inside the AEGIS repository; it does not overwrite AEGIS.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Codewithadi21/aegis-real-time-supply-chain-ai/blob/main/datapulse-ai/notebooks/DataPulse_AI_Colab.ipynb)

## Problem
The column `engagement_events_30d` used to count purchases. A producer switches the definition to login events but keeps its name, type and non-null behavior. The data pipeline passes basic schema checks, yet a pre-trained churn-risk model interprets logins as purchase activity. Traditional "pipeline succeeded" monitoring may miss the resulting model decision shifts.

## What this implementation demonstrates
- Synthetic customer event data and an explicitly documented **semantic data contract**.
- Conventional schema/type/uniqueness checks, plus formatting/whitespace/duplicate fault handling.
- Statistical input change monitoring (`PSI`, KS statistic) with caution about interpreting drift.
- Fixed-model, same-cohort, paired replay that shows how many predictions and high-risk flags change.
- Evaluation against synthetic known churn labels (AUC, recall, false negatives) rather than claiming drift automatically equals harm.
- Evidence-first incident report and manually declared field → feature → model → decision lineage.
- Optional BigQuery upload, Pub/Sub incident-event publishing, and private Gemini explanation.

## Verified locally
The default CLI and automated tests are designed to run offline. **Live GCP deployment and production-scale performance are not claimed.** Metrics come from seeded synthetic data, not real company customers.

## Run locally
```bash
cd datapulse-ai  # if running from the AEGIS repository root
python -m pip install -r requirements.txt
python -m pytest -q
python -m datapulse --rows 5000
```
Expected outputs (ignored by Git):
```text
artifacts/replay_summary.json
artifacts/incident_report.json
artifacts/prediction_replay.csv
```

## Day 1 — Colab (no GCP costs)
[**Launch notebook**](https://colab.research.google.com/github/Codewithadi21/aegis-real-time-supply-chain-ai/blob/main/datapulse-ai/notebooks/DataPulse_AI_Colab.ipynb)

## Day 2 — Optional Google Cloud integration
See [GCP and Colab instructions](docs/GCP_COLAB_GUIDE.md). BigQuery and Pub/Sub may use free-tier allowances or credits. No service account keys are required in the repo.

## Architecture
```mermaid
flowchart LR
    A[Source snapshot] --> B[Basic contract checks]
    B --> C[Baseline and changed features]
    C --> D[Fixed ML churn model]
    D --> E[Decision Impact Replay]
    C --> F[Distribution + semantic monitoring]
    F --> G[Evidence-first investigator]
    E --> G
    G --> H[Human review]
    G -. optional .-> I[Gemini explanation]
```

## What we measure
- How much the `engagement_events_30d` distribution changed.
- Whether the **basic** input checks still pass.
- Whether the **semantic** data contract fails.
- How many predictions flip under identical cohort/model conditions.
- Whether labeled ML metrics change (when synthetic labels are available).

## Engineering honesty and limitations
- A fixed-model replay demonstrates **sensitivity to a source change**; it does **not prove causation or actual business loss**.
- Synthetic data are designed to make this failure mode visible.
- Feature drift can be benign. Do not automatically quarantine all distribution changes.
- Incident diagnostics propose actions requiring approval; they never change production data.
- This is an educational portfolio prototype. It is not a vendor replacement or proven enterprise-wide observability platform.

More: [business brief](docs/PROJECT_BRIEF.md) · [architecture decisions](docs/ARCHITECTURE.md) · [interview guide](docs/INTERVIEW_GUIDE.md).

## Security
Never commit production data, OAuth tokens, API keys, or service-account key files. `.gitignore` excludes `.env`, artifacts, and credential-like filenames.

## Free local LLM — no Gemini billing required
Run the independent [DataPulse Local AI Colab notebook](notebooks/DataPulse_Local_AI_Colab.ipynb) to explain the **real** DataPulse incident report using the open-weight [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) model. This integration uses a local `datapulse/local_llm.py` adapter and `requirements-local-llm.txt`: no Gemini API key, Vertex AI account, or model API billing required. Free Colab GPU availability is limited and model weights download on first run. The original, deterministic investigator remains authoritative; the LLM adds a reviewable explanation, not a proven root cause or autonomous remediation. The new code is committed, but **live model inference in the user's Colab is not yet verified**.

## DataPulse Guide AI — project tutor + incident investigation
The [Guide AI Colab notebook](notebooks/DataPulse_Guide_AI_Colab.ipynb) demonstrates two grounded assistant modes: (1) explaining how DataPulse works from checked-in project documentation and (2) analyzing the verified synthetic incident report. `datapulse/guide_assistant.py` uses local **TF-IDF source retrieval**, optional local Qwen generation, explicit source paths, and a retrieval-only fallback. Read [the user guide](docs/DATAPULSE_USER_GUIDE.md). This is not a trained-from-scratch LLM, true vector embedding RAG, an autonomous repair agent, or a Vertex AI deployment. GitHub code is committed; user-side Colab LLM inference remains to be validated.
