# Google Colab + GCP exact Day-1 cloud setup

## Before you start
- GCP free trial active until December **does not mean services are free**; check remaining trial credits, upgrade status and the project billing account at https://console.cloud.google.com/billing.
- Create a small billing budget alert at https://console.cloud.google.com/billing. Alerts are notifications, **not** hard spending caps.
- Use a **personal project** and **synthetic data only**. Never upload company or production data or service account keys.

## Open these browser tabs
1. https://console.cloud.google.com/projectcreate → create project `aegis-supply-chain-ai` (the real **project ID** may differ).
2. https://console.cloud.google.com/apis/library → select your project → enable Pub/Sub, BigQuery, Dataflow, Cloud Storage. Vertex AI optional later.
3. https://colab.research.google.com/ → create notebook or open `notebooks/AEGIS_Day1_Colab.ipynb` from this ZIP.
4. https://console.cloud.google.com/bigquery → for checking dataset, tables and SQL output.
5. https://console.cloud.google.com/cloudpubsub/topic/list → for checking Pub/Sub topic and subscriptions.

## Day 1, Colab execution order
1. Open the included notebook in Colab. If using the ZIP download, upload the ZIP in its first cell. **Do not share your credentials**.
2. Install Python requirements. Authenticate with `auth.authenticate_user()`.
3. Set `PROJECT_ID` to **real** GCP project ID (not project display name), e.g. `aegis-supply-chain-ai-123`.
4. Generate six synthetic CSVs. Run local risk/retrieval demo and tests.
5. Execute setup script. It creates the `aegis_warehouse` BigQuery dataset, six reference tables, raw ingestion table, two sets of SQL views, and Pub/Sub topic `aegis-sales-events`.
6. **Create a BigQuery subscription manually in the Console:** Pub/Sub → Subscriptions → Create subscription. Subscription ID: `aegis-to-bigquery`; select topic `aegis-sales-events`. Delivery type: **Write to BigQuery**. Choose project → dataset `aegis_warehouse` → table `raw_sales_events`. Schema Configuration: **Don't use a schema**; **Write metadata disabled**. Click Create.
7. **Permissions if create fails:** Pub/Sub service agent `service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com` needs `BigQuery Data Editor` on the destination dataset (or a sufficiently scoped resource). Google official docs: https://cloud.google.com/pubsub/docs/create-bigquery-subscription. Ask for help if your GCP Console shows a policy error; do not assign Owner broadly.
8. Publish `--count 20 --replay-first`. Wait a short period for export; rerun KPI query until raw rows appear (streaming is eventually visible).
9. Verify raw events > 0, validated sales = number of unique valid `event_id`, duplicate replay does not double-count, stock-risk view shows expected output.
10. Stop publishing events when done; you can delete the subscription and topic after collecting proof screenshots. Direct export does not need an always-on Dataflow worker.

## Expected sample results
- 6 product rows, 3 suppliers, 2 warehouses, 12 opening inventory positions, 12 purchase orders, 540 historical-demand rows.
- With 20 messages plus replay, about **21 raw records** and **20 unique valid events** (if all messages arrive and no other messages are present).
- Scenario replay has 0/3/7/14-day delays with non-decreasing hypothetical revenue exposure.

## Troubleshooting
- `403` during BigQuery operations: your signed-in account lacks dataset / job permissions or billing/API not enabled.
- `403` on creating BigQuery subscription: missing Pub/Sub service agent `roles/bigquery.dataEditor` at destination.
- `404` on publish: check topic and exact project ID.
- `Not found dataset`: check `US` location and the selected project.
- `ModuleNotFoundError`: ensure `%pip` cell completed and restart Colab runtime if required.
- BigQuery result 0 rows after publish: confirm export subscription existed **before** publishing; topic messages sent beforehand won't automatically be delivered to a new subscription unless retained.

## Suggested demo screenshots
Pub/Sub topic + BigQuery subscription; BigQuery raw events; v_valid_sales unique counts; v_stock_risk; scenario replay table; tests passing. Do not display private identifiers, billing balances or credentials.
