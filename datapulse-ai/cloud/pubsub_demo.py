"""Optional one-shot publish of synthetic incident metadata to Pub/Sub.

This is not a managed streaming production pipeline. Keep volume small.
"""
import argparse
import json
from datetime import datetime, timezone
from google.cloud import pubsub_v1
from datapulse.replay import decision_replay


def publish(project_id: str, topic_id: str = "datapulse-incidents"):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(project_id, topic_id)
    try:
        publisher.create_topic(request={"name": topic_path})
    except Exception as exc:
        from google.api_core.exceptions import AlreadyExists
        if not isinstance(exc, AlreadyExists):
            raise
    result, _ = decision_replay(n=500)
    message = {"event_type":"ML_DATA_SEMANTIC_DRIFT", "created_at":datetime.now(timezone.utc).isoformat(),
               "source":"synthetic", "prediction_flips":result["prediction_flips"],
               "semantic_discrepancy_rate":result["semantic_after"]["discrepancy_rate"]}
    message_id = publisher.publish(topic_path, json.dumps(message).encode("utf-8")).result(timeout=30)
    print("Published incident event to", topic_path, "message_id:", message_id)
    print("This only publishes; configure a consumer or sink separately for end-to-end streaming.")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--topic",default="datapulse-incidents")
    args=parser.parse_args()
    publish(args.project_id,args.topic)
