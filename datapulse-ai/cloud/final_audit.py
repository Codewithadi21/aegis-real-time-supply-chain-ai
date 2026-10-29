"""Read-only final DataPulse validation against local artifacts and Google Cloud.

Usage: python -m cloud.final_audit --project-id YOUR_PROJECT_ID

Does NOT create, change, publish, consume, or acknowledge cloud resources.
Runs local pytest and validates the existing JSON/CSV outputs and cloud records.
Queries may incur a small BigQuery query cost covered by eligible trial credits.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def local_checks(root: Path) -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=root, text=True, capture_output=True,
    )
    print("\nPYTEST RESULT:\n", result.stdout[-3500:], result.stderr[-1000:])
    artifacts = root / "artifacts"
    summary_path = artifacts / "replay_summary.json"
    report_path = artifacts / "incident_report.json"
    csv_path = artifacts / "prediction_replay.csv"
    if not (summary_path.exists() and report_path.exists() and csv_path.exists()):
        demo = subprocess.run(
            [sys.executable, "-m", "datapulse", "--rows", "5000"],
            cwd=root, text=True, capture_output=True,
        )
        print("Local replay:", demo.stdout[-1000:])
        if demo.returncode:
            print("Local replay error:", demo.stderr[-1000:])
    checks = {"pytest": result.returncode == 0,
              "replay_summary_exists": summary_path.exists(),
              "incident_report_exists": report_path.exists(),
              "paired_prediction_csv_exists": csv_path.exists()}
    if summary_path.exists() and report_path.exists():
        try:
            summary = json.loads(summary_path.read_text())
            report = json.loads(report_path.read_text())
            checks["schema_pass_semantic_fail"] = bool(
                summary["schema_checks_after"]["passed"]
                and not summary["semantic_after"]["passed"]
            )
            checks["prediction_flips_positive"] = summary["prediction_flips"] > 0
            checks["incident_matches_replay"] = (
                report["evidence"]["prediction_flips"] == summary["prediction_flips"]
                and report["requires_human_approval"] is True
            )
        except (ValueError, KeyError, TypeError) as exc:
            print("Artifact validation error:", exc)
            checks["artifact_validation"] = False
    return checks


def cloud_checks(project: str) -> dict:
    from google.cloud import bigquery, pubsub_v1

    checks = {}
    bq = bigquery.Client(project=project)
    required = ("baseline_customers", "shifted_customers",
                "paired_prediction_replay", "incident_events")
    for name in required:
        ref = f"{project}.datapulse_ai.{name}"
        try:
            bq.get_table(ref)
            rows = list(bq.query(
                f"SELECT COUNT(*) AS n FROM `{ref}`", location="US"
            ).result())
            checks[f"bigquery_{name}_populated"] = bool(rows and rows[0].n > 0)
            print("BigQuery table:", name, "rows:", rows[0].n)
        except Exception as exc:
            checks[f"bigquery_{name}_populated"] = False
            print("BigQuery check failed:", name, str(exc)[:350])

    try:
        rows = list(bq.query(
            "SELECT COUNTIF(predicted_churn_before != predicted_churn_after) AS flips "
            f"FROM `{project}.datapulse_ai.paired_prediction_replay`",
            location="US",
        ).result())
        checks["cloud_prediction_flips_positive"] = bool(rows and rows[0].flips > 0)
        print("Warehouse prediction flips:", rows[0].flips)
    except Exception as exc:
        checks["cloud_prediction_flips_positive"] = False
        print("Warehouse replay check failed:", str(exc)[:350])

    try:
        rows = list(bq.query(
            "SELECT COUNT(*) AS n FROM "
            f"`{project}.datapulse_ai.incident_events` "
            "WHERE event_type='ML_DATA_SEMANTIC_DRIFT' "
            "AND source='synthetic' AND pubsub_message_id IS NOT NULL",
            location="US",
        ).result())
        checks["cloud_incident_event_valid"] = bool(rows and rows[0].n > 0)
        print("Recorded synthetic Pub/Sub incidents:", rows[0].n)
    except Exception as exc:
        checks["cloud_incident_event_valid"] = False
        print("Incident history check failed:", str(exc)[:350])

    publisher = pubsub_v1.PublisherClient()
    subscriber = pubsub_v1.SubscriberClient()
    try:
        publisher.get_topic(request={"topic": publisher.topic_path(
            project, "datapulse-incidents"
        )})
        checks["pubsub_topic_exists"] = True
    except Exception as exc:
        checks["pubsub_topic_exists"] = False
        print("Topic check failed:", str(exc)[:350])
    try:
        sub = subscriber.get_subscription(request={
            "subscription": subscriber.subscription_path(
                project, "datapulse-incidents-consumer"
            )
        })
        checks["pubsub_subscription_connected"] = sub.topic == publisher.topic_path(
            project, "datapulse-incidents"
        )
    except Exception as exc:
        checks["pubsub_subscription_connected"] = False
        print("Subscription check failed:", str(exc)[:350])
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--output", default="artifacts/final_audit.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    checks = local_checks(root)
    checks.update(cloud_checks(args.project_id))
    final = {"project_id": args.project_id, "checks": checks,
             "passed": all(checks.values()),
             "passed_count": sum(checks.values()),
             "total_count": len(checks)}
    path = root / args.output
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(final, indent=2))
    print("\nFINAL AUDIT:", final["passed_count"], "/", final["total_count"])
    for name, val in checks.items():
        print("PASS" if val else "PENDING", name)
    print("Report saved to:", path)
    if not final["passed"]:
        sys.exit(1)
    print("DATAPULSE ONE-SHOT PORTFOLIO DEMO: VERIFIED")


if __name__ == "__main__":
    main()
