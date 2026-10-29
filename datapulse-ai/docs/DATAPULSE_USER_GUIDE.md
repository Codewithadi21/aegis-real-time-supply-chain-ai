# DataPulse AI — Project Guidance & Demo Handbook

## What is DataPulse?
DataPulse is a **synthetic, reproducible ML data-reliability prototype**. It demonstrates that a source field can preserve valid types, required columns and unique identifiers while changing its **business meaning**. The existing churn model then makes different predictions. The project traces source → data checks → feature drift → model replay → incident report. It does **not** claim demonstrated real-world harm.

## What's implemented?
- Synthetic baseline and semantically shifted customer events: `datapulse/generator.py`
- Schema, formatting, duplicate checks and cleanup: `datapulse/quality.py`
- Semantic checks, PSI and KS feature drift: `datapulse/drift.py`
- Predictive classification and metrics: `datapulse/model.py`
- Fixed-model / same-cohort paired replay: `datapulse/replay.py`
- Evidence-based deterministic investigation: `datapulse/investigator.py`
- Optional local LLM on a pretrained Qwen model: `datapulse/local_llm.py`
- **Project guide and retrieval assistant**: `datapulse/guide_assistant.py`
- Optional BigQuery uploads: `cloud/bigquery_load.py`
- Optional **one-event Pub/Sub publisher**, not a subscriber: `cloud/pubsub_demo.py`
- Colab notebooks for core demo, local AI, and optional Vertex AI trial experiment.

## The main failure mode
Field `engagement_events_30d` originally represents purchases but silently begins to represent logins. Both are non-null integers, so baseline quality rules pass. A synthetic independently trusted `purchases_30d` field is used as a semantic reference. Do not claim every real company can access such a reference.

## How to demonstrate DataPulse from scratch
1. Open `notebooks/DataPulse_AI_Colab.ipynb` and run the core test, snapshot, replay and incident cells.
2. Observe basic contract pass, semantic contract failure, feature drift and paired prediction changes.
3. Generate the evidence-only incident report. The reports and replay CSV are stored under gitignored `artifacts/`.
4. Open `notebooks/DataPulse_Guide_AI_Colab.ipynb`; retrieve answers to 'How does DataPulse work?' and 'Why did schema validation pass?' using in-repo documentation.
5. Optionally load a small pretrained Qwen model in free Colab (GPU allocation not guaranteed) to express retrieved evidence in natural language.
6. Optional: verify BigQuery uploads, one-shot Pub/Sub publish or Vertex AI separately. Never claim live cloud execution before it happens.

## What does the assistant actually do?
**Guide mode:** retrieves passages from committed Markdown docs using TF-IDF cosine similarity, with file-source names in results. The optional local LLM summarizes the retrieved passages and can guide a newcomer through the project.

**Incident mode:** reads the already-verified `investigate(summary)` JSON alongside retrieved documentation, and explains possible causes, impact and human-approved investigation steps. The local LLM never generates the underlying metrics or executes remediation.

**Fallback:** works without downloading any language model: it returns quoted, source-attributed document passages. This is **retrieval only, not an LLM response**.

## Important limits
- Model is a pretrained open-weight Qwen; this project has **not trained a new foundation LLM** or fine-tuned Qwen.
- Local retrieval is TF-IDF, **not** embedding-based vector RAG or a BigQuery vector index.
- Guide mode explains checked-in docs; unsupported questions need explicit uncertainty.
- No production use, autonomous fixes, automatic SQL execution, real customer data or guaranteed LLM accuracy.
- Google Vertex AI is an ML/AI service platform, not a language model itself. Vertex AI deployment needs separate access, IAM and cost verification.
- BigQuery and Pub/Sub code being in the repo does not mean successful user-side cloud execution.

## Demo questions
- What business problem does DataPulse solve?
- How does DataPulse generate the trusted and shifted snapshots?
- Why do schema checks pass when data semantics change?
- Why replay with the same model and fixed customer IDs?
- What are PSI and KS, and what are their limits?
- Where are the incident report and prediction CSV saved?
- What does the DataPulse Investigator do?
- How do I verify BigQuery and Pub/Sub?
- Is the local Qwen assistant trained from scratch?
- Which features are prototypes versus live deployed cloud resources?

## Developer commands
```bash
cd datapulse-ai
python -m pip install -r requirements.txt
python -m pytest -q
python -m datapulse --rows 5000
```

Local model is optional. See `notebooks/DataPulse_Guide_AI_Colab.ipynb`.
