"""Create a Pub/Sub BigQuery export subscription for the AEGIS demo.

Run AFTER `scripts.setup_gcp`, with a GCP identity authorized to create
subscriptions. The Pub/Sub service agent must separately have write access to
the destination BigQuery dataset. No credentials are stored by this script.
"""
from __future__ import annotations

import argparse

from google.api_core.exceptions import AlreadyExists, GoogleAPICallError, NotFound
from google.cloud import pubsub_v1

from aegis.gcp import DATASET, TOPIC, safe_project_id

SUBSCRIPTION = "aegis-to-bigquery"
TABLE = "raw_sales_events"


def create_subscription(project_id: str) -> str:
    project_id = safe_project_id(project_id)
    subscriber = pubsub_v1.SubscriberClient()
    subscription_path = subscriber.subscription_path(project_id, SUBSCRIPTION)
    topic_path = subscriber.topic_path(project_id, TOPIC)
    table = f"{project_id}.{DATASET}.{TABLE}"

    try:
        existing = subscriber.get_subscription(request={"subscription": subscription_path})
        actual_table = existing.bigquery_config.table
        if actual_table != table:
            raise RuntimeError(
                f"Subscription already exists, but its destination is {actual_table!r}; "
                f"expected {table!r}. Inspect it in Cloud Console rather than overwriting it."
            )
        print(f"Subscription already exists: {subscription_path}")
        return subscription_path
    except NotFound:
        pass

    try:
        created = subscriber.create_subscription(
            request={
                "name": subscription_path,
                "topic": topic_path,
                "bigquery_config": {
                    "table": table,
                    "use_topic_schema": False,
                    "use_table_schema": False,
                    "write_metadata": False,
                },
            }
        )
    except AlreadyExists:
        print("Subscription was created concurrently; inspect its destination in Console.")
        return subscription_path
    except GoogleAPICallError as error:
        print("GCP rejected the subscription request:", error)
        print("Check the Cloud Pub/Sub API, destination table, and your IAM permissions.")
        print("The Pub/Sub service agent may require BigQuery Data Editor on")
        print(f"the destination dataset {project_id}.{DATASET} (not project-wide Owner).")
        print("Guide: https://cloud.google.com/pubsub/docs/create-bigquery-subscription")
        raise

    print("Created BigQuery export subscription:", created.name)
    print("Destination table:", created.bigquery_config.table)
    print("No schema selected; Write metadata disabled.")
    return created.name


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-id", required=True)
    args = parser.parse_args()
    create_subscription(args.project_id)


if __name__ == "__main__":
    main()
