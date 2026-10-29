"""One-shot Pub/Sub -> BigQuery incident consumer for synthetic DataPulse events.

Run setup BEFORE publishing, otherwise a newly created subscription won't
receive already-published events. Pulls at most one event and acknowledges only
after a successful BigQuery append. This demo is not an always-on service.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone


REQUIRED_FIELDS = ("event_type", "source", "prediction_flips",
                   "semantic_discrepancy_rate", "created_at")


def parse_incident(payload: bytes) -> dict:
    """Validate untrusted Pub/Sub JSON before storing it in the warehouse."""
    try:
        obj = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Incident message is not valid UTF-8 JSON") from exc
    if not isinstance(obj, dict) or any(key not in obj for key in REQUIRED_FIELDS):
        raise ValueError("Missing required incident fields")
    if obj["event_type"] != "ML_DATA_SEMANTIC_DRIFT" or obj["source"] != "synthetic":
        raise ValueError("Unexpected event type or source")
    if type(obj["prediction_flips"]) is not int or obj["prediction_flips"] < 0:
        raise ValueError("prediction_flips must be a nonnegative integer")
    rate = obj["semantic_discrepancy_rate"]
    if type(rate) not in (int, float) or not 0 <= rate <= 1:
        raise ValueError("semantic_discrepancy_rate must be between 0 and 1")
    if not isinstance(obj["created_at"], str) or not obj["created_at"]:
        raise ValueError("created_at must be a timestamp string")
    try:
        parsed_time = datetime.fromisoformat(obj["created_at"].replace("Z", "+00:00"))
        if parsed_time.tzinfo is None:
            raise ValueError()
    except ValueError as exc:
        raise ValueError("created_at must be ISO-8601 with timezone") from exc
    return {key: obj[key] for key in REQUIRED_FIELDS}


def setup_subscription(project_id: str, topic_id: str = "datapulse-incidents",
                       subscription_id: str = "datapulse-incidents-consumer") -> str:
    from google.api_core.exceptions import AlreadyExists
    from google.cloud import pubsub_v1

    publisher = pubsub_v1.PublisherClient()
    topic = publisher.topic_path(project_id, topic_id)
    try:
        publisher.create_topic(request={"name": topic})
        print("Created topic:", topic)
    except AlreadyExists:
        print("Topic already exists:", topic)
    subscriber = pubsub_v1.SubscriberClient()
    name = subscriber.subscription_path(project_id, subscription_id)
    try:
        subscriber.create_subscription(request={"name": name, "topic": topic})
        print("Created subscription:", name)
    except AlreadyExists:
        print("Subscription already exists:", name)
    return name


def consume_once(project_id: str, dataset_id: str = "datapulse_ai",
                 topic_id: str = "datapulse-incidents",
                 subscription_id: str = "datapulse-incidents-consumer") -> None:
    from google.api_core.exceptions import DeadlineExceeded
    from google.cloud import bigquery, pubsub_v1

    name = setup_subscription(project_id, topic_id, subscription_id)
    subscriber = pubsub_v1.SubscriberClient()
    try:
        response = subscriber.pull(
            request={"subscription": name, "max_messages": 1},
            timeout=20,
        )
    except DeadlineExceeded:
        print("No message arrived within pull deadline; publish an event and retry.")
        return
    if not response.received_messages:
        print("No message available. Publish after creating the subscription.")
        return

    received = response.received_messages[0]
    try:
        incident = parse_incident(received.message.data)
        row = {
            **incident,
            "pubsub_message_id": received.message.message_id,
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        client = bigquery.Client(project=project_id)
        dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
        dataset.location = "US"
        client.create_dataset(dataset, exists_ok=True)
        table = f"{project_id}.{dataset_id}.incident_events"
        schema = [
            bigquery.SchemaField("event_type", "STRING"),
            bigquery.SchemaField("source", "STRING"),
            bigquery.SchemaField("prediction_flips", "INTEGER"),
            bigquery.SchemaField("semantic_discrepancy_rate", "FLOAT"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
            bigquery.SchemaField("pubsub_message_id", "STRING"),
            bigquery.SchemaField("ingested_at", "TIMESTAMP"),
        ]
        job = client.load_table_from_json(
            [row], table, job_config=bigquery.LoadJobConfig(
                schema=schema, write_disposition="WRITE_APPEND"
            ), location="US"
        )
        job.result()
    except Exception:
        # Deliberately do not acknowledge malformed or failed loads. Operators
        # must investigate and may need to seek/ack a poison message.
        print("Message not acknowledged. Review payload, schema, or BQ permission.")
        raise

    subscriber.acknowledge(request={
        "subscription": name, "ack_ids": [received.ack_id]
    })
    print("Loaded incident to:", table)
    print("Acknowledged Pub/Sub message:", received.message.message_id)
    print("Note: demo is at-least-once; retries can create duplicate BQ rows.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--topic", default="datapulse-incidents")
    parser.add_argument("--subscription", default="datapulse-incidents-consumer")
    parser.add_argument("--dataset", default="datapulse_ai")
    parser.add_argument("--setup-only", action="store_true")
    args = parser.parse_args()
    if args.setup_only:
        setup_subscription(args.project_id, args.topic, args.subscription)
    else:
        consume_once(args.project_id, args.dataset, args.topic, args.subscription)


if __name__ == "__main__":
    main()
