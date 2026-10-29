"""Optional GCP experiment: persist synthetic baseline/shift and replay report.

Usage: python -m cloud.bigquery_load --project-id YOUR_PROJECT_ID
Requires GCP user ADC, BigQuery enabled, and dataset creation permissions.
No service account keys checked into GitHub.
"""
import argparse
import json
from google.cloud import bigquery
from datapulse.generator import make_customer_data, introduce_semantic_shift
from datapulse.replay import decision_replay


def run(project_id: str, dataset_id: str = "datapulse_ai", location: str = "US"):
    client = bigquery.Client(project=project_id)
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)
    original = make_customer_data()
    shifted = introduce_semantic_shift(original)
    summary, comparisons = decision_replay()
    for name, frame in [("baseline_customers", original), ("shifted_customers", shifted), ("paired_prediction_replay", comparisons)]:
        table = f"{project_id}.{dataset_id}.{name}"
        client.load_table_from_dataframe(frame, table, job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE"), location=location).result()
        print("Loaded", table, len(frame), "rows")
    print("Evaluation:", json.dumps({"flips": summary["prediction_flips"], "before_auc": summary["baseline_model"]["roc_auc"], "after_auc": summary["changed_data_same_model"]["roc_auc"]}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--dataset", default="datapulse_ai")
    args = parser.parse_args()
    run(args.project_id, args.dataset)
