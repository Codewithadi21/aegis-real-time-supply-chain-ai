# Publish AEGIS on GitHub — safely

1. Confirm local `python -m pytest -q` passes and cloud output is real before claiming anything has been deployed.
2. Go to https://github.com/new and create a new **public** repository named `aegis-real-time-supply-chain-gcp`. Choose **not** to initialize with a README when uploading using Git from an existing folder.
3. Extract the ZIP to a clean local folder, open a terminal in `AEGIS_GCP_RealTime_Portfolio`, and use:

```bash
git init
git add .
git commit -m "Initial AEGIS supply chain streaming portfolio"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/aegis-real-time-supply-chain-gcp.git
git push -u origin main
```

Alternatively, create a GitHub repository on the website and use **Add file → Upload files**. Upload files and folders from *inside* the project folder, not the ZIP file alone. GitHub website uploads may have per-file and folder handling limitations; `git push` is usually easier for a multi-directory project.

4. Add screenshots to a folder such as `docs/evidence/` **after actually running GCP**; do not upload billing numbers, credentials or personal identifiers.
5. Update the README to record *which components you actually deployed*, number of events verified, and measured latency and model MAE if tested. This evidence is much more valuable to interviewers than listing every technology as completed.
6. Never upload `.env`, credential JSON, access tokens, private account exports, or employer code. `.gitignore` excludes common secret names; scan your commit before pushing.

## Example project resume line — only after cloud execution

> Developed a GCP-based consumer-electronics streaming analytics prototype using Python, Pub/Sub and BigQuery, with SQL-driven data-quality checks, event-ID deduplication, dimensional joins and inventory stockout-risk views; simulated supplier delays to estimate potential revenue exposure.

Add `Dataflow`, `BigQuery ML`, `Vertex AI` or `RAG` as **implemented** only when you have run and demonstrated each corresponding component.
